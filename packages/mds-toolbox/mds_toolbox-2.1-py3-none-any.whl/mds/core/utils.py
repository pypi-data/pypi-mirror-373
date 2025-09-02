import datetime
import hashlib
import json
import logging
import os
import shutil
import time
from typing import Sequence, Callable


logger = logging.getLogger("mds")


def cwd() -> str:
    """returns the current working directory"""
    return os.getcwd()


def another_instance_in_execution(pid_file: str) -> bool:
    """Try to read pid from a pid file to check if there is another instance in execution"""
    if os.path.exists(pid_file):
        with open(pid_file) as f:
            pid = int(f.read().strip())
            return pid_is_running(pid)
    else:
        return False


def pid_is_running(pid: int) -> bool:
    """Check For the existence of a unix pid. 0 signal has no effect on the process"""
    try:
        # 0 signal doesn't have any effect
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def pprint_dict(my_dict: dict) -> None:
    """use json format to pretty print a dictionary"""
    pretty_dict = json.dumps(my_dict, indent=4)
    logger.info(pretty_dict)


def check_dict_validity(my_dict: dict, mandatory_attrs: list) -> None:
    # check if all values are correct
    for k, v in my_dict.items():
        if v is None and k in mandatory_attrs:
            raise ValueError(f"Missing value for '{k}'")

        # in case of list arguments check if they contain values
        if isinstance(v, Sequence) and len(v) == 0:
            raise ValueError(f"Empty value for '{k}'")

    # check if mandatory attrs are present
    my_dict_attrs = set(my_dict.keys())
    missing_attrs = set(mandatory_attrs) - my_dict_attrs
    if missing_attrs:
        raise ValueError(f"Missing attributes: {', '.join(missing_attrs)}")


def get_temporary_directory(output_filename: str, base_directory: str) -> str:
    """
    Given a filename, a uniquely identifiable temporary directory is generated within the desired directory

    :param output_filename: The output filename used to generate the temporary directory
    :param base_directory: The path where to generate the base_directory
    """
    md5_filename = hashlib.md5(output_filename.encode()).hexdigest()

    return os.path.join(base_directory, f".{md5_filename}")


def mv_overwrite(file: str, output_directory: str):
    filename = os.path.basename(file)
    dest_file = str(os.path.join(output_directory, filename))
    shutil.move(file, dest_file)


def compute_md5(file_path: str):
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()


def factor_of_1_mb(filesize, num_parts):
    x = filesize / int(num_parts)
    y = x % 1048576
    return int(x + 1048576 - y)


def calc_etag(input_file, part_size):
    md5_digests = []
    with open(input_file, "rb") as f:
        for chunk in iter(lambda: f.read(part_size), b""):
            md5_digests.append(hashlib.md5(chunk).digest())
    return hashlib.md5(b"".join(md5_digests)).hexdigest() + "-" + str(len(md5_digests))


def possible_partsizes(filesize, num_parts):
    return (
        lambda part_size: part_size < filesize
        and (float(filesize) / float(part_size)) <= num_parts
    )


def compute_etag(input_file, etag):
    filesize = os.path.getsize(input_file)
    num_parts = int(etag.split("-")[1])

    partsizes = [  # Default Partsizes Map
        8388608,  # aws_cli/boto3
        15728640,  # s3cmd
        factor_of_1_mb(
            filesize, num_parts
        ),  # Used by many clients to upload large files
    ]

    for part_size in filter(possible_partsizes(filesize, num_parts), partsizes):
        if etag == calc_etag(input_file, part_size):
            return True

    return False


def elapsed_time(func: Callable):
    def decorator(*args, **kwargs):
        start_time = time.perf_counter()
        func_args = f"args={args}" if args else "args=None"
        func_kwargs = f"kwargs={kwargs}" if kwargs else "kwargs=None"
        result = func(*args, **kwargs)
        elaps_time = time.perf_counter() - start_time
        logger.info(
            f"Elapsed time: {elaps_time} (s) - {func.__name__}({func_args}, {func_kwargs})"
        )
        return result

    return decorator


def etag_match(dest_file, digest: str):
    if "-" in digest:
        logger.debug("Comparing Etag")
        local_digest = compute_etag()
    else:
        logger.debug("Comparing md5")
        local_digest = compute_md5(dest_file)

    return local_digest == digest
    # use local file to store local etag info
    # output_directory = os.path.dirname(dest_file)
    # filename = os.path.basename(dest_file)
    #
    # sync_file = str(os.path.join(output_directory, SYNC_FILE))
    # db_file = str(os.path.join(output_directory, DB_FILE))
    #
    # if not os.path.exists(dest_file):
    #     return False
    #
    # with open(sync_file, 'a') as s:
    #     with file_lock(s):
    #         try:
    #             with open(db_file, 'r') as f_read:
    #                 data = json.load(f_read)
    #         except FileNotFoundError:
    #             data = {}
    #
    #         if filename not in data:
    #             return False
    #
    #         return data[filename] == etag


def timestamp_match(dest_file, remote_last_modified: datetime.datetime):
    local_last_modified = os.path.getmtime(dest_file)
    return local_last_modified == remote_last_modified.timestamp()


def split_list_into_parts(input_list: list, m):
    # Calculate the length of each part
    part_length = len(input_list) // m
    # Initialize an empty list to store parts
    parts = []
    # Split the list into parts
    for i in range(m):
        start = i * part_length
        # For the last part, include remaining elements
        end = (i + 1) * part_length if i < m - 1 else None
        parts.append(input_list[start:end])
    return parts
