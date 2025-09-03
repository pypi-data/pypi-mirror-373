"""
Main entry point for the GBIF image downloader application.
This script initializes logging, validates query parameters, configures image settings,
and processes a list of tree species to download images from GBIF if necessary.
"""

import logging
import pandas as pd

from anhaltai.gbif_downloader.config import (
    QUERY_PARAMS,
    ALREADY_PREPROCESSED,
    TREE_LIST_INPUT_PATH,
    PROCESSED_TREE_LIST_PATH,
)

from anhaltai.gbif_downloader.utils import (
    validate_query_params,
    configure_image_settings,
)
from anhaltai.gbif_downloader.crawler.base import GBIFCrawler
from anhaltai.gbif_downloader.minio_log_handler import MinioLogHandler
from anhaltai.gbif_downloader.downloader import GBIFImageDownloader
from anhaltai.gbif_downloader.tree_list_processor import TreeListProcessor

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

minio_handler = MinioLogHandler()
minio_handler.setLevel(logging.INFO)
minio_handler.setFormatter(formatter)
logger.addHandler(minio_handler)

logger.info("MinIO-Logging started.")

validate_query_params(QUERY_PARAMS)
configure_image_settings()

if not ALREADY_PREPROCESSED:
    processor = TreeListProcessor(
        input_path=TREE_LIST_INPUT_PATH,
        sheet_name="Gehölzarten",
        taxon="speciesKey",
    )
    processor.process_tree_list(PROCESSED_TREE_LIST_PATH)

try:
    df = pd.read_csv(PROCESSED_TREE_LIST_PATH)
except Exception as e:
    logger.error("Error reading CSV file %s: %s", PROCESSED_TREE_LIST_PATH, e)
    raise SystemExit(f"Aborted due to CSV read error: {e}") from e

downloader = GBIFImageDownloader()

for species_key in df["species_key"].dropna().unique():

    QUERY_PARAMS["taxonKey"] = int(species_key)

    try:
        crawler = GBIFCrawler(downloader=downloader, query_params=QUERY_PARAMS)
        crawler.crawl()

    except (ValueError, KeyError) as e:
        logger.error("Error processing taxon key %s: %s", int(species_key), e)
        continue

logger.info("MinIO-Logging finished successfully.")
