import pandas as pd


EXPECTED_TABLES = {"quarterly","profit_loss","balance_sheet","cash_flow","ratios"}


def validate_expected_tables(cleaned_tables: dict) -> None:
    #checks weather all tables are present

    actual_tables = set(cleaned_tables.keys()) #takes all the keys of the icomingf dic

    missing_tables = EXPECTED_TABLES - actual_tables

    if missing_tables:
        raise ValueError(
            f"Missing expected tables: {missing_tables}"
        )
    else:
        print("PASS: All expected tables are present")

def validate_empty_table(df: pd.DataFrame,table_name: str) -> None:
    #checks if the table is empty or not
    if df.empty:
        raise ValueError(f"FAIL: Table '{table_name}' is empty")
    else:
        print(f"PASS: {table_name} is not empty")

def validate_periods(df: pd.DataFrame,table_name: str) -> None:
    #checks the period structure,also excludes the metric column

    period_columns = []
    for column in df.columns:
        if column != "metric":
            period_columns.append(column) #gets all the periods in the list

    if not period_columns:
        raise ValueError(f"FAIL: No period columns found in {table_name}") #checks if periods exist 

    if len(period_columns) != len(set(period_columns)):
        raise ValueError(f"FAIL: Duplicate periods found in {table_name}")  #checks for duplicates as sets cant habe duplicates and by converting before len it creates a distiction

    for period in period_columns:
        if not str(period).strip():
            raise ValueError(
                f"FAIL: Empty period found in {table_name}")

    print(f"PASS: Period structure valid for {table_name}")


def validate_metrics(df: pd.DataFrame,table_name: str) -> None:
    #Check metrics names for missing or duplicate values.

    if "metric" not in df.columns:
        raise ValueError(f"FAIL: 'metric' column missing in {table_name}") #raises error if metric not in column

    metrics = (df["metric"].dropna().astype(str).str.strip())

    if metrics.empty:
        raise ValueError(
            f"FAIL: No metrics found in {table_name}."
        )

    duplicate_metrics = (metrics[metrics.duplicated()].unique().tolist()) #checks for duplicates using unique and converts them to list using tolist 
    if duplicate_metrics:
        raise ValueError(
            f"FAIL: Duplicate metrics in {table_name}: "
            f"{duplicate_metrics}")#
    print(f"PASS: Metric structure valid for {table_name}") #if the list is empty then the metrics are not duplicated


def validate_numeric_values(df: pd.DataFrame,table_name: str) -> None:
    
    #Check that all metric rows contain numeric values in their period columns.
    #The Status row is excluded because it contains text.
    

    period_columns = []
    for column in df.columns:
        if column != "metric":
            period_columns.append(column) #everything exept metric considered period
    
    metric_rows = df[df["metric"] != "Status"] #removes status row by just choosing non-status rows

    for period in period_columns:
        non_numeric_values = pd.to_numeric(metric_rows[period],errors="coerce") #conberts values to numeric and text is converted to Nan

        invalid_values = (metric_rows[period].notna() & non_numeric_values.isna()) #checks for invalid values 

        if invalid_values.any():
            invalid_metrics = metric_rows.loc[invalid_values,"metric"].tolist()# selects invalid values and metric

            raise ValueError(
                f"FAIL: Non-numeric values found in "
                f"{table_name}, period '{period}', "
                f"metrics: {invalid_metrics}")
    print(f"PASS: Numeric values valid for {table_name}")

def validate_missing_values(df: pd.DataFrame,table_name: str) -> None:
    
    #Detect missing values in the cleaned table.
    #Missing values generate a warning rather than immediately failing the validation.
    

    period_columns = []
    for column in df.columns:
        if column != "metric":
            period_columns.append(column) #everything exept metric considered period
    
    metric_rows = df[df["metric"] != "Status"] 

    missing_count = metric_rows[period_columns].isna().sum().sum() #isna checks for each Nan value the first .sum sums for each row and last .sum sums the entire table 

    if missing_count > 0:
        print(f"WARNING: {table_name} contains {missing_count} missing value(s)")
    else:
        print(f"PASS: No missing values found in {table_name}")

def validate_status(
    df: pd.DataFrame,table_name: str) -> None:
    
    #Check the Status row created by the cleaner.

    status_rows = df[df["metric"] == "Status"]

    if status_rows.empty:
        print(f"WARNING: No Status row found in {table_name}") #check for no status row
        return

    if len(status_rows) > 1:
        raise ValueError(f"FAIL: Multiple Status rows found in {table_name}") #check for multi status rows


def validate_table(df: pd.DataFrame,table_name: str) -> None:
    
    #Run all validation checks for one table.
    
    print(f"\nValidating: {table_name}")

    validate_empty_table(df,table_name)
    validate_periods(df,table_name)
    validate_metrics(df,table_name)
    validate_numeric_values(df,table_name)
    validate_missing_values(df,table_name)
    validate_status(df,table_name)

def validate_all(cleaned_tables: dict) -> None:
    #Run validation on all cleaned tables.
    
    validate_expected_tables(cleaned_tables)
    for table_name, df in cleaned_tables.items():
        validate_table(df,table_name)
