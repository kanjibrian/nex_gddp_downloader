# NASA NEX-GDDP-CMIP6 Downloader

A high-performance downloader for the NASA NEX-GDDP-CMIP6 climate dataset.

## Features

- Parallel downloads (configurable worker count)
- Resume interrupted downloads via HTTP Range headers
- MD5 checksum verification
- Automatic retries with exponential backoff
- Progress bars (per-file and overall)
- Structured logging (console + file)
- Filtering by:
    - Variable (tas, pr, etc.)
    - Model (ACCESS-CM2, CanESM5, etc.)
    - Scenario (historical, ssp245, ssp585, etc.)
    - Ensemble (r1i1p1f1, etc.)
    - Year range
- Preserves NASA directory structure

## Usage

- Clone or download this repository into your local computer, and make the repository folder your working directory.

### Installation

```bash
pip install -r requirements.txt
```
### Configuration

Edit `settings.yml` to choose:

- **variables** — climate variables to download (e.g. `tas`, `pr`)
- **models** — CMIP6 models (e.g. `ACCESS-CM2`, `CanESM5`)
- **scenarios** — emission scenarios (e.g. `historical`, `ssp245`, `ssp585`)
- **ensembles** — ensemble members (e.g. `r1i1p1f1`)
- **years** — start / end year range
- **workers** — number of simultaneous downloads
- **download_directory** — where files are saved
- **verify_md5** — enable/disable MD5 verification
- **resume_downloads** — enable/disable download resumption

### Running

```bash
python main.py
```
- All downloads will be saved in the default download directory in this repository.

## Project Structure

```
nex_gddp_downloader/
├── main.py              # Entry point
├── config.py            # Settings loader
├── settings.yml         # Configuration file
├── requirements.txt     # Python dependencies
├── downloader/
│   ├── __init__.py
│   ├── models.py        # ClimateFile data model
│   ├── catalog.py       # Catalogue container with lookup
│   ├── index.py         # NASA CSV catalogue fetcher/parser
│   ├── filters.py       # Filter logic
│   ├── validators.py    # Selection validation & summary
│   ├── download.py      # Parallel download engine
│   ├── checksum.py      # MD5 verification
│   ├── retry.py         # Exponential backoff retry
│   ├── progress.py      # tqdm progress bars
│   ├── logger.py        # Logging setup
│   ├── utils.py         # Formatting helpers
│   └── exceptions.py    # Custom exceptions
├── downloads/           # Default output directory
├── logs/                # Log files
└── tests/               # Test suite
```
