"""
This module defines the GBIFCrawler class, which is responsible for crawling
the GBIF (Global Biodiversity Information Facility) API to extract occurrence records.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlencode
import requests

from anhaltai.gbif_downloader.config import MAX_THREADS, CRAWL_NEW_ENTRIES
from anhaltai.gbif_downloader.utils import does_record_exists


class GBIFCrawler:
    """
    This GBIFCrawler class is responsible for crawling the GBIF (Global Biodiversity
    Information Facility) API to extract occurrence records based on a specified
    taxon key. It uses a thread pool executor to process records concurrently,
    improving efficiency and performance during the crawling process. It also
    includes error handling for network requests and data processing. This class is
    part of the gbif_extractor package and is designed to work with a downloader
    instance that manages the fetching and processing of data.
    """

    def __init__(
        self,
        downloader,
        query_params: dict,
    ):
        """
        Initializes the GBIFCrawler crawler with the downloader and query parameters.
        Args:
            downloader: The downloader instance responsible for fetching data.
            query_params: A dictionary containing query parameters for the GBIF API.
        """
        self.downloader = downloader
        self.query_params = query_params
        self.query_offset = query_params.get("offset", 0)

    def build_query_url(self, offset: int = 0) -> str:
        """
        Builds the query URL for the GBIF API with the given offset.
        This method constructs the URL using the base GBIF occurrence search endpoint
        and appends the query parameters including the offset.
        Args:
            offset: The offset for pagination in the GBIF API query.

        Returns:
            The complete URL for the GBIF occurrence search.
        """
        params = {**self.query_params, "offset": offset}

        return f"https://api.gbif.org/v1/occurrence/search?{urlencode(params)}"

    def handle_data(self, occurrence_records):
        """
        Handles the data fetched from the GBIF API.
        This method processes each occurrence record in the occurrence_records.
        It checks if the occurrence ID exists, builds the taxonomy output path,
        and submits the record for processing using a thread pool executor.
        Args:
            occurrence_records: A list of occurrence records fetched from the GBIF API.
        """

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = []

            for record in occurrence_records:

                occurrence_id = record.get("key")
                if not occurrence_id:
                    logging.warning("[Record: %s] Record has no Occurrence.", record)
                    continue

                taxonomy_path = self.downloader.build_taxonomy_output_path(
                    record=record,
                    occurrence_id=occurrence_id,
                )

                record_exists = does_record_exists(
                    taxonomy_path=taxonomy_path,
                    file_name=occurrence_id,
                )

                if CRAWL_NEW_ENTRIES and record_exists:
                    continue

                futures.append(
                    executor.submit(
                        self.downloader.process_occurrence_record,
                        record,
                        taxonomy_path,
                        occurrence_id,
                    )
                )

            for future in as_completed(futures):
                try:
                    future.result()
                except (ValueError, KeyError, OSError) as e:
                    logging.error("Exception in thread: %s", e)

    def crawl(self):
        """
        Crawls the GBIF API for occurrence records based on the specified taxon key.
        This method constructs the query URL, fetches data from the GBIF API,
        and processes the occurrence_records in batches using the handle_data method.
        """
        offset = self.query_offset

        while True:

            url = self.build_query_url(offset=offset)
            logging.debug("Crawling url: %s", url)

            try:
                data = self.downloader.fetch_data(url)
            except (requests.exceptions.RequestException, ValueError):
                logging.error("Error fetching data from URL: %s", url)
                break

            occurrence_records = data.get("occurrence_records", [])
            if not occurrence_records:
                logging.error("No occurrence_records found for URL %s", url)
                break

            self.handle_data(occurrence_records)

            offset += len(occurrence_records)
            logging.debug(
                "%s occurrence_records remaining for URL %s at offset %s",
                data["count"] - offset,
                url,
                offset,
            )

            if "count" not in data:
                logging.error(
                    "Missing 'count' in response for URL %s in data %s",
                    url,
                    data,
                )
                break
            if offset >= data["count"]:
                break
