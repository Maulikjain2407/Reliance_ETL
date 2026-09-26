import json
from pathlib import Path

import pandas as pd

#maps each processed csv to the JSON file for the dashboard
CSV_TO_JSON = {
    "quarterly.csv": "quarterly.json",
    "profit_loss.csv": "profit_loss.json",
    "balance_sheet.csv": "balance_sheet.json",
    "cash_flow.csv": "cash_flow.json",
    "ratios.csv": "ratios.json"}

def convert_value(raw_value, is_status): #is_status tells if the cell is that of status row, raw value is value from csv

    if (raw_value is None or (isinstance(raw_value, float) and pd.isna(raw_value))): # empty & NaN cells become None, shown as "-"
        return None

    text = str(raw_value).strip() #converts to string and strips whitespace
    if text == "" or text.lower() == "nan": #none for nil values
        return None

    if is_status:   #checks if current cell is status or normal
        return text

    number = float(text.replace(",",""))

    if number.is_integer():
        return int(number)

    return number


def csv_to_records(csv_path): #Reads one processed CSV and returns it as a list of row dicts

    df = pd.read_csv(csv_path)

    records = []
    for _, row in df.iterrows():
        metric_name = row.iloc[0] #get metric name
        status_row = str(metric_name).strip().lower() == "status" #checks if metric name status

        record = {"metric": metric_name} #creates dictionary for current row and loops through period columns, start from 1 since first is metric and rest are periods
        for column in df.columns[1:]:
            record[column] = convert_value(row[column],status_row)  #creates records

        records.append(record)

    return records


def export_all(dashboard_data,processed_data): #Converts every processed csv into its matching dashboard JSON file
    dashboard_data.mkdir(parents=True, exist_ok=True)

    for csv_name, json_name in CSV_TO_JSON.items():
        csv_path = processed_data/csv_name
        json_path = dashboard_data/ json_name

        if not csv_path.exists():
             raise FileNotFoundError(f"{csv_name}: not found at {csv_path}")

        records = csv_to_records(csv_path)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False) #indent fro readability and ensure_ascaii for unicode readability

        print(f"Wrote ({len(records)} rows)")