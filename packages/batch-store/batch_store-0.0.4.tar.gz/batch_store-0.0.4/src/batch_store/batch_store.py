import asyncio
import json
import logging
import shutil
import tempfile
import time
import traceback
from abc import ABC
from pathlib import Path
from typing import Any, Dict

import httpx
import pandas as pd
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from util_common.io_util import b64str2bytes, bytes2b64str, json2bytes
from util_common.list_util import in_batches
from util_common.logger import setup_logger
from util_common.path import (
    duplicate,
    ensure_folder,
    remove_file,
    remove_folder,
    sort_paths,
    split_basename,
)
from util_common.pydantic_util import show_settings_as_env
from util_common.singleton import singleton


class BatchStoreSettings(BaseSettings):
    """Workflow settings class that combines all settings."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="allow",
    )

    data_root: Path = Field(
        default=Path("/home/sheldon/repos/docparser_trainer_datasets/data")
    )  # DATA_ROOT 环境变量
    decompress_base_url: str = "http://192.168.8.251:28001"
    unify_base_url: str = "http://192.168.8.251:28002"


batch_store_settings = BatchStoreSettings()
show_settings_as_env(batch_store_settings)
# Configure logging
setup_logger()
logger = logging.getLogger(__file__)


def log_file_size(file_type: str, file: bytes):
    size_mb = len(file) / 1024
    logger.info(f'Writing {file_type}, file size: {size_mb:.2f} KB')


class TagRecord(BaseModel):
    batch_name: str
    sample_name: str
    page_name: str
    tag: str


class Page(BaseModel):
    name: str
    page_dir: Path


class Sample(BaseModel):
    name: str
    sample_dir: Path
    pages: list[Page]


async def _save_unified_file(
    save_page_dir: Path,
    unified_page: Dict[str, Any],
):
    """Helper method to save unified file and its associated data."""

    ensure_folder(save_page_dir)
    logger.info(f'Writing {save_page_dir.name} ===')

    if unified_page.get('text'):
        save_page_dir.joinpath('pure.txt').write_text(unified_page['text'])
    else:
        save_page_dir.joinpath('pure.txt').write_text('')
    if unified_page.get('html'):
        save_page_dir.joinpath('raw.html').write_text(unified_page['html'])
    else:
        save_page_dir.joinpath('raw.html').write_text(unified_page['text'])

    for file_type, file_key, file_name, ext in [
        ('Excel', 'xlsx', 'raw', 'xlsx'),
        ('PDF', 'pdf', 'raw', 'pdf'),
        ('norm_image', 'norm_image', 'norm', 'png'),
        ('char_block', 'char_block', 'char_block', 'json'),
        ('text_block', 'text_block', 'text_block', 'json'),
        ('table_block', 'table_block', 'table_block', 'json'),
    ]:
        if unified_page.get(file_key):
            if file_key in ['char_block', 'text_block', 'table_block']:
                content = json2bytes(unified_page[file_key])
            else:
                content = b64str2bytes(unified_page[file_key]['file_b64str'])
            log_file_size(file_type, content)
            save_page_dir.joinpath(f'{file_name}.{ext}').write_bytes(content)


async def request_unify_pages(file_name: str, content: bytes, target_results: list[str]):
    res = await make_request(
        UnifyClient().get_client(),
        "/unify-pages",
        {
            "file_name": file_name,
            "file_b64str": bytes2b64str(content),
            "task_settings": {
                "target_results": target_results,
            },
            "step_settings": [
                {
                    "step_name": "excel",
                    "excel_rows_limit": 500,
                    "excel_rows_limit_exceed_schema": "truncate",
                    "delete_invalid_rows": False,
                },
            ],
        },
    )
    success_pages = res.json()['success_pages']
    failed_files = res.json()['failures']
    return success_pages, failed_files


async def unify_pages_and_save(
    file_path: Path,
    sample_dir: Path,
    failed_dir: Path,
    target_results: list[str],
) -> None:
    try:
        success_pages, failed_files = await request_unify_pages(
            file_path.name, file_path.read_bytes(), target_results
        )

        for unified_page in success_pages:
            stem, ext = split_basename(file_path.name)
            pid = unified_page["page_id"]
            sheet_name = unified_page["sheet_name"]
            if sheet_name:
                save_page_dir = sample_dir / f'{stem}-p{pid}_{sheet_name.replace("-", "_")}.{ext}'
            else:
                save_page_dir = sample_dir / f'{stem}-p{pid}.{ext}'
            await _save_unified_file(save_page_dir, unified_page)

        failed_sample_path = failed_dir / file_path.parent.name
        if len(failed_files) == 0:
            if failed_sample_path.is_dir():
                remove_folder(failed_sample_path)
            elif failed_sample_path.is_file():
                remove_file(failed_sample_path)

        for failure in failed_files:
            logger.error(
                'File normalization failed: '
                f'{failure["file_name"]}.{failure["page_id"]}: {failure["error_msg"]}'
            )
            duplicate(file_path.parent, failed_sample_path)

    except Exception:
        logger.error(f"Error in unify_pages: {traceback.format_exc()}")
        duplicate(file_path.parent, failed_sample_path)


async def decompress_sample_and_save(
    sample_path: Path,
    decompressed_dir: Path,
    failed_dir: Path | None = None,
):
    save_dir = decompressed_dir / sample_path.name
    if sample_path.is_dir():
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = Path(tmpdir) / f"{sample_path.name}.zip"
                shutil.make_archive(str(zip_path.with_suffix('')), 'zip', root_dir=sample_path)
                content = zip_path.read_bytes()
        except Exception:
            logger.error(f"Error zipping sample directory {sample_path}: {traceback.format_exc()}")
            if failed_dir:
                duplicate(sample_path, failed_dir / sample_path.name)
            return []
    else:
        content = sample_path.read_bytes()

    try:
        payload = {
            "file_name": sample_path.name,
            "file_b64str": bytes2b64str(content),
        }
        res = await make_request(DecompressClient().get_client(), "/decompress", payload)
        response_data = res.json()
        ensure_folder(save_dir)
        for file in response_data['success_files']:
            file_name = file['file_name']
            (save_dir / file_name).write_bytes(b64str2bytes(file['file_b64str']))
        for file in response_data['failed_files']:
            logger.error('Decompression failed: ' f'{file["file_name"]}. {file["error_msg"]}')
            if failed_dir:
                duplicate(sample_path, failed_dir / sample_path.name)
    except Exception:
        logger.error(f"Error in decompress_sample: {traceback.format_exc()}")
        if failed_dir:
            duplicate(sample_path, failed_dir / sample_path.name)
        return []
    return sort_paths(save_dir.iterdir())


class HTTPXClient(ABC):
    def __init__(self, base_url: str, timeout: int = 600, max_retries: int = 3):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self._init_client()
        self.client: httpx.AsyncClient | None = None

    def _init_client(self):
        """Initialize the HTTP client."""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )

    async def close(self):
        """Close the HTTP client."""
        if self.client is not None:
            await self.client.aclose()
            self.client = None

    def __del__(self):
        """Ensure client is closed when object is garbage collected."""
        if self.client is not None:
            try:
                # Check if there's already a running event loop
                try:
                    loop = asyncio.get_running_loop()
                    # If there's a running loop, we can't use asyncio.run()
                    # Create a task to close the client
                    if not loop.is_closed():
                        loop.create_task(self.client.aclose())
                except RuntimeError:
                    # No running event loop, safe to use asyncio.run()
                    asyncio.run(self.client.aclose())
            except Exception:
                # Ignore any exceptions during cleanup to prevent the warning
                pass

    def get_client(self):
        """Get the client, reinitializing it if necessary."""
        if self.client is None:
            self._init_client()
        return self.client


@singleton
class DecompressClient(HTTPXClient):
    def __init__(self):
        super().__init__(batch_store_settings.decompress_base_url)


@singleton
class UnifyClient(HTTPXClient):
    def __init__(self):
        super().__init__(batch_store_settings.unify_base_url)


async def close_all_clients():
    """Close all singleton HTTP clients."""
    await DecompressClient().close()
    await UnifyClient().close()


async def make_request(
    client: httpx.AsyncClient | None,
    url: str,
    payload: Dict[str, Any],
    max_retries: int = 3,
) -> httpx.Response:
    """Make an HTTP request with retries and proper error handling."""
    if client is None:
        raise ValueError("Client cannot be None")

    for attempt in range(max_retries):
        try:
            response = await client.post(url=url, json=payload)
            response.raise_for_status()
            logger.info(f'Request {url} success')
            return response
        except httpx.HTTPStatusError as e:
            logger.warning(
                f"HTTP error occurred: {e.response.status_code} - {e.response.text}, retrying..."
            )
            if attempt == max_retries - 1:
                raise e
        except httpx.RequestError as e:
            logger.warning(f"Request error occurred: {str(e)}, retrying...")
            if attempt == max_retries - 1:
                raise e
        except Exception as e:
            logger.warning(f"Unexpected error occurred: {traceback.format_exc()}, retrying...")
            if attempt == max_retries - 1:
                raise e
        await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
    raise Exception('Failed to make request')


class BatchStore:
    """
    功能:
    对一个批次内的样本进行统一的数据预处理, 以及存储操作, 并提供一些辅助功能

    目录结构:
    不指定 batch_dir 时, 数据根目录结构:
    |-workflow_settings.data_root
    |   |-batches
    |   |   |-batch-1
    |   |   |   |-raw:
    |   |   |   |   |-sample_1.zip
    |   |   |   |   |-sample_2
    |   |   |   |   |-sample_3.pdf
    |   |   |   |   |-sample_4.xls
    |   |   |   |   |-...

    指定 batch_dir 时, 数据根目录结构:
    |-batch_dir
    |   |-raw:
    |   |   |-sample_1.zip
    |   |   |-sample_2
    |   |   |-sample_3.pdf
    |   |   |-sample_4.xls
    |   |   |-...

    依赖:
    解压缩服务
    文件归一化服务

    使用方法:
    配置环境变量 DATA_ROOT 为数据根目录
    配置环境变量 DECOMPRESS_BASE_URL 为解压缩服务地址
    配置环境变量 UNIFY_BASE_URL 为文件归一化服务地址

    使用示例:
    batch_store = BatchStore('batch-1')
    asyncio.run(batch_store.preprocess_batch())
    """

    def __init__(self, batch_name: str | None = None, batch_dir: Path | None = None) -> None:
        if batch_name is None and batch_dir is None:
            raise ValueError('batch_name or batch_dir must be provided')
        if batch_name is not None and batch_dir is not None:
            if batch_dir.name != batch_name:
                raise ValueError('batch_name and batch_dir must have the same name')
        self.batch_name = batch_name or batch_dir.name  # type: ignore
        self.batch_dir = batch_dir or batch_store_settings.data_root / 'batches' / self.batch_name
        self.raw_dir = self.batch_dir / 'raw'
        self.decompressed_dir = self.batch_dir / 'decompressed'
        self.unified_dir = self.batch_dir / 'unified'
        self.failed_dir = self.batch_dir / 'failed'
        self.results_dir = self.batch_dir / 'result'  # 端到端结果存放
        self.tag_dir = self.batch_dir / 'tag'  # 端到端标签存放
        self.compare_dir = self.batch_dir / 'compare'  # 端到端结果对比
        self.task_results_dir = self.batch_dir / 'task_results'  # 单任务结果存放
        self.task_tag_dir = self.batch_dir / 'task_tags'  # 单任务标签存放
        self.task_compare_dir = self.batch_dir / 'task_compares'  # 单任务结果对比
        self.classified_dir = (
            self.batch_dir / 'classified'
        )  # 按照分类标签分拣到对应文件夹下用来查看
        self.sessions_dir = self.batch_dir / 'sessions'  # TODO: 保存一次运行会话的上下文信息
        self.split_dict_path = self.batch_dir / 'split_dict.json'

    async def _preprocess_sample(
        self,
        sample_path: Path,
        target_results: list[str] = [],
        fix_broken: bool = False,
        check_empty: bool = False,
    ) -> None:
        save_dir = self.unified_dir / sample_path.name
        if fix_broken and save_dir.is_dir():
            return
        try:
            if check_empty is True:
                for page_dir in sort_paths(save_dir.iterdir()):
                    if page_dir.joinpath('pure.txt').read_text().strip():
                        continue
                    if not page_dir.joinpath('raw.pdf').exists():
                        continue
                    logger.info(f'Checking empty page: {page_dir.name} ...')
                    success_pages, failed_files = await request_unify_pages(
                        page_dir.joinpath('raw.pdf').name,
                        page_dir.joinpath('raw.pdf').read_bytes(),
                        target_results,
                    )
                    if len(success_pages) == 1:
                        await _save_unified_file(page_dir, success_pages[0])
                        if page_dir.joinpath('pure.txt').read_text().strip():
                            logger.info(f'Extract page success: {page_dir.name}')
                        else:
                            logger.info(f'Empty page checked! {page_dir.name}')
                    else:
                        logger.error(f'Check empty page failed! {page_dir.name}')
            else:
                file_paths = await decompress_sample_and_save(
                    sample_path, self.decompressed_dir, self.failed_dir
                )
                await asyncio.gather(
                    *[
                        unify_pages_and_save(
                            file_path,
                            save_dir,
                            self.failed_dir,
                            target_results,
                        )
                        for file_path in file_paths
                    ]
                )
        except Exception:
            logger.error(f"Error processing sample {sample_path}: {traceback.format_exc()}")
            duplicate(sample_path, self.failed_dir / sample_path.name)

    async def preprocess_batch(
        self,
        target_results: list[str] = [],
        concurrency: int = 1,
        failed_only: bool = False,  # 只需要运行 failed 下的样本
        fix_broken: bool = False,  # 跳过已经处理过的样本
        check_empty: bool = False,  # 检查样本 pure.txt 是否为空, 如果为空再试一次
    ) -> None:
        """Process all samples in the batch with proper error handling."""
        # Ensure all required directories exist
        for dir_path in [
            self.raw_dir,
            self.decompressed_dir,
            self.unified_dir,
            self.failed_dir,
        ]:
            ensure_folder(dir_path)

        try:
            if failed_only:
                sample_paths = sort_paths(self.failed_dir.iterdir())
            else:
                sample_paths = sort_paths(self.raw_dir.iterdir())

            for i, batch in enumerate(in_batches(sample_paths, concurrency)):
                start_time = time.time()
                await asyncio.gather(
                    *[
                        self._preprocess_sample(
                            sample_path, target_results, fix_broken, check_empty
                        )
                        for sample_path in batch
                    ]
                )
                end_time = time.time()
                logger.info(
                    f'### Preprocess batch {i + 1} finished in {end_time - start_time:.2f} seconds'
                )
        except Exception as e:
            logger.error(f"Error in preprocess_batch: {traceback.format_exc()}")
            raise e
        finally:
            await close_all_clients()

    def load_unified_samples(self) -> list[Sample]:
        samples = []
        for sample_dir in sort_paths(self.unified_dir.iterdir()):
            pages = []
            for page_dir in sort_paths(sample_dir.iterdir()):
                pages.append(Page(name=page_dir.name, page_dir=page_dir))
            samples.append(Sample(name=sample_dir.name, sample_dir=sample_dir, pages=pages))
        return samples

    def save_sample(self, content: bytes, file_name: str):
        save_path = self.raw_dir / file_name
        ensure_folder(save_path.parent)
        save_path.write_bytes(content)

    def save_sample_task_result(
        self,
        sample_name: str,
        result: list[dict] | dict,
        task_id: str,
        session_id: int,
    ):
        save_dir = self.results_dir / task_id / f'{task_id}-{session_id}'
        save_dir.mkdir(parents=True, exist_ok=True)
        save_path = save_dir / f'{sample_name}.json'
        save_path.write_bytes(json2bytes(result))

    def get_sample_task_result(self, sample_name, task_id: str, session_id: int = 0):
        result_path = self.results_dir / task_id / f'{task_id}-{session_id}' / f'{sample_name}.json'
        return json.loads(result_path.read_text())

    def get_task_compare_dir(self, task_id: str, session_id: int):
        compare_dir = self.task_compare_dir / task_id / f'{task_id}-{session_id}'
        compare_dir.mkdir(parents=True, exist_ok=True)
        return compare_dir

    def backup_tag(self, tag_name: str):
        records = []
        for sample_dir in sort_paths(self.unified_dir.iterdir()):
            for page_dir in sort_paths(sample_dir.iterdir()):
                tag_path = page_dir / f"tag-{tag_name}.json"
                if tag_path.exists():
                    record = TagRecord(
                        batch_name=self.batch_name,
                        sample_name=sample_dir.name,
                        page_name=page_dir.name,
                        tag=tag_path.read_text(),
                    )
                    records.append(record.model_dump())

        df = pd.DataFrame.from_records(records)
        logger.info(f'Saving {tag_name}.csv...')
        logger.info(f'total {df.shape[0]} records')
        logger.info(f'first 5 records: {df.head()}')
        logger.info(f'last 5 records: {df.tail()}')
        ensure_folder(self.task_tag_dir)
        df.to_csv(f'{self.task_tag_dir}/{tag_name}.csv', index=False)

    def restore_tag(self, tag_name: str):
        df = pd.read_csv(f'{self.task_tag_dir}/{tag_name}.csv')
        for _, row in df.iterrows():
            sample_name = row['sample_name']
            page_name = row['page_name']
            tag = row['tag']
            save_path = self.unified_dir / sample_name / page_name / f'tag-{tag_name}.json'
            try:
                save_path.write_text(tag)  # type: ignore
            except Exception:
                logger.error(f'{sample_name} {page_name} {tag_name} restore failed, skip')


if __name__ == '__main__':
    batch_store = BatchStore('batch-temp')
    asyncio.run(
        batch_store.preprocess_batch(
            target_results=[
                "text",
                "xlsx",
                "html",
                "pdf",
            ],
            concurrency=1,
            failed_only=False,
            fix_broken=False,
            check_empty=False,
        )
    )
