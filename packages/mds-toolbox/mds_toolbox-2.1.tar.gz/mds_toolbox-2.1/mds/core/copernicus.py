import pathlib
import copernicusmarine
import requests

from typing import List
from mds.core import utils


GET_MANDATORY_ATTRS = ["filter", "output_directory", "dataset_id"]
SUBSET_MANDATORY_ATTRS = [
    "output_filename",
    "output_directory",
    "dataset_id",
    "start_datetime",
    "end_datetime",
]


def subset(**subset_kwargs) -> pathlib.Path:
    subset_kwargs.update({"disable_progress_bar": True})
    utils.check_dict_validity(subset_kwargs, SUBSET_MANDATORY_ATTRS)

    # patch needed because Click returns a tuple but subset() needs a list of variables
    subset_kwargs["variables"] = list(subset_kwargs["variables"])

    # download
    utils.pprint_dict(subset_kwargs)
    result = copernicusmarine.subset(
        **subset_kwargs,
    )
    return result


def get(**get_kwargs) -> List[pathlib.Path]:
    utils.check_dict_validity(get_kwargs, GET_MANDATORY_ATTRS)

    # download
    utils.pprint_dict(get_kwargs)
    result = copernicusmarine.get(**get_kwargs)
    return result


def get_s3_native(product, dataset, version) -> str:
    stac_url = f"https://stac.marine.copernicus.eu/metadata/{product}/{dataset}_{version}/dataset.stac.json"
    response = requests.get(stac_url)

    # Check if the request was successful (status code 200)
    if response.status_code != 200:
        raise ValueError(
            f"Unable to get native from: {stac_url} - {response.status_code}: {response.text}"
        )

    dataset_stac = response.json()

    return dataset_stac["assets"]["native"]["href"]
