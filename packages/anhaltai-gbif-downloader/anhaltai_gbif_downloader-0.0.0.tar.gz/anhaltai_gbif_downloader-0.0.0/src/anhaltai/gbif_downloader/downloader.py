"""
GBIFImageDownloader Class
This class is responsible for downloading images from the GBIF API,
processing occurrence records, and uploading images to a MinIO bucket.
"""

import os
import logging
import requests
from requests.exceptions import RequestException, Timeout, HTTPError

from anhaltai.gbif_downloader.utils import (
    normalize_and_upload_image,
    upload_metadata,
    get_image_hash,
)

from anhaltai.gbif_downloader.config import (
    GBIF_SESSION,
    OUTPUT_PATH,
)


class GBIFImageDownloader:
    """
    GBIFImageDownloader is a class that handles the downloading of images
    from the GBIF API, processing occurrence records, and uploading images
    to a MinIO bucket. It handles the downloading of images concurrently
    using threads. It also provides methods for fetching data from the GBIF API,
    building taxonomy output paths, processing occurrence records, and processing
    image items.
    It is designed to work with a configuration that includes a MinIO client,
    a bucket name, an output path, and parameters for crawling new entries,
    maximum threads, and a requests session.
    """

    def __init__(self):
        self.output_path = OUTPUT_PATH
        self.session = GBIF_SESSION

    def fetch_data(self, url):
        """
        Fetches data from the given URL using the requests' session.
        Args:
            url: The URL to fetch data from.

        Returns:
            The JSON response from the URL.

        Raises:
            RequestException: If there is a network error or timeout.
            ValueError: If the response cannot be decoded as JSON.
        """
        try:
            response = self.session.get(url, timeout=25)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logging.error("Network error for url %s: %s", url, e)
            raise e
        except ValueError as e:
            logging.error("JSON decoding error for url %s: %s", url, e)
            raise e

    def build_taxonomy_output_path(self, record, occurrence_id):
        """
        Builds the output path for the taxonomy based on the record's taxonomic keys,
        query taxon key and the output path defined in the class.
        Args:
            record: The occurrence record containing taxonomic keys.
            occurrence_id: The unique identifier for the occurrence record.

        Returns:
            The constructed output path for the taxonomy.

            If any taxonomic key is missing it returns a path indicating an unknown
            taxonomy path.
        """
        taxonomic_keys = [
            "kingdomKey",
            "phylumKey",
            "classKey",
            "orderKey",
            "familyKey",
            "genusKey",
            "speciesKey",
            "key",
        ]

        path_parts = [self.output_path]

        for key in taxonomic_keys:
            value = record.get(key)

            if not value:
                logging.warning(
                    "[occurrence_id=%s] Missing taxonomy key %s in record: %s",
                    occurrence_id,
                    key,
                    record,
                )
                return os.path.join(self.output_path, "unknown")

            path_parts.append(str(value))

        return os.path.join(*path_parts)

    def process_occurrence_record(self, record, taxonomy_path, occurrence_id):
        """
        Processes an occurrence record by checking if it contains a valid media list.
        If valid media items are found, it processes each image item by downloading,
        normalizing, and uploading the image to the MinIO bucket.
        It also uploads metadata associated with the occurrence record.
        Args:
            record: The occurrence record containing media items.
            taxonomy_path: The path where the taxonomy images will be stored in MinIO.
            occurrence_id: The unique identifier for the occurrence record.
        """

        if "media" not in record:
            logging.warning(
                "[occurrence_id=%s] No valid media list in record: %s",
                occurrence_id,
                record,
            )
            return

        for media_item in record["media"]:

            self.process_image_item(
                media_item=media_item,
                taxonomy_path=taxonomy_path,
                occurrence_id=occurrence_id,
            )

        upload_metadata(
            record=record,
            taxonomy_path=taxonomy_path,
            file_name=occurrence_id,
        )

    def process_image_item(
        self,
        media_item,
        taxonomy_path,
        occurrence_id,
    ):
        """
        Processes an individual image item by downloading the image,
        generating a SHA-256 hash for the image, converting it to PNG format with
        RGB color channels, and uploading it to the MinIO bucket. The media item is
        updated with the hash number.

        If the image URL is invalid or if there are any errors during the download,
        it logs a warning or error message.

        Args:
            media_item: The media item containing the image URL and other metadata.
            taxonomy_path: The path where the taxonomy images will be stored in MinIO.
            occurrence_id: The unique identifier for the occurrence record.
        """

        image_url = media_item.get("identifier")
        if not image_url:
            logging.warning(
                "[occurrence_id=%s] Missing or invalid image_url in record %s",
                occurrence_id,
                media_item,
            )
            return
        try:
            img_response = self.session.get(image_url, timeout=25)
            img_response.raise_for_status()
            image_bytes = img_response.content
            image_hash = get_image_hash(image_bytes=image_bytes, image_url=image_url)
            if image_hash is None:
                logging.warning(
                    "[occurrence_id=%s] Skipping image due to hash failure: %s",
                    occurrence_id,
                    image_url,
                )
                return

            img_path = os.path.join(taxonomy_path, f"{image_hash}.png")

            normalize_and_upload_image(image_bytes=image_bytes, img_path=img_path)

            media_item["hash_number"] = image_hash

            logging.debug(
                "Saved image: %s, Occurrence ID: %s", image_url, occurrence_id
            )

        except (RequestException, HTTPError, Timeout) as e:
            logging.error(
                "[occurrence_id=%s] Error Downloading URL %s: %s",
                occurrence_id,
                image_url,
                e,
            )
