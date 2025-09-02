import contextlib
import fcntl
import fnmatch
import glob
import json
import logging
import os
import shutil
import tempfile
from collections import namedtuple
from typing import List

import boto3
from botocore import UNSIGNED
from botocore.config import Config

from mds.core import utils, copernicus
from mds.core.utils import etag_match

logger = logging.getLogger("mds")

# conf
DOWNLOAD_MODES = ["subset", "get"]
S3_ENDPOINT = "https://s3.waw3-1.cloudferro.com"
S3_FILE = namedtuple("S3_FILE", ["name", "etag", "last_modified"])
SYNC_FILE = ".sync"
DB_FILE = ".etag.json"


def extract_s3_info_from_path(s3_file: str):
    s3_file = s3_file.removeprefix("s3://")
    s3_bucket = s3_file.split("/")[0]
    s3_path = s3_file.removeprefix(f"{s3_bucket}/")
    return s3_bucket, s3_path


@utils.elapsed_time
def mds_etag(
    s3_file, product, dataset_id, version, subdir, mds_filter
) -> List[S3_FILE]:
    s3_endpoint = S3_ENDPOINT
    s3 = boto3.client(
        "s3", endpoint_url=s3_endpoint, config=Config(signature_version=UNSIGNED)
    )
    paginator = s3.get_paginator("list_objects_v2")

    if s3_file:
        s3_bucket, s3_path = extract_s3_info_from_path(s3_file)
    else:
        s3_bucket, s3_path = get_s3_info(
            s3_endpoint, product, dataset_id, version, subdir
        )

    logger.debug(f"Listing files in {s3_bucket}/{s3_path}")

    files_found = []
    for s3_result in paginator.paginate(Bucket=s3_bucket, Prefix=s3_path):
        if "Contents" not in s3_result:
            raise ValueError(f"No result found for {s3_bucket}/{s3_path}")

        contents = s3_result["Contents"]
        for content in contents:
            etag = content["ETag"].replace('"', "")
            s3_file = content["Key"]
            last_modified = content["LastModified"]
            if not mds_filter or fnmatch.fnmatch(s3_file, mds_filter):
                files_found.append(S3_FILE(s3_file, etag, last_modified))

    return files_found


def get_s3_info(s3_endpoint, product, dataset, version, subdir):
    """
    Query copernicium stat web site to retrieve info about s3 bucket and s3 path
    """
    href_native = copernicus.get_s3_native(product, dataset, version)
    native_complete_no_endpoint = href_native.replace(f"{s3_endpoint}/", "")
    s3_bucket = native_complete_no_endpoint.split("/")[0]
    s3_path = native_complete_no_endpoint.removeprefix(f"{s3_bucket}/")
    s3_path = f"{s3_path}/{subdir}"
    return s3_bucket, s3_path


@utils.elapsed_time
def mds_list(dataset_id, mds_filter: str, quiet=True, dataset_version=None) -> List:
    # mds write as default this file - name cannot be chosen via python
    mds_output_filename = "files_to_download.txt"
    tempdir = tempfile.mkdtemp()
    output_file = f"{tempdir}/{mds_output_filename}"

    # mds_output_filename is ignored
    mds_get_list_attrs = {
        "dataset_id": dataset_id,
        "filter": mds_filter,
        "output_directory": tempdir,
        "create_file_list": mds_output_filename,
        "disable_progress_bar": True,
        "dataset_version": dataset_version,
    }

    try:
        if quiet:
            # shutdown copernicus logger
            logging.getLogger("copernicus_marine_root_logger").setLevel("ERROR")
            # logging.getLogger("mds").setLevel("ERROR")
        copernicus.get(**mds_get_list_attrs)
    except SystemExit:
        pass

    if not os.path.exists(output_file):
        raise ValueError("An error occurred")

    with open(output_file, "r") as f:
        data = f.readlines()

    shutil.rmtree(tempdir, ignore_errors=True)

    return [f.strip() for f in data]


@utils.elapsed_time
def mds_download(
    download_mode: str,
    dry_run: bool = False,
    overwrite: bool = False,
    **kwargs,
):
    """
    Wrapper around copernicusmarine too to add missing features:
        - don't download a file if already exists locally
        - download only missing files
        - sync multiple attempts to download the same file multiple times
        - re-download the file in case of a previous failed download

    A temporary directory is used for each download. The temporary directory is unique for each output_filename,
    and it's obtained using the md5 of the output_filename. Only when the downloaded file is ok the temporary directory
    is deleted and the file moved in output directory.


    :param download_mode: copernicus download mode: subset|get
    :param dry_run: Print only the downloading info without actually downloading the file
    :param overwrite: Force the download of the file also if it already exists locally
    """
    # check if download mode is supported
    if download_mode not in DOWNLOAD_MODES:
        raise ValueError(f"Download mode not supported: '{download_mode}'")
    logger.info(f"Download mode: {download_mode}")

    # get mandatory args
    output_filename = (
        kwargs["output_filename"] if download_mode == "subset" else kwargs["filter"]
    )
    output_directory = kwargs["output_directory"]

    # set output directory
    if output_directory is None:
        output_directory = utils.cwd()
    logger.info(f"Output directory: {output_directory}")

    # check if  the file  is already present
    logger.info(f"Output filename: {output_filename}")
    destination_file = os.path.join(output_directory, output_filename)
    files_found = glob.glob(destination_file)
    if not overwrite and len(files_found) > 0:
        logger.info(f"File already exists: {', '.join(files_found)}")
        return

    # get temporary directory where to download the file
    temporary_dl_directory = utils.get_temporary_directory(
        output_filename=output_filename,
        base_directory=output_directory,
    )
    logger.debug(f"Temporary directory: {temporary_dl_directory}")

    # pid
    pid_file = os.path.join(temporary_dl_directory, ".pid")

    # check if another download is ongoing or a zombie directory is present
    if os.path.exists(temporary_dl_directory):
        logger.debug(f"Found temporary directory: {temporary_dl_directory}")
        if os.path.exists(pid_file) and utils.another_instance_in_execution(pid_file):
            logger.info(
                f"Another download process already exists: {pid_file}, nothing to do..."
            )
            return

        # an error must occur in the previous download, restart it
        logger.info("Zombie download dir found, cleaning it")
        shutil.rmtree(temporary_dl_directory)

    # safe mkdir and write pid
    try:
        os.makedirs(temporary_dl_directory, exist_ok=False)
        with open(pid_file, "w") as f:
            f.write(f"{os.getpid()}\n")
    except OSError as e:
        # if two processes start in the same moment the previous pid check can fail
        logger.error(
            f"Cannot create temporary directory: {temporary_dl_directory}, possible conflict ongoing"
        )
        raise e

    if dry_run:
        return

    kwargs["output_directory"] = temporary_dl_directory
    download_func = get_download_func(download_mode)
    try:
        download_func(**kwargs)
    except SystemExit as e:
        logger.error(f"An error occurs during download: {e}")

        # check if the file is not on mds
        dataset_id = kwargs["dataset_id"]
        mds_filter = kwargs["filter"]
        file_list = mds_list(dataset_id, mds_filter, quiet=False)
        if len(file_list) == 0:
            shutil.rmtree(temporary_dl_directory)
            raise FileNotFoundError(f"No match found for {mds_filter} if {dataset_id}")
        shutil.rmtree(temporary_dl_directory)
        raise e
    except Exception as e:
        logger.error(f"An error occurs during downloading {kwargs}: {e}")
        shutil.rmtree(temporary_dl_directory)
        raise e

    # move in output_directory
    for file in glob.glob(os.path.join(temporary_dl_directory, "*")):
        logger.info(f"mv {file} to {output_directory}")
        utils.mv_overwrite(file, output_directory)

    logger.info(f"Removing temporary directory: {temporary_dl_directory}")
    shutil.rmtree(temporary_dl_directory)


def get_download_func(download_mode):
    if download_mode == "subset":
        return copernicus.subset
    if download_mode == "get":
        return copernicus.get

    raise ValueError(f"Unknown download mode: {download_mode}")


@utils.elapsed_time
def mds_update_download(**kwargs):
    mds_filter = kwargs["filter"]
    output_directory = kwargs["output_directory"]

    # get list of files
    dataset_id = kwargs["dataset_id"]
    s3_files_list = mds_list(dataset_id, mds_filter, quiet=False)

    if len(s3_files_list) == 0:
        raise FileNotFoundError(
            f"No matching files found for {dataset_id}/{mds_filter} on mds"
        )

    # for each file get etag
    s3_files = []
    for s3_file in s3_files_list:
        logger.info(f"Try to obtain Etag for: {s3_file}")
        s3_files.extend(mds_etag(s3_file, *[None for _ in range(5)]))

    # download
    for s3_file in s3_files:
        filename = os.path.basename(s3_file.name)
        dest_file = str(os.path.join(output_directory, filename))

        if os.path.exists(dest_file) and etag_match(dest_file, s3_file.etag):
            logger.info(f"{s3_file} already updated, nothing to do...")
            continue

        bk_file = f"{dest_file}.bk"
        if os.path.exists(dest_file):
            logger.info(f"New version available for {s3_file.name}")
            logger.info(f"Creating backup file: {bk_file}")
            shutil.move(dest_file, bk_file)

        kwargs["filter"] = filename
        mds_download("get", **kwargs)

        # update json file
        # update_etag(filename, output_directory, s3_file.etag)

        if os.path.exists(bk_file):
            logger.info(f"Removing backup file: {bk_file}")
            os.remove(bk_file)


@utils.elapsed_time
def update_etag(filename, output_directory, etag):
    sync_file = str(os.path.join(output_directory, SYNC_FILE))
    with open(sync_file, "a") as s:
        with file_lock(s):
            db_file = str(os.path.join(output_directory, DB_FILE))
            try:
                with open(db_file, "r") as f_read:
                    data = json.load(f_read)
            except FileNotFoundError:
                data = {}

            data[filename] = etag

            with open(db_file, "w") as f_write:
                json.dump(data, f_write, indent=4)


@contextlib.contextmanager
def file_lock(file):
    try:
        fcntl.lockf(file, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.lockf(file, fcntl.LOCK_UN)


@utils.elapsed_time
def download_file(*args, **kwargs):
    print("Downloading")


def log():
    logger.info("I'm wrapper")
