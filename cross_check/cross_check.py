import pandas as pd

from configs.config import PROCESSED_PATH

PERIOD = "Jun 2026"

#Official Reliance Q1 FY27 consolidated filing values
OFFICIAL_VALUES = {
    "Gross Revenue": 340257,
    "Finance Costs": 7036,
    "Depreciation": 15100,
    "Profit Before Tax": 30630,
    "Profit After Tax": 23001,
}


#Mapping between Screener metric names and the corresponding official filing terms
METRIC_MAPPING = {
    "Sales": "Gross Revenue",
    "Interest": "Finance Costs",
    "Depreciation": "Depreciation",
    "Profit before tax": "Profit Before Tax",
    "Net Profit": "Profit After Tax",
}


def load_screener_data():

    file_path = PROCESSED_PATH / "quarterly.csv"
    if not file_path.exists():
        raise FileNotFoundError(f"Screener file not found: {file_path}")
    df = pd.read_csv(file_path)

    return df


def get_screener_value(df,metric,period): #retrives one specifc value from screener df

    matching_rows = df[df["metric"] == metric] #checks each row and only selects one row
    if matching_rows.empty:
        raise ValueError(f"Metric '{metric}' not found in Screener data")
    if len(matching_rows) > 1:
        raise ValueError(f"Duplicate metric '{metric}' found")

    value=matching_rows.iloc[0][period] #brings the actual value of the metric by choosing the correct value from the periods and metric

    try:
        return float(value)
    except(ValueError,TypeError):
        raise ValueError(f"Non-numeric value found for {metric} in period {period}: {value}")


def compare_values(screener_value,official_value):

    if pd.isna(screener_value):
        return "Missing"
    if screener_value == official_value:
        return "Match"

    return "Difference"   #checks if there is a difference or not and returns the status


def cross_check(df):

    results = []
    for screener_metric, official_metric in METRIC_MAPPING.items(): #gets the key and value pair  where the screener names is the key and the official metric the value
        screener_value = get_screener_value(df,screener_metric,PERIOD)

        official_value = OFFICIAL_VALUES[official_metric]

        status = compare_values(screener_value,official_value)

        if pd.isna(screener_value):
            difference = pd.NA
        else:
            difference = (screener_value - official_value) #tells the difference between the values if any

        results.append({
            "metric": screener_metric,
            "official_metric": official_metric,
            "period": PERIOD,
            "screener_value": screener_value,
            "official_value": official_value,
            "difference": difference,
            "status": status})

    return pd.DataFrame(results)


def save_cross_check(results):

    output_file = (PROCESSED_PATH/ "q1_fy27_crosscheck.csv")
    results.to_csv(output_file,index=False)
    print(f"Saved: {output_file}")


def executor():

    screener_data = load_screener_data()
    results = cross_check(screener_data)
    print("\nQ1 FY27 CROSS-CHECK")
    print(results)
    save_cross_check(results)