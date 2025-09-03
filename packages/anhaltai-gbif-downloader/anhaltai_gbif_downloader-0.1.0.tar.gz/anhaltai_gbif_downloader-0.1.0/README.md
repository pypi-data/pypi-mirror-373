# 🌳 GBIF Image Downloader

This project automatically downloads taxon-specific images from the [GBIF API](https://techdocs.gbif.org/en/openapi/),
processes them, and stores both images and metadata in a taxonomically organized structure in a
[MinIO](https://www.min.io/) bucket.

---

## Features

- Loads Latin taxon names from `.csv` or `.xlsx` files
- Resolves `taxonKeys` automatically via the GBIF API
- Downloads associated media (images) from GBIF
- Stores metadata and images in a taxonomic folder structure in MinIO
- Optionally processes only new GBIF occurrences (`crawl_new_entries`)
- Multithreading for parallel processing and uploads
- Logging directly to MinIO

---

## Usage

## Installation

Install dependencies via:

```bash
pip install -r requirements.txt
```

---

### 1. Prepare your input file

Create a `.csv` or `.xlsx` file with at least the following column:

| latin_name      |
|-----------------|
| Quercus robur   |
| Fagus sylvatica |

### 2. Adjust your configuration

Edit the file `config/config.yaml` to set your MinIO connection, output paths, and processing options.  
A typical configuration looks like this:

```yaml
minio:
  bucket: meinewaldki-gbif         # Name of your MinIO bucket
  endpoint: s3.anhalt.ai           # MinIO/S3 endpoint URL
  secure: true                     # Use HTTPS (true/false)
  cert_check: true                 # Check SSL certificates (true/false)

paths:
  output: gbif-test/               # Output directory for images and metadata
  tree_list_input_path: data/tree_list.xlsx   # Path to your input taxon list
  processed_tree_list_path: data/species_key.csv # Path for the processed taxonKey list
  log_dir: logs/                   # Directory for log files

query_params:
  mediaType: StillImage            # Only download images
  limit: 100                       # Number of records per API call
  offset: 0                        # Start offset

options:
  already_preprocessed: True       # Set False to process the taxon list again
  crawl_new_entries: False         # Only process new occurrences if True
  max_threads: 10                  # Number of parallel threads for downloads/uploads
```

#### Query Parameters for GBIF API URL

The parameters used to build the GBIF API request URL are defined in the `query_params` section of your
`config/config.yaml`. These parameters control which records are fetched from the GBIF API.

**Supported parameters:**

- `mediaType` (e.g. `StillImage`): Only download records with images.
- `taxonKey`: The taxon key.
- `datasetKey`: Filter by dataset.
- `country`: Filter by country code (e.g. `DE` for Germany).
- `hasCoordinate`: Only records with coordinates (`true` or `false`).
- `year`, `month`: Filter by year or month of occurrence.
- `basisOfRecord`: Type of record (e.g. `HUMAN_OBSERVATION`).
- `recordedBy`: Filter by collector/observer.
- `institutionCode`, `collectionCode`: Filter by institution or collection.
- `limit`: Number of records per API call (pagination, max. 300).
- `offset`: Start offset for pagination.

**How it works:**

- All parameters in `query_params` are automatically validated at startup.
- Only the above parameters are allowed. Invalid parameters will cause the program to stop with an error.

### 3. Process taxonKey list and resolve taxonKeys

```python
from anhaltai.gbif_downloader.tree_list_processor import TreeListProcessor

processor = TreeListProcessor(input_path="data/tree_list.xlsx",
                              sheet_name="Gehölzarten", taxon="speciesKey")
processor.process_tree_list(output_path="data/species_key.csv")
```

### 4. Download media and metadata from GBIF

Run the main program:

```bash
PYTHONPATH=src python3 src/gbif_extractor/main.py
```

### Note:

- MinIO credentials must be set in `.env` see `.env-example` for the required format\.
- Log files are automatically uploaded to MinIO.
- Parallel processing and uploads are controlled by a configurable thread limit.
- Semaphores are used in this project to control the number of concurrent threads
  during uploads to MinIO.
- The program will skip old entries if `crawl_new_entries` is set to `True`.
