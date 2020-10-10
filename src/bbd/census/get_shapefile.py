from typing import Dict, Union
from urllib.parse import urljoin
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
import logging

import requests

from ..working_directory import working_directory

from .geography import Geography
from .us import state_to_fips

"""Maps year to congressional district number"""
CD = {
    2019: 116,
    2018: 116,
    2017: 115,
    2016: 115,
    2015: 114,
    2014: 114,
    2013: 113,
    2012: 113,
    2011: 112,
}


def shapefile_urls(fips: str, year=2019) -> Dict[str, str]:
    """Generates urls to shapefiles associated with a given fips code
    on the census ftp site.

    Note that these urls may not work for every year.
    Note that these urls point to a zip file.
    """
    try:
        cd = CD[year]
    except KeyError:
        logging.warning(f"Unsupported year: {year}. Urls may be incorrect")
        cd = "xxx"

    base = f"https://www2.census.gov/geo/tiger/TIGER{year}/"
    urls = {
        "tract": urljoin(base, f"TRACT/tl_{year}_{fips}_tract.zip"),  # 2019
        "congressional district": urljoin(base, f"CD/tl_{year}_us_cd{cd}.zip"),  # 2019
        "county": urljoin(base, f"COUNTY/tl_{year}_us_county.zip"),
        "state": urljoin(base, f"STATE/tl_{year}_us_state.zip"),
        "zip code tabulation area": urljoin(base, f"ZCTA5/tl_{year}_us_zcta510.zip"),
        "block": urljoin(base, f"TABBLOCK/tl_{year}_{fips}_tabblock10.zip"),  # 14-19
        "block group": urljoin(base, f"BG/tl_{year}_{fips}_bg.zip"),
    }

    return urls


def get_shapefile(
    geography: Geography,
    state: Union[int, str],
    year: int,
    cache: bool = False,
) -> Path:
    """Download and extract a census shapefile for a specified geography.
    Returns the name of the extracted directory.

    Shapefiles are also available directly from the US Census Bureau:
        https://www.census.gov/cgi-bin/geo/shapefiles/index.php
    """

    fips = state_to_fips(state)

    # Get the shapefile URL
    url = shapefile_urls(fips, year)[geography]

    # Determine name of zip file
    zip_name = url.split("/")[-1]  # e.g. "tl_2019_us_cd.zip"
    dir_name = zip_name.split(".")[0]  # e.g. "tl_2019_us_cd"
    save_to = working_directory.resolve(dir_name)

    # If it's okay to use the cached directory, check if it exists
    # and return it if possible
    if cache and save_to.is_dir() and save_to.exists():
        logging.debug(f"Using cached directory: {dir_name}")
        return save_to

    # Not using the cached file, download and extract
    logging.info(
        "Not using chached directory. "
        "Downloading shapefile from: {url}; to: {save_to}"
    )

    r = requests.get(url, stream=True)
    if not r.ok:
        raise RuntimeError(f"Bad request. Status code: {r.status_code} Url: {url}")

    with ZipFile(BytesIO(r.content)) as z:
        z.extractall(save_to)

    # Return path to extracted directory
    return save_to


if __name__ == "__main__":
    state = "CO"
    year = 2019
    name = get_shapefile(Geography.COUNTY, state, year)
