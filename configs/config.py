import yaml
from pathlib import Path

BASE_PATH= Path(__file__).resolve().parent.parent

def load_config():
    CONFIG_PATH= BASE_PATH/"configs"/"configs.yaml"
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

configs= load_config()
DATA_PATH= BASE_PATH/configs["path"]["data_dir"]
DASHBOARD_PATH= BASE_PATH/configs["path"]["dashboard_dir"]
RAW_PATH= DATA_PATH/configs["path"]["raw_data"]
PROCESSED_PATH= DATA_PATH/configs["path"]["processed_data"]
DASHBOARD_DATA_PATH= DASHBOARD_PATH/configs["path"]["dashboard_data"]

SCRAPPER_TIMEOUT= configs["scrapper"]["timeout"]
SCRAPPER_RETRIES= configs["scrapper"]["retries"]
SCRAPPER_DELAY= configs["scrapper"]["delay"]
SCRAPPER_URL= configs["scrapper"]["url"]

SECTION_ID_QUARTERS= configs["scrapper"]["section_id"]["quarter"]
SECTION_ID_PROFIT_LOSS= configs["scrapper"]["section_id"]["profit&loss"]
SECTION_ID_BALANCE_SHEET= configs["scrapper"]["section_id"]["balance_sheet"]
SECTION_ID_CASH_FLOW= configs["scrapper"]["section_id"]["cash_flow"]
SECTION_ID_RATIOS= configs["scrapper"]["section_id"]["ratios"]

print(DASHBOARD_DATA_PATH)