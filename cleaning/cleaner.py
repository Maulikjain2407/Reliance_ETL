from pathlib import Path
import pandas as pd

def clean_table(table_data: dict, table_name: str):
    periods = table_data.get("periods",[]) # here the ,[] if no periods found returns []
    rows= table_data.get("rows",[])

    if not periods:
        raise ValueError(f"No periods for table {table_name}")
    if not rows:
        raise ValueError(f"No rows for table {table_name}")

    if table_name.lower() in {"quarterly","quarters"}: #label the frequency of the table
        frequency= "quarterly"
    else:
        frequency= "Annual"

    clean_data=[]

    # Create the period column names in the same order as Screener
    period_names = []

    for period in periods:

        period_name = str(period.get("period", "")).strip()

        if not period_name:
            raise ValueError(f"Missing period in table {table_name}")

        period_names.append(period_name)

    status_by_period = {}
    for period_name in period_names:
        status_by_period[period_name] = "Present" #creates a dictionary related to every period, may changes leter

    for row in rows:

        metric= row.get("name", "").strip()
        metric= metric.replace("+","").strip()

        if metric.lower() == "raw pdf":
            continue

        if not metric: # if metric name is empty we skip it, prevent blank rows
            continue

        values = row.get("values",[])

        # validation for values and periods
        # The number of values and periods has to be same
        # Only x number of periods can have x number of values not more not less
        # if any nan nil or otherwise value found cleaner cleans it later

        if len(values) != len(periods):
            raise ValueError(
                f"Period-Value mismatch in {table_name}"
                f"For metric: {metric}"
            )

        clean_row = {"metric": metric}

        for period,raw_value in zip(periods,values): #here zip is used to pair coresponding elements

            period_name = str(period.get("period", "")).strip()

            if raw_value is None:

                numeric_value= pd.NA
                status="Source_missing"

            else:

                value = str(raw_value).strip()

                if value in {"","-","—","NA","N/A"}:
                    numeric_value= pd.NA            #removal of nil values
                    status="Source_missing"

                else:
                    value = value.replace(",","")
                    value = value.replace("%", "")
                    value = value.strip()

                    try:
                        numeric_value = float(value)
                        status= "Present"

                    except ValueError:
                        numeric_value = pd.NA #exeption handling for in case screener give invalid value
                        status= "Cleaning_missing"
            clean_row[period_name] = numeric_value

            # Update the overall status for this period
            if status == "Cleaning_missing":

                status_by_period[period_name] = "Cleaning_missing"

            elif (
                status == "Source_missing"
                and status_by_period[period_name] == "Present"
            ):

                status_by_period[period_name] = "Source_missing"

        clean_data.append(clean_row)
    # Add the Status row after all metrics
    status_row = {"metric": "Status"}

    for period_name in period_names:
        status_row[period_name] = status_by_period[period_name]


    clean_data.append(status_row)
    #dataframe

    df=pd.DataFrame(clean_data)
    if df.empty:
        raise ValueError(
            f"Dataframe is empty for table {table_name}"
        )
    
    #Standardizing columns

    df = df[["metric"] + period_names] #keeping screener order

    #text

    df["metric"] = (df["metric"].astype("string").str.strip())

    #converting periods to numeric and keeping status as string

    status_mask = df["metric"] == "Status"

    for period in period_names:
        df.loc[~status_mask, period] = pd.to_numeric(            # basically checks if each metric is same as status
            df.loc[~status_mask, period],errors="coerce")        #~ selecs every row that is NOT status and converts them   
    #drop duplicates
    df=df.reset_index(drop=True)

    return df

def clean_all(parsed_tables: dict) -> dict: #cleans all tables
    
    cleaned_tables={}
    for table_name,table_data in parsed_tables.items(): #parsed_tables.items gives both key-value pair
        cleaned_tables[table_name]= clean_table(table_data,table_name)

    return cleaned_tables

def save_tables(cleaned_tables: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True,exist_ok=True)

    for table_name, dataframe in cleaned_tables.items():

        output_file=output_dir/f"{table_name}.csv"
        dataframe.to_csv(output_file,index=False)
        print(f"Saved: {output_file}")

def executor(parsed_tables: dict, output_dir: Path) ->None:

    cleaned_tables= clean_all(parsed_tables)
    save_tables(cleaned_tables,output_dir)