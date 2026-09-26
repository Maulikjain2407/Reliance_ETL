# Reliance Industries Financial Data Pipeline

A reproducible Python-based ETL pipeline for collecting, parsing, cleaning, validating, and structuring consolidated financial data for **Reliance Industries Ltd.**

The project uses **Screener** as the primary data source and includes a cross-check against Reliance Industries Ltd.'s official **Q1 FY2026–27 Financial & Operational Performance** filing. A lightweight web dashboard presents the processed datasets.

---

## Table of Contents

- Project Overview
- Objectives
- Data Sources
- Pipeline Architecture
- Project Structure
- Data Collection
- Raw Data
- Cleaning and Structuring
- Processed Data
- Validation
- Q1 FY27 Cross-Check
- JSON Export
- Dashboard
- Installation
- Running the Pipeline
- Running the Dashboard
- Requirements
- Reproducibility
- Design Decisions
- Limitations
- Author

---

## Project Overview

This project was developed as a technical assessment focused on **financial data engineering and data quality**.

The pipeline follows a structured ETL workflow:

```text
Scraping
  ↓
Raw HTML
  ↓
Table Parsing
  ↓
Cleaning & Structuring
  ↓
Validation
  ↓
Q1 FY27 Cross-Check
  ↓
Processed CSV
  ↓
JSON Export
  ↓
Dashboard
```

The pipeline extracts and processes the following financial datasets:

- Quarterly Profit & Loss
- Annual Profit & Loss
- Balance Sheet
- Cash Flow
- Financial Ratios

The project separates data collection, transformation, validation, and presentation so that each stage can be inspected independently.

---

## Objectives

The pipeline is designed to:

- Systematically collect financial data from Screener.
- Preserve the original scraped HTML as raw data.
- Identify financial tables using their HTML structure rather than relying on fixed row or column positions.
- Correctly associate financial values with their corresponding reporting periods.
- Clean and standardize extracted values using Python and Pandas.
- Preserve numeric values, percentages, and missing values in a consistent format.
- Validate the extracted datasets before they are used downstream.
- Cross-check selected June 2026 values against Reliance Industries Ltd.'s official Q1 FY2026–27 filing.
- Export processed datasets into formats suitable for dashboard consumption.
- Provide a reproducible workflow that can be run from the project root.

---

## Data Sources

### Primary Source — Screener

The primary source for the financial datasets is the Screener page for Reliance Industries Ltd.

The scraper downloads the page HTML and stores it in the raw-data directory before parsing or cleaning takes place.

The following Screener sections are currently extracted:

| Dataset | Screener Section |
|---|---|
| Quarterly | `quarters` |
| Profit & Loss | `profit-loss` |
| Balance Sheet | `balance-sheet` |
| Cash Flow | `cash-flow` |
| Ratios | `ratios` |

The extracted data represents the consolidated financial information available through the selected Screener page.

### Official Source — Q1 FY2026–27 Cross-Check

Selected June 2026 quarterly values are cross-checked against Reliance Industries Ltd.'s official Q1 FY2026–27 Financial & Operational Performance filing.

The current cross-check covers:

- Gross Revenue
- Finance Costs
- Depreciation
- Profit Before Tax
- Profit After Tax

The purpose of the cross-check is to verify the extracted data against an authoritative company filing and identify differences where the two sources use different presentation, definitions, consolidation treatment, or rounding.

---

## Pipeline Architecture

```text
                         Screener
                            │
                            ▼
                  ┌──────────────────┐
                  │      Scraper     │
                  └────────┬─────────┘
                           │
                           ▼
                    data/raw/*.html
                           │
                           ▼
                  ┌──────────────────┐
                  │   Table Parser   │
                  └────────┬─────────┘
                           │
                           ▼
                     Parsed Tables
                           │
                           ▼
                  ┌──────────────────┐
                  │     Cleaner      │
                  └────────┬─────────┘
                           │
                           ▼
                 data/processed/*.csv
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       ┌─────────────┐          ┌─────────────┐
       │  Validator  │          │ Cross-Check │
       └─────────────┘          └──────┬──────┘
                                        │
                                        ▼
                                 Q1 FY27 Results
                                        │
                                        ▼
                                 ┌─────────────┐
                                 │ JSON Export │
                                 └──────┬──────┘
                                        │
                                        ▼
                             dashboard/data/*.json
                                        │
                                        ▼
                                   Dashboard
```

Each stage has a separate responsibility:

- **Scraping** — retrieves the source HTML.
- **Parsing** — identifies and extracts the required financial tables.
- **Cleaning** — converts the extracted information into structured datasets.
- **Validation** — checks the integrity and quality of the cleaned data.
- **Cross-checking** — compares selected quarterly values against the official filing.
- **Exporting** — converts processed CSV files into JSON datasets.
- **Dashboard** — displays the processed data.

---

## Project Structure

```text
Reliance_ETL/
│
├── configs/
│   ├── __init__.py
│   ├── config.py
│   └── configs.yaml
│
├── scrapper/
│   ├── __init__.py
│   ├── screener_scrapper.py
│   └── table_parser.py
│
├── cleaning/
│   └── cleaner.py
│
├── validation/
│   └── validator.py
│
├── cross_check/
│   └── cross_check.py
│
├── exporter/
│   └── csv_to_json.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── dashboard/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── data/
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

### Module Responsibilities

| Component | Responsibility |
|---|---|
| `configs/` | Central configuration and project paths |
| `scrapper/` | Downloads and parses Screener financial tables |
| `cleaning/` | Cleans and structures extracted data |
| `validation/` | Performs data-quality and structural checks |
| `cross_check/` | Performs the Q1 FY27 source cross-check |
| `exporter/` | Converts processed CSV files into dashboard JSON |
| `data/raw/` | Stores the original scraped HTML |
| `data/processed/` | Stores cleaned CSV datasets |
| `dashboard/` | Presents processed data through a web interface |
| `main.py` | Orchestrates the complete ETL pipeline |

---

## Data Collection

The data collection stage consists of two parts:

1. Downloading the Screener HTML.
2. Parsing the required financial tables from the downloaded HTML.

### HTML Retrieval

The scraper uses Python's `requests` library to retrieve the Screener page.

The request includes a custom User-Agent and a configurable request timeout.

The downloaded HTML is saved to:

```text
data/raw/
```

The raw HTML is retained before any cleaning or transformation takes place.

### Table Identification

The parser uses BeautifulSoup to inspect the downloaded HTML and locate the required financial sections.

Tables are identified using their section identifiers rather than relying on fixed row or column positions.

The current section mapping is:

```python
TABLE_SECTIONS = {
    "quarterly": "quarters",
    "profit_loss": "profit-loss",
    "balance_sheet": "balance-sheet",
    "cash_flow": "cash-flow",
    "ratios": "ratios",
}
```

### Period Extraction

Reporting periods are extracted from the table headers using the period metadata provided by the source HTML.

Each period is stored together with its corresponding source date key.

This allows the parser to associate each financial value with the correct reporting period.

### Row Extraction

For every table row, the parser extracts:

- Financial metric name
- Values corresponding to each reporting period

The parser verifies that the number of extracted values matches the number of identified periods.

If the number of values does not match the number of periods, the parser raises an error rather than silently producing misaligned data.

---

## Raw Data

Raw and processed data are kept separate.

The original scraped HTML is stored under:

```text
data/raw/
```

The raw file is preserved as an inspectable representation of the source page.

No cleaning or transformation is performed directly on the raw HTML.

The processed datasets are instead written to:

```text
data/processed/
```

This separation provides an audit trail between:

```text
Original Source
      ↓
Raw HTML
      ↓
Parsed Data
      ↓
Cleaned Data
```

The raw source therefore remains available for debugging, validation, or reprocessing if required.

---

## Cleaning and Structuring

The cleaning stage uses Pandas to convert the parsed table structures into structured datasets.

### Standardized Structure

Each processed dataset follows a wide format:

```text
metric | period_1 | period_2 | period_3 | ...
```

For example:

```text
metric,Jun 2025,Sep 2025,Dec 2025,Mar 2026,Jun 2026
Sales,450000,480000,500000,520000,530000
Expenses,400000,420000,440000,460000,470000
```

### Cleaning Operations

The cleaning stage handles:

- Leading and trailing whitespace
- HTML extraction artifacts
- Unnecessary `+` characters
- Commas in numeric values
- Percentage symbols
- Empty values: `-`, `—`, `NA`, `N/A`

Valid numeric values are converted into numeric Pandas types.

Decimal values are preserved rather than being unnecessarily converted to integers.

### Missing Values

Source-level missing values are represented using Pandas missing values.

The pipeline distinguishes between:

- `Present`
- `Source_missing`
- `Cleaning_missing`

This allows downstream validation to distinguish between a value that was absent from the source and a value that could not be converted during cleaning.

### Status Row

Each processed table contains a final Status row.

For example:

```text
metric,Mar 2025,Mar 2026
Sales,100000,120000
Operating Profit,20000,25000
Status,Present,Present
```

The status provides a period-level indication of whether the corresponding source data was present and successfully cleaned.

---

## Processed Data

The cleaning stage produces the following CSV files:

```text
data/processed/
├── quarterly.csv
├── profit_loss.csv
├── balance_sheet.csv
├── cash_flow.csv
├── ratios.csv
└── q1_fy27_crosscheck.csv
```

## Validation

Validation is performed after the cleaning stage and before the data is exported for dashboard use.

The validator is designed to fail or warn when problems are detected rather than silently accepting incomplete or malformed data.

### Expected Tables

The validator checks that all expected datasets are present:

- `quarterly`
- `profit_loss`
- `balance_sheet`
- `cash_flow`
- `ratios`

### Empty Dataset Check

Each processed dataset is checked to ensure that it is not empty.

### Period Validation

The validator checks that:

- Period columns exist.
- Period names are not empty.
- Duplicate period columns are not present.

### Metric Validation

The validator checks that:

- A metric column exists.
- At least one metric is present.
- Duplicate metric names are not present.

### Numeric Validation

Financial data columns are checked to ensure that non-missing values can be interpreted as numeric values.

Unexpected non-numeric values cause validation to fail.

### Missing-Value Validation

Missing values are counted and reported as warnings.

Missing source values do not automatically cause the pipeline to fail because financial datasets may legitimately contain periods where a source value is unavailable.

### Status Validation

The validator checks the Status row and accepts the following states:

- `Present`
- `Source_missing`
- `Cleaning_missing`

This ensures that the status information generated during cleaning remains consistent.

---

## Q1 FY27 Cross-Check

The pipeline includes a dedicated cross-check for the June 2026 quarter (Q1 FY2026–27).

Selected Screener values are compared with corresponding values from Reliance Industries Ltd.'s official financial filing.

### Metrics Compared

| Screener Metric | Official Metric |
|---|---|
| Sales | Gross Revenue |
| Interest | Finance Costs |
| Depreciation | Depreciation |
| Profit before tax | Profit Before Tax |
| Net Profit | Profit After Tax |

The comparison records:

- Screener value
- Official value
- Difference
- Comparison status

The output is stored as:

```text
data/processed/q1_fy27_crosscheck.csv
```

### Purpose

The cross-check is intended as a data-quality verification step, not as a financial-analysis exercise.

Differences between the two sources can occur because of:

- Different metric definitions
- Presentation differences
- Consolidation or reporting treatment
- Rounding
- Differences in how the source extracts or labels financial information

---

## JSON Export

The dashboard uses JSON files generated from the processed CSV datasets.

The exporter maps the processed files as follows:

| CSV | JSON |
|---|---|
| `quarterly.csv` | `quarterly.json` |
| `profit_loss.csv` | `profit_loss.json` |
| `balance_sheet.csv` | `balance_sheet.json` |
| `cash_flow.csv` | `cash_flow.json` |
| `ratios.csv` | `ratios.json` |

The JSON files are stored in:

```text
dashboard/data/
```

### Data Type Handling

The exporter preserves:

- Integers as integers
- Decimal values as floating-point numbers
- Missing values as JSON `null`
- Status values as strings

This keeps the dashboard data machine-readable while preserving the structure of the processed datasets.

---

## Dashboard

The project includes a lightweight web dashboard built using:

- HTML
- CSS
- JavaScript
- Chart.js

The dashboard presents the processed datasets without modifying the underlying financial data.

### Dashboard Sections

The interface contains:

- Overview
- Quarterly
- Profit & Loss
- Balance Sheet
- Cash Flow
- Ratios

### Dashboard Data Flow

The dashboard does not scrape Screener directly.

Instead, it consumes the JSON files generated by the ETL pipeline:

```text
Screener
    ↓
Python ETL Pipeline
    ↓
Processed CSV
    ↓
JSON Export
    ↓
dashboard/data/
    ↓
JavaScript fetch()
    ↓
Dashboard
```

This keeps the dashboard independent from the data collection process.

### Data Loading

The JavaScript application loads the datasets using `fetch()`.

Each dataset is loaded independently so that a failure in one dataset does not prevent the remaining datasets from being displayed.

Missing numeric values are displayed as `—`.

Status values are displayed using their corresponding status labels.

---

## Installation

### Prerequisites

- Python 3.10 or later
- Internet connection for retrieving the Screener page
- A modern web browser

### Clone the Repository

```bash
git clone https://github.com/Maulikjain2407/Reliance_ETL
cd Reliance_ETL
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Pipeline

Run the complete ETL pipeline from the project root:

```bash
python main.py
```

The pipeline executes the following stages:

```text
[1/6] Scraping Screener
[2/6] Parsing Tables
[3/6] Cleaning Data
[4/6] Validating Data
[5/6] Q1 FY27 Cross-Check
[6/6] Exporting JSON
```

On successful completion, the processed CSV files will be available in:

```text
data/processed/
```

and the dashboard JSON files will be available in:

```text
dashboard/data/
```

---

## Running the Dashboard

Because the dashboard loads JSON files using JavaScript `fetch()`, it should be served through a local HTTP server rather than opened directly as a file.

From the project root:

```bash
cd dashboard
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

The dashboard will load the JSON files from:

```text
dashboard/data/
```

---

## Requirements

The project dependencies are listed in `requirements.txt`.

The main Python libraries used by the pipeline are:

| Library | Purpose |
|---|---|
| `requests` | Retrieve the Screener page |
| `beautifulsoup4` | Parse HTML |
| `pandas` | Clean and structure financial data |
| `PyYAML` | Load project configuration |

---

## Reproducibility

The project is designed so that the complete workflow can be executed with minimal manual intervention.

The main pipeline is controlled through:

```text
main.py
```

Configuration values such as paths, timeout settings, retry settings, delay settings, and the Screener URL are maintained separately in:

```text
configs/configs.yaml
```

This avoids hard-coding environment-specific paths throughout the project.

The pipeline also performs validation before the processed datasets are passed to the dashboard export stage.

---

## Design Decisions

### Separation of Raw and Processed Data

Raw scraped HTML and cleaned datasets are stored separately.

This prevents the original source representation from being overwritten during cleaning.

### Structure-Based Parsing

The parser identifies tables through the structure of the Screener HTML rather than relying on fixed row numbers.

This makes the extraction logic more maintainable and reduces dependence on the exact ordering of financial rows.

### Validation Before Export

Validation occurs before JSON export.

This prevents the dashboard from becoming the first place where data-quality problems are discovered.

### Modular Architecture

Scraping, parsing, cleaning, validation, cross-checking, and exporting are implemented as separate modules.

This makes individual stages easier to test, debug, and maintain.

### Configuration Separation

Paths and scraper settings are maintained independently from the implementation code.

This allows configuration changes without modifying the individual pipeline modules.

### Data Presentation vs. Data Processing

The dashboard is treated as a presentation layer.

It consumes the JSON files generated by the pipeline rather than performing its own scraping or financial-data transformation.

This maintains a clear separation between the ETL pipeline and the user interface.

---

## Limitations

- The pipeline depends on the current HTML structure of the Screener page.
- Changes to Screener's page structure or section identifiers may require parser updates.
- The pipeline currently processes the financial sections explicitly defined in `TABLE_SECTIONS`.
- The Q1 FY27 cross-check covers selected metrics rather than every value in the quarterly dataset.
- The dashboard is intended for data presentation and inspection rather than advanced financial analysis.
- Internet access is required when retrieving the Screener source page.

---

## Author

**Maulik Jain**
B.Tech — Artificial Intelligence & Machine Learning
GitHub: [Maulikjain2407](https://github.com/Maulikjain2407)
