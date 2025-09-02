# Marine Data Store ToolBox

This Python script provides a command-line interface (CLI) for downloading datasets using
[copernicusmarine toolbox](https://help.marine.copernicus.eu/en/collections/4060068-copernicus-marine-toolbox)
or [botos3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

[![boto3](https://img.shields.io/badge/boto3->1.34-blue.svg)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
[![copernicusmarine](https://img.shields.io/badge/copernicusmarine->1.06-blue.svg)](https://help.marine.copernicus.eu/en/collections/4060068-copernicus-marine-toolbox)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

<!-- TOC -->
* [Marine Data Store ToolBox](#marine-data-store-toolbox)
* [How to Install it](#how-to-install-it)
  * [Uninstall](#uninstall)
* [Usage](#usage)
  * [S3 direct access](#s3-direct-access)
    * [s3-get](#s3-get)
    * [s3-list](#s3-list)
  * [Wrapper for copernicusmarine](#wrapper-for-copernicusmarine)
    * [Subset](#subset)
    * [Get](#get)
    * [File List](#file-list)
    * [Etag](#etag)
  * [Authors](#authors)
<!-- TOC -->

---
# How to Install it

Create the conda environment:

```shell
mamba env create -f environment.yml
mamba activate mdsenv

pip install .
```

## Uninstall

To uninstall it:

```shell
mamba activate mdsenv

pip uninstall mds-toolbox
```

---

# Usage

The script provides several commands for different download operations:

```shell
Usage: mds [OPTIONS] COMMAND [ARGS]...

Options:
  -h, --help  Show this message and exit.

Commands:
  etag       Get the etag of a give S3 file
  file-list  Wrapper to copernicus marine toolbox file list
  get        Wrapper to copernicusmarine get
  s3-get     Download files with direct access to MDS using S3
  s3-list    Listing file on MDS using S3
  subset     Wrapper to copernicusmarine subset
```

---

## S3 direct access

Since the copernicusmarine tool add a heavy overhead to s3 request, two functions has been developed to:

* make very fast s3 request
* provide a thread-safe access to s3 client

### s3-get

```shell
Usage: mds s3-get [OPTIONS]

Options:
  -b, --bucket TEXT            Bucket name  [required]
  -f, --filter TEXT            Filter on the online files  [required]
  -o, --output-directory TEXT  Output directory  [required]
  -p, --product TEXT           The product name  [required]
  -i, --dataset-id TEXT        Dataset Id  [required]
  -g, --dataset-version TEXT   Dataset version or tag
  -r, --recursive              List recursive all s3 files
  --threads INTEGER            Downloading file using threads
  -s, --subdir TEXT            Dataset directory on mds (i.e. {year}/{month})
                               - If present boost the connection
  --overwrite                  Force overwrite of the file
  --keep-timestamps            After the download, set the correct timestamp
                               to the file
  --sync-time                  Update the file if it changes on the server
                               using last update information
  --sync-etag                  Update the file if it changes on the server
                               using etag information
  --help                       Show this message and exit.
```

**Example**

```shell
mds s3-get -i cmems_obs-ins_med_phybgcwav_mynrt_na_irr -b mdl-native-03 -g 202311 -p INSITU_MED_PHYBGCWAV_DISCRETE_MYNRT_013_035 -o "/work/antonio/20240320" -s latest/$(date -du +"%Y%m%d") --keep-timestamps --sync-etag -f $(date -du +"%Y%m%d")
```

**Example using threads**

```shell
mds s3-get --threads 10 -i cmems_obs-ins_med_phybgcwav_mynrt_na_irr -b mdl-native-03 -g 202311 -p INSITU_MED_PHYBGCWAV_DISCRETE_MYNRT_013_035 -o "." -s latest/$(date -du +"%Y%m%d") --keep-timestamps --sync-etag -f $(date -du +"%Y%m%d")
```

### s3-list

```shell
Usage: mds.py s3-list [OPTIONS]

Options:
  -b, --bucket TEXT           Filter on the online files  [required]
  -f, --filter TEXT           Filter on the online files  [required]
  -p, --product TEXT          The product name  [required]
  -i, --dataset-id TEXT       Dataset Id
  -g, --dataset-version TEXT  Dataset version or tag
  -s, --subdir TEXT           Dataset directory on mds (i.e. {year}/{month}) -
                              If present boost the connection
  -r, --recursive             List recursive all s3 files
  --help                      Show this message and exit.
```

**Example**

```shell
mds s3-list -b mdl-native-01 -p INSITU_GLO_PHYBGCWAV_DISCRETE_MYNRT_013_030 -i cmems_obs-ins_glo_phybgcwav_mynrt_na_irr -g 202311 -s "monthly/BO/202401" -f "*" | tr " " "\n"
```

**Example recursive**

```shell
mds s3-list -b mdl-native-12 -p MEDSEA_ANALYSISFORECAST_PHY_006_013 -f '*' -r | tr " " "\n"
```

---

## Wrapper for copernicusmarine

**The following functions rely on copernicusmarine implementation, the final result is strictly related to the installed
version**

### Subset

```shell
Usage: mds.py subset [OPTIONS]

Options:
  -o, --output-directory TEXT    Output directory  [required]
  -f, --output-filename TEXT     Output filename  [required]
  -i, --dataset-id TEXT          Dataset Id  [required]
  -v, --variables TEXT           Variables to download. Can be used multiple times
  -x, --minimum-longitude FLOAT  Minimum longitude for the subset.
  -X, --maximum-longitude FLOAT  Maximum longitude for the subset.
  -y, --minimum-latitude FLOAT   Minimum latitude for the subset. Requires a
                                 float within this range:  [-90<=x<=90]
  -Y, --maximum-latitude FLOAT   Maximum latitude for the subset. Requires a
                                 float within this range:  [-90<=x<=90]
  -z, --minimum-depth FLOAT      Minimum depth for the subset. Requires a
                                 float within this range:  [x>=0]
  -Z, --maximum-depth FLOAT      Maximum depth for the subset. Requires a
                                 float within this range:  [x>=0]
  -t, --start-datetime TEXT      Start datetime as:
                                 %Y|%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d
                                 %H:%M:%S|%Y-%m-%dT%H:%M:%S.%fZ
  -T, --end-datetime TEXT        End datetime as:
                                 %Y|%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d
                                 %H:%M:%S|%Y-%m-%dT%H:%M:%S.%fZ
  -r, --dry-run                  Dry run
  -g, --dataset-version TEXT     Dataset version or tag
  -n, --username TEXT            Username
  -w, --password TEXT            Password
  --help                         Show this message and exit.
```

**Example**

```shell
mds subset -f output.nc -o . -i cmems_mod_glo_phy-thetao_anfc_0.083deg_P1D-m -x -18.16667 -X 1.0 -y 30.16 -Y 46.0 -z 0.493 -Z 5727.918000000001 -t 2025-01-01 -T 2025-01-01 -v thetao 
```

### Get

**Command**:

```shell
Usage: mds.py get [OPTIONS]

Options:
  -f, --filter TEXT            Filter on the online files
  -o, --output-directory TEXT  Output directory  [required]
  -i, --dataset-id TEXT        Dataset Id  [required]
  -g, --dataset-version TEXT   Dataset version or tag
  -s, --service TEXT           Force download through one of the available
                               services using the service name among
                               ['original-files', 'ftp'] or its short name
                               among ['files', 'ftp'].
  -d, --dry-run                Dry run
  -u, --update                 If the file not exists, download it, otherwise
                               update it it changed on mds
  -v, --dataset-version TEXT   Dry run
  -nd, --no-directories TEXT   Option to not recreate folder hierarchy in
                               output directory
  --disable-progress-bar TEXT  Flag to hide progress bar
  -n, --username TEXT          Username
  -w, --password TEXT          Password
  --help                       Show this message and exi
```

**Example**

```shell
mds get -f '20250210*_d-CMCC--TEMP-MFSeas9-MEDATL-b20250225_an-sv10.00.nc' -o . -i cmems_mod_med_phy-tem_anfc_4.2km_P1D-m
```

### File List

To retrieve a list of file, use:

```shell
Usage: mds.py file-list [OPTIONS] DATASET_ID MDS_FILTER

Options:
  -g, --dataset-version TEXT  Dataset version or tag
  --help                      Show this message and exit.
```

**Example**

```shell
mds file-list cmems_mod_med_phy-cur_anfc_4.2km_PT15M-i *b20250225* -g 202411
```

### Etag

```shell
Usage: mds.py etag [OPTIONS]

Options:
  -e, --s3_file TEXT     Path to a specific s3 file - if present, other
                         parameters are ignored.
  -p, --product TEXT     The product name
  -d, --dataset_id TEXT  The datasetID
  -v, --version TEXT     Force the selection of a specific dataset version
  -s, --subdir TEXT      Subdir structure on mds (i.e. {year}/{month})
  -f, --mds_filter TEXT  Pattern to filter data (no regex)
  --help                 Show this message and exit.
```

**Example**

With a specific file:

```shell
mds etag -e s3://mdl-native-12/native/MEDSEA_ANALYSISFORECAST_PHY_006_013/cmems_mod_med_phy-cur_anfc_4.2km_PT15M-i_202411/2025/05/20250501_qm-CMCC--RFVL-MFSeas9-MEDATL-b20250513_an-sv10.00.nc
```

Or:

```shell
mds etag -p MEDSEA_ANALYSISFORECAST_PHY_006_013 -i cmems_mod_med_phy-cur_anfc_4.2km_PT15M-i -g 202411 -f '*' -s 2025/05
```

---

## Authors

* Antonio Mariani - antonio.mariani@cmcc.it
