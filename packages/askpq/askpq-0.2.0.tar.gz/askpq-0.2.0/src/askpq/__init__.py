import json
import logging
import os
from typing import Literal
from urllib.parse import urljoin

import httpx
import icechunk
import xarray

DETECT_FROM_ENV = "detect from env"
DETECT_FROM_ENV_T = Literal["detect from env"]


def open_ds(
    dataset_id: str,
    access_key_id: str | DETECT_FROM_ENV_T = DETECT_FROM_ENV,
    secret_access_key: str | DETECT_FROM_ENV_T = DETECT_FROM_ENV,
    catalog_api_v1_endpoint: str | DETECT_FROM_ENV_T | Literal["default"] = "default",
) -> xarray.Dataset:
    if access_key_id == DETECT_FROM_ENV:
        logging.info("Finding ASKPQ_ACCESS_KEY_ID in env")
        access_key_id = os.environ.get("ASKPQ_ACCESS_KEY_ID")
        if access_key_id is None:
            error_message = "ASKPQ_ACCESS_KEY_ID not found in env"
            logging.error(error_message)
            logging.error("Stopping askpq client creation and raising an exception")
            raise NameError(error_message)
        else:
            logging.info("Found env var: ASKPQ_ACCESS_KEY_ID")

    if secret_access_key == DETECT_FROM_ENV:
        logging.info("Finding ASKPQ_SECRET_ACCESS_KEY in env")
        secret_access_key = os.environ.get("ASKPQ_SECRET_ACCESS_KEY")
        if secret_access_key is None:
            error_message = "ASKPQ_SECRET_ACCESS_KEY not found in env"
            logging.error(error_message)
            logging.error("Stopping askpq client creation and raising an exception")
            raise NameError(error_message)
        else:
            logging.info("Found env var: ASKPQ_SECRET_ACCESS_KEY")

    DEFAULT_CATALOG_API_V1_ENDPOINT = "https://catalog-api-v1.askpq.com"
    if catalog_api_v1_endpoint == "default":
        catalog_api_v1_endpoint = DEFAULT_CATALOG_API_V1_ENDPOINT
        logging.info(
            f"Using default catalog api v1 endpoint since None was provided: {DEFAULT_CATALOG_API_V1_ENDPOINT}"  # noqa: E501
        )
    elif catalog_api_v1_endpoint == DETECT_FROM_ENV:
        catalog_api_v1_endpoint = os.environ.get("ASKPQ_CATALOG_API_V1_ENDPOINT")
        if catalog_api_v1_endpoint is None:
            error_message = "Told to find catalog_api_v1_endpoint from environment, but did not find any variable named ASKPQ_CATALOG_API_V1_ENDPOINT"  # noqa: E501
            logging.error(error_message)
            logging.error("Stopping askpq client creation and raising an exception")
            raise NameError(error_message)
        else:
            logging.info(
                f"Found env var ASKPQ_CATALOG_API_V1_ENDPOINT: {catalog_api_v1_endpoint}"  # noqa: E501
            )

    # Query the catalog api for the bucket and prefix
    logging.info("Querying Askpq catalog api for storage bucket to connect to")
    url = urljoin(catalog_api_v1_endpoint, "/v1/bucket-and-prefix")
    resp = httpx.get(url, params={"dataset-id": dataset_id})
    bandp = resp.json()
    bucket = bandp["bucket"]
    prefix = bandp["prefix"]

    logging.info("Retrieving xarray dataset from stored data on storage bucket")
    # Open the bucket with the prefix using the tigris storage backend with icechunk
    icechunk_storage = icechunk.tigris_storage(
        bucket=bucket,
        prefix=prefix,
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        region="auto",
    )
    icechunk_repo = icechunk.Repository.open(icechunk_storage)
    icechunk_session = icechunk_repo.readonly_session(branch="main")
    ds = xarray.open_dataset(icechunk_session.store, engine="zarr", consolidated=False)

    return ds
