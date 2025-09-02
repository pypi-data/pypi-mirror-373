import logging
import os
from multiprocessing import Pool
from typing import List

from mds.core import s3_singleton
from mds.core import utils
from mds.core.s3file import S3File

# conf
logger = logging.getLogger("mds")
THREADS_TIMEOUT = 10 * 60


@utils.elapsed_time
def get_file_list(
    s3_bucket: str,
    product: str,
    dataset_id: str,
    dataset_version: str,
    file_filter: str,
    subdir: str,
    recursive: bool,
):
    my_s3 = s3_singleton.S3()
    return my_s3.file_list(
        s3_bucket, product, dataset_id, dataset_version, file_filter, subdir, recursive
    )


@utils.elapsed_time
def download_files(
    s3_bucket: str,
    product: str,
    dataset_id: str,
    dataset_version: str,
    file_filter: str,
    output_directory: str,
    overwrite: bool = False,
    keep_timestamps: bool = False,
    subdir: str = None,
    sync_etag: bool = False,
    sync_time: bool = False,
    n_threads=None,
    recursive: bool = False,
):
    files_list = get_file_list(
        s3_bucket, product, dataset_id, dataset_version, file_filter, subdir, recursive
    )

    if len(files_list) == 0:
        logger.error(
            f"No match found for {file_filter} in {product}/{dataset_id}_{dataset_version}"
        )
        raise FileNotFoundError(
            f"No match found for {file_filter} in {product}/{dataset_id}_{dataset_version}"
        )

    if not n_threads:
        _download(
            files_list,
            keep_timestamps,
            output_directory,
            overwrite,
            sync_etag,
            sync_time,
        )
    else:
        # if user select more threads than the files to download
        if n_threads > len(files_list):
            logger.warning(f"Resize number of threads to {len(files_list)}")

        files_list_split = utils.split_list_into_parts(files_list, n_threads)
        if n_threads != len(files_list_split):
            raise ValueError(
                f"Mismatch between number of threads ({n_threads}) "
                f"and threads parameters ({len(files_list_split)})"
            )

        # build input args for each threads
        threads_args = [
            [
                files_list_split[i],
                keep_timestamps,
                output_directory,
                overwrite,
                sync_etag,
                sync_time,
            ]
            for i in range(n_threads)
        ]

        with Pool(processes=10) as pool:
            # start threads
            results: List = [
                pool.apply_async(_download, thread_args) for thread_args in threads_args
            ]
            try:
                for r in results:
                    r.get(timeout=THREADS_TIMEOUT)
            except TimeoutError:
                logger.critical("Expired timeout")
                raise
            except Exception as e:
                logger.critical(f"Pool error: '{e}'")
                raise


def _download(
    files_list, keep_timestamps, output_directory, overwrite, sync_etag, sync_time
):
    """Download files from S3 to local filesystem"""
    try:
        my_s3 = s3_singleton.S3()
        for s3_file in files_list:
            filename = os.path.basename(s3_file.file)
            dest_file = str(os.path.join(output_directory, filename))

            # check if file must me download
            if not file_can_be_downloaded(
                s3_file, dest_file, overwrite, sync_time, sync_etag
            ):
                logger.warning(f"Skipping {s3_file} - local: {dest_file}")
                continue

            os.makedirs(os.path.dirname(dest_file), exist_ok=True)

            logger.info(f"Downloading: {s3_file.file} as {dest_file}")
            my_s3.download(s3_file.bucket, s3_file.file, dest_file)

            if keep_timestamps:
                logger.info(
                    f"Set original last modified: {s3_file.last_modified} to {dest_file}"
                )
                last_modified_timestamp = s3_file.last_modified.timestamp()
                os.utime(dest_file, (last_modified_timestamp, last_modified_timestamp))

    except BaseException as e:
        logger.critical(f"Error: {e}")
        return


def file_can_be_downloaded(
    s3_file: S3File, dest_file: str, overwrite: bool, sync_time: bool, sync_etag: bool
) -> bool:
    """Check if the destination file can be downloaded/overwritten"""
    if not os.path.exists(dest_file) or overwrite:
        return True

    if sync_time and not utils.timestamp_match(dest_file, s3_file.last_modified):
        logger.info(f"{dest_file} is outdated")
        return True

    if sync_etag and not utils.etag_match(dest_file, s3_file.etag):
        logger.info(f"{dest_file} is outdated")
        return True

    return False
