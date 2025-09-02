import click

from mds import mds_s3
from mds.core import wrapper
from mds.mng import initializer

verbose = click.option(
    "--log-level",
    "LOG_LEVEL",
    type=click.Choice(["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL", "QUIET"]),
    default="INFO",
    help="Verbosity level based on standard logging library",
)


@click.group(help="Manage S3 groups")
def s3_cli() -> None:
    pass


@s3_cli.command()
@click.option(
    "-e",
    "--s3_file",
    type=str,
    default=None,
    help="Path to a specific s3 file - if present, other parameters are ignored.",
)
@click.option("-p", "--product", type=str, default=None, help="The product name")
@click.option("-i", "--dataset_id", type=str, default=None, help="The datasetID")
@click.option(
    "-g",
    "--version",
    type=str,
    default=None,
    help="Force the selection of a specific dataset version",
)
@click.option(
    "-s",
    "--subdir",
    type=str,
    default=None,
    help="Subdir structure on mds (i.e. {year}/{month})",
)
@click.option(
    "-f",
    "--mds_filter",
    type=str,
    default=None,
    help="Pattern to filter data (no regex)",
)
@verbose
@initializer.init_app
def etag(**kwargs):
    """Get the etag of a give S3 file"""
    s3_files = wrapper.mds_etag(**kwargs)
    for s3_file in s3_files:
        print(f"{s3_file.name} {s3_file.etag}")


@s3_cli.command()
@click.option(
    "-b", "--bucket", "s3_bucket", required=True, type=str, help="Bucket name"
)
@click.option(
    "-f",
    "--filter",
    "file_filter",
    required=True,
    type=str,
    help="Filter on the online files",
)
@click.option(
    "-o", "--output-directory", required=True, type=str, help="Output directory"
)
@click.option("-p", "--product", required=True, type=str, help="The product name")
@click.option("-i", "--dataset-id", required=True, type=str, help="Dataset Id")
@click.option(
    "-g", "--dataset-version", type=str, default=None, help="Dataset version or tag"
)
@click.option(
    "-r", "--recursive", is_flag=True, default=False, help="List recursive all s3 files"
)
@click.option(
    "--threads",
    "n_threads",
    type=int,
    default=None,
    help="Downloading file using threads",
)
@click.option(
    "-s",
    "--subdir",
    type=str,
    default=None,
    help="Dataset directory on mds (i.e. {year}/{month}) - If present boost the connection",
)
@click.option(
    "--overwrite",
    required=False,
    is_flag=True,
    default=False,
    help="Force overwrite of the file",
)
@click.option(
    "--keep-timestamps",
    required=False,
    is_flag=True,
    default=False,
    help="After the download, set the correct timestamp to the file",
)
@click.option(
    "--sync-time",
    required=False,
    is_flag=True,
    default=False,
    help="Update the file if it changes on the server using last update information",
)
@click.option(
    "--sync-etag",
    required=False,
    is_flag=True,
    default=False,
    help="Update the file if it changes on the server using etag information",
)
@verbose
@initializer.init_app
def s3_get(**kwargs):
    """Download files with direct access to MDS using S3"""
    mds_s3.download_files(**kwargs)


@s3_cli.command()
@click.option(
    "-b",
    "--bucket",
    "s3_bucket",
    required=True,
    type=str,
    help="Filter on the online files",
)
@click.option(
    "-f",
    "--filter",
    "file_filter",
    required=True,
    type=str,
    help="Filter on the online files",
)
@click.option("-p", "--product", required=True, type=str, help="The product name")
@click.option("-i", "--dataset-id", required=False, type=str, help="Dataset Id")
@click.option(
    "-g", "--dataset-version", type=str, default=None, help="Dataset version or tag"
)
@click.option(
    "-s",
    "--subdir",
    type=str,
    default=None,
    help="Dataset directory on mds (i.e. {year}/{month}) - If present boost the connection",
)
@click.option(
    "-r", "--recursive", is_flag=True, default=False, help="List recursive all s3 files"
)
@verbose
@initializer.init_app
def s3_list(**kwargs):
    """Listing file on MDS using S3"""
    s3_files = mds_s3.get_file_list(**kwargs)
    print(f"{' '.join([f.file for f in s3_files])}")
