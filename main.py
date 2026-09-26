from pathlib import Path

from configs.config import RAW_PATH,PROCESSED_PATH,DASHBOARD_DATA_PATH,SCRAPPER_TIMEOUT,SCRAPPER_URL

from scrapper.screener_scrapper import executor as scrape
from scrapper.table_parser import load_html, table_parser

from cleaning.cleaner import clean_all, save_tables

from validation.validator import validate_all

from cross_check.cross_check import executor as run_cross_check

from exporter.csv_to_json import export_all


#maps table names to the section IDs used by the Screener HTML page.
TABLE_SECTIONS = {
    "quarterly": "quarters",
    "profit_loss": "profit-loss",
    "balance_sheet": "balance-sheet",
    "cash_flow": "cash-flow",
    "ratios": "ratios",}


def get_raw_file() -> Path: #sorts all the files in the raw folder and gets the latest file, glob used to find file with.html, * signified any file

    raw_files = sorted(RAW_PATH.glob("*.html"))

    if not raw_files:
        raise FileNotFoundError(f"No raw HTML files found in {RAW_PATH}")

    return raw_files[-1]


def main():

    print("=" * 50)
    print("RELIANCE FINANCIAL DATA ETL PIPELINE")
    print("=" * 50)


   #Scrapper
    print("\n[1/6] SCRAPING SCREENER")

    scrape(SCRAPPER_URL,RAW_PATH,SCRAPPER_TIMEOUT)

    raw_file = get_raw_file()

    print(f"Raw file selected: {raw_file}")

    #parser

    print("\n[2/6] PARSING TABLES")

    html = load_html(raw_file)

    parsed_tables = {}

    for table_name,section_id in TABLE_SECTIONS.items():

        print(f"Parsing: {table_name}")

        parsed_tables[table_name] = table_parser(html,section_id)

        periods =parsed_tables[table_name]["periods"]
        rows =parsed_tables[table_name]["rows"]

        print(f"Periods found: {len(periods)}")
        print(f"Rows found: {len(rows)}")


    #cleaner

    print("\n[3/6] CLEANING DATA")

    cleaned_tables = clean_all(parsed_tables)

    save_tables(cleaned_tables,PROCESSED_PATH)

    #validator

    print("\n[4/6] VALIDATING DATA")

    validate_all(cleaned_tables)

    #cross_check with offical filing

    print("\n[5/6] Q1 FY27 CROSS-CHECK")

    run_cross_check()

    #json export

    print("\n[6/6] EXPORTING JSON")

    export_all(DASHBOARD_DATA_PATH,PROCESSED_PATH)


    print("\n" + "=" * 50)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 50)


if __name__ == "__main__":
    main()