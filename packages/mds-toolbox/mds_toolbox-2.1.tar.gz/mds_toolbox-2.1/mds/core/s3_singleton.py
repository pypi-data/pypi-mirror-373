import fnmatch
import glob
import logging
import multiprocessing
import os

import boto3
from botocore import UNSIGNED
from botocore.config import Config

from mds.core.s3file import S3File

# conf
logger = logging.getLogger("mds")
lock = multiprocessing.Lock()
S3_ENDPOINT = "https://s3.waw3-1.cloudferro.com"


class Singleton(type):
    """Multiprocessing safe implementation of a singleton class"""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(Singleton, cls).__call__(
                        *args, **kwargs
                    )
        return cls._instances[cls]


def clean_corrupted_file(dest_file: str):
    """Removes corrupted file if it exists"""
    # generally s3_client download the file as dest_file.STRING
    files_to_clean = glob.glob(f"{dest_file}.*")
    for file_to_clean in files_to_clean:
        logger.info(f"Cleaning {file_to_clean}")
        os.remove(file_to_clean)


def build_s3_path(dataset, products, subdir, version):
    """Build the s3 path with the provided information"""
    s3_path = f"native/{products}"
    if dataset:
        s3_path += f"/{dataset}"
    if version:
        s3_path += f"_{version}"
    if subdir:
        s3_path += f"/{subdir}"
    return s3_path


class S3(metaclass=Singleton):
    """
    Multiprocessing safe implementation of a singleton class to provide a unique client connection to a s3 endpoint.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, s3_endpoint=S3_ENDPOINT):
        s3_endpoint = s3_endpoint
        self.__s3 = boto3.client(
            "s3",
            endpoint_url=s3_endpoint,
            config=Config(
                signature_version=UNSIGNED,
                retries={"total_max_attempts": 10, "mode": "adaptive"},
                connect_timeout=300,
                read_timeout=300,
                tcp_keepalive=True,
            ),
        )
        self.__paginator = self.__s3.get_paginator("list_objects_v2")

    @property
    def paginator(self):
        return self.__paginator

    @property
    def s3(self):
        return self.__s3

    def file_list(
        self,
        s3_bucket: str,
        products: str,
        dataset: str,
        version: str,
        file_filter: str,
        subdir: str = None,
        recursive: bool = False,
    ) -> list[S3File]:
        """
        Listing file on s3 bucket and return the list of file that match the provided filter
        :param s3_bucket: Name of s3 bucket
        :param products: Product ID
        :param dataset: Dataset ID
        :param version: Dataset version
        :param file_filter: A pattern that must match the absolute paths of the files to download.
        :param subdir: Dataset subdirectory
        :param recursive: If True, recursively list the files
        :return: A list of S3Files found in the s3 paths that match the file_filter
        :raise: A FileNotFoundError if the path on s3 doesn't exist or if no file are found
        """
        files_found = []
        paginator = self.__paginator
        delimiter = "*" if recursive else "/"

        s3_path = build_s3_path(dataset, products, subdir, version)
        logger.info(f"Listing files in {s3_bucket}/{s3_path}")

        for s3_result in paginator.paginate(
            Bucket=s3_bucket, Prefix=f"{s3_path}/", Delimiter=delimiter
        ):
            if "Contents" not in s3_result:
                raise FileNotFoundError(f"No result found for {s3_bucket}/{s3_path}")

            for content in s3_result["Contents"]:
                etag = content["ETag"].replace('"', "")
                s3_file = content["Key"]
                last_modified = content["LastModified"]
                if fnmatch.fnmatch(s3_file, f"*{file_filter}*"):
                    files_found.append(S3File(s3_bucket, s3_file, etag, last_modified))

        return files_found

    def download(self, s3_bucket: str, s3_file: str, dest_file: str) -> None:
        """
        Download a file from s3 bucket
        :param s3_bucket: Name of s3 bucket
        :param s3_file: Absolute path to s3 file to download (i.e. s3://bucket/product/dataset_version/yyyy/mm/file.nc)
        :param dest_file: Destination file to download
        """
        s3 = self.s3
        try:
            clean_corrupted_file(dest_file)
            s3.download_file(s3_bucket, s3_file, dest_file)
            if not os.path.isfile(dest_file):
                raise RuntimeError(
                    f"Unable to download {s3_file} as {dest_file}, unknown error"
                )
        except BaseException as e:
            logger.critical(f"An error occurs during the download: {e}")
            clean_corrupted_file(dest_file)
            raise e
