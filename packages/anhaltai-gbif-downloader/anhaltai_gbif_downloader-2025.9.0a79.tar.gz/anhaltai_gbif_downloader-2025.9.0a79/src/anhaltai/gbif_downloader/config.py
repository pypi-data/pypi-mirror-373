"""
Configuration module for the GBIF Downloader project.
This module loads configuration settings from a file and sets up constants
for the application.
"""

import os
from datetime import datetime, timezone

import threading
from anhaltai_commons_minio.client_utils import get_client
import requests
from requests.adapters import HTTPAdapter
from anhaltai.gbif_downloader.config_loader import load_config


def create_request_session(
    pool_connections: int = 100, pool_maxsize: int = 100, max_retries: int = 5
):
    """
    Create a requests session with custom connection pooling and retry settings.
    Args:
        pool_connections: Number of connection pools to maintain.
        pool_maxsize: Maximum number of connections in each pool.
        max_retries: Maximum number of retries for failed requests.
    Returns:
        requests.Session: Configured session object.
    """
    session = requests.Session()
    adapter = HTTPAdapter(
        pool_connections=pool_connections,
        pool_maxsize=pool_maxsize,
        max_retries=max_retries,
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


CONFIG = load_config()

BUCKET = CONFIG["minio"]["bucket"]
ENDPOINT = CONFIG["minio"]["endpoint"]
SECURE = CONFIG["minio"]["secure"]
CERT_CHECK = CONFIG["minio"]["cert_check"]

OUTPUT_PATH = CONFIG["paths"]["output"]
LOG_DIR = CONFIG["paths"]["log_dir"]
TREE_LIST_INPUT_PATH = CONFIG["paths"]["tree_list_input_path"]
PROCESSED_TREE_LIST_PATH = CONFIG["paths"]["processed_tree_list_path"]

ALREADY_PREPROCESSED = CONFIG["options"]["already_preprocessed"]
CRAWL_NEW_ENTRIES = CONFIG["options"]["crawl_new_entries"]
MAX_THREADS = CONFIG["options"]["max_threads"]

QUERY_PARAMS = CONFIG.get("query_params", {})

START_TIME = datetime.now(timezone.utc).strftime("%Y_%m_%d_%H_%M_%S")
LOG_PATH = os.path.join(OUTPUT_PATH, LOG_DIR, f"log_{START_TIME}.txt")

GBIF_SESSION = create_request_session()

SEMAPHORE_THREADS = threading.Semaphore(MAX_THREADS)

MINIO_CLIENT = get_client(secure=SECURE, cert_check=CERT_CHECK, endpoint=ENDPOINT)
