import click

from mds import wrapper
from mds.mng import initializer

verbose = click.option(
    "--log-level",
    "LOG_LEVEL",
    type=click.Choice(["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL", "QUIET"]),
    default="INFO",
    help="Verbosity level based on standard logging library",
)


@click.group()
def wrapper_cli() -> None:
    pass


@wrapper_cli.command()
@click.argument("dataset_id", type=str)
@click.argument("mds_filter", type=str)
@click.option(
    "-g", "--dataset-version", type=str, default=None, help="Dataset version or tag"
)
@verbose
@initializer.init_app
def file_list(*args, **kwargs):
    """Wrapper to copernicus marine toolbox file list"""
    mds_file_list = wrapper.mds_list(*args, **kwargs)
    print(f"{' '.join(mds_file_list)}")


@wrapper_cli.command()
@click.option(
    "-o", "--output-directory", required=True, type=str, help="Output directory"
)
@click.option(
    "-f", "--output-filename", required=True, type=str, help="Output filename"
)
@click.option("-i", "--dataset-id", required=True, type=str, help="Dataset Id")
@click.option(
    "-v", "--variables", multiple=True, type=str, help="Variables to download"
)
@click.option(
    "-x", "--minimum-longitude", type=float, help="Minimum longitude for the subset."
)
@click.option(
    "-X", "--maximum-longitude", type=float, help="Maximum longitude for the subset. "
)
@click.option(
    "-y",
    "--minimum-latitude",
    type=float,
    help="Minimum latitude for the subset. Requires a float within this range:  [-90<=x<=90]",
)
@click.option(
    "-Y",
    "--maximum-latitude",
    type=float,
    help="Maximum latitude for the subset. Requires a float within this range:  [-90<=x<=90]",
)
@click.option(
    "-z",
    "--minimum-depth",
    type=float,
    help="Minimum depth for the subset. Requires a float within this range:  [x>=0]",
)
@click.option(
    "-Z",
    "--maximum-depth",
    type=float,
    help="Maximum depth for the subset. Requires a float within this range:  [x>=0]",
)
@click.option(
    "-t",
    "--start-datetime",
    type=str,
    default=False,
    help="Start datetime as: %Y|%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S|%Y-%m-%dT%H:%M:%S.%fZ",
)
@click.option(
    "-T",
    "--end-datetime",
    type=str,
    default=False,
    help="End datetime as: %Y|%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S|%Y-%m-%dT%H:%M:%S.%fZ",
)
@click.option("-r", "--dry-run", is_flag=True, default=False, help="Dry run")
@click.option(
    "-g", "--dataset-version", type=str, default=None, help="Dataset version or tag"
)
@click.option("-n", "--username", type=str, default=None, help="Username")
@click.option("-w", "--password", type=str, default=None, help="Password")
@verbose
@initializer.init_app
def subset(**kwargs):
    """Wrapper to copernicusmarine subset"""
    wrapper.mds_download("subset", **kwargs)


@wrapper_cli.command()
@click.option(
    "-f", "--filter", required=False, type=str, help="Filter on the online files"
)
@click.option(
    "-o", "--output-directory", required=True, type=str, help="Output directory"
)
@click.option("-i", "--dataset-id", required=True, type=str, help="Dataset Id")
@click.option(
    "-g", "--dataset-version", type=str, default=None, help="Dataset version or tag"
)
# @click.option('-s', '--service', type=str, default='files',
#               help="Force download through one of the available services using the service name among "
#                    "['original-files', 'ftp'] or its short name among ['files', 'ftp'].")
@click.option("-d", "--dry-run", is_flag=True, default=False, help="Dry run")
@click.option(
    "-u",
    "--update",
    is_flag=True,
    default=False,
    help="If the file not exists, download it, otherwise update it it changed on mds",
)
@click.option("-v", "--dataset-version", type=str, default=None, help="Dry run")
@click.option(
    "-nd",
    "--no-directories",
    type=str,
    default=True,
    help="Option to not recreate folder hierarchy in output directory",
)
@click.option(
    "--disable-progress-bar", type=str, default=True, help="Flag to hide progress bar"
)
@click.option("-n", "--username", type=str, default=None, help="Username")
@click.option("-w", "--password", type=str, default=None, help="Password")
@verbose
@initializer.init_app
def get(**kwargs):
    """Wrapper to copernicusmarine get"""
    update = kwargs.pop("update")
    if update:
        wrapper.mds_update_download(**kwargs)
    else:
        wrapper.mds_download("get", **kwargs)
