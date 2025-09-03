"""
This module defines the TreeListProcessor class, which processes a list of
latin names by loading data from a CSV or Excel file, retrieving taxon keys from
the GBIF API, and saving the results to a new CSV file.
"""

import os
import logging
import pandas as pd
import requests
from anhaltai.gbif_downloader.config import GBIF_SESSION


class TreeListProcessor:
    """
    TreeListProcessor is a class that processes a list of latin names
    by loading data from a CSV or Excel file, retrieving taxon keys from the
    GBIF API, and saving the results to a new CSV file.
    """

    def __init__(
        self,
        input_path: str,
        sheet_name: str | None = None,
        taxon: str = "speciesKey",
    ):
        """
        Initializes the TreeListProcessor with the input file path, sheet name,
        and taxon type. It sets up the GBIF session for API requests.
        Args:
            input_path: Path to the input CSV or Excel file containing tree species
            data.
            sheet_name: Name of the sheet to read from the Excel file (if applicable).
            taxon: Type of taxon to retrieve from the GBIF API (default is
            'speciesKey').
        """
        self.session = GBIF_SESSION
        self.input_path = input_path
        self.sheet_name = sheet_name
        self.taxon = taxon
        self.df: pd.DataFrame | None = None

    def load_data(self) -> pd.DataFrame:
        """
        Loads data from a CSV or Excel file into a pandas DataFrame.
        It checks the file extension to determine the format, reads the data,
        and processes it to ensure it contains the required columns.
        Returns:
            A DataFrame containing the processed tree species data.

        Raises:
            ValueError: If the input file is not in a supported format or if the
                required columns are missing.

                If no data is found in the input file.

                If the 'latin_name' column is not present in the DataFrame.
        """
        _, ext = os.path.splitext(self.input_path.lower())

        if ext == ".csv":
            self.df = pd.read_csv(self.input_path)
        elif ext in [".xls", ".xlsx"]:
            if self.sheet_name is None:
                logging.error("Sheet name must be provided for Excel files.")
                raise ValueError("Sheet name must be provided for Excel files.")

            self.df = pd.read_excel(self.input_path, sheet_name=self.sheet_name)
        else:
            logging.error("Unsupported file type: %s", ext)
            raise ValueError(f"Unsupported file format: {ext}")

        if self.df is None:
            logging.error("No data found for %s", self.input_path)
            raise ValueError(f"No data found for {self.input_path}")
        if "latin_name" not in self.df.columns:
            logging.error("The input file must contain a 'latin_name' column.")
            raise ValueError("The input file must contain a 'latin_name' column.")

        columns = ["latin_name"]

        self.df = self.df[columns].dropna(subset=["latin_name"])
        self.df["latin_name"] = self.df["latin_name"].str.strip().str.lower()

        self.df = self.df.drop_duplicates(subset="latin_name")

        return self.df

    def find_taxon_keys(self) -> pd.DataFrame:
        """
        Finds taxon keys for each Latin name in the DataFrame by querying the GBIF API.
        Failed requests are logged, and None is assigned to the taxon key if not found.
        Returns:
            The original DataFrame with an additional column for taxon
            keys.
        Raises:
            ValueError: If the DataFrame has not been loaded yet.
        """
        if self.df is None:
            logging.error("Data must be loaded first with `load_data()`.")
            raise ValueError("Data must be loaded first with `load_data()`.")

        taxon_keys: list[int | None] = []
        for latin_name in self.df["latin_name"]:
            url = f"https://api.gbif.org/v1/species/match?name={latin_name}"
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                key: int | None = data.get(self.taxon)
                if key is None:
                    logging.warning("TaxonKey not found for: %s", latin_name)
                    taxon_keys.append(None)
                elif not key:
                    logging.warning("No valid TaxonKey: %s", latin_name)
                    taxon_keys.append(None)
                else:
                    taxon_keys.append(key)
            except requests.RequestException as e:
                logging.error("Request failed for %s: %s", latin_name, e)
                taxon_keys.append(None)

        self.df[self.taxon] = taxon_keys
        self.df[self.taxon] = self.df[self.taxon].astype("Int64")
        return self.df

    def save(self, output_path: str):
        """
        Saves the DataFrame to a CSV file at the specified output path.
        Args:
            output_path: Path where the processed DataFrame will be saved as a CSV file.

        Raises:
            ValueError: If there is no data to save.
        """
        if self.df is not None:
            self.df.to_csv(output_path, index=False)
        else:
            logging.error("No data to save. Run load_data() first.")
            raise ValueError("No data to save. Run load_data() first.")

    def process_tree_list(self, output_path: str):
        """
        Processes the tree list by loading data, finding taxon keys, and saving the
        results.
        Args:
            output_path: Path where the processed DataFrame will be saved as a CSV file.
        """
        self.load_data()
        self.find_taxon_keys()
        self.save(output_path)
        logging.info("Tree list processed and saved to %s", output_path)
