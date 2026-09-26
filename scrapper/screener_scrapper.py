import requests
from pathlib import Path
from datetime import datetime

def fetch_screener(url: str, timeout: int) -> str: #fetch screener page and return its html content
    headers= {
        "User-Agent" : "Maulik-Reliance_ETL"
    }
    response = requests.get(url,headers=headers,timeout=timeout)
    response.raise_for_status()

    return response.text

def save_raw_html(html: str, output_dir: Path) -> Path:

    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_file= output_dir/f"screener_reliance_{timestamp}.html"
    output_file.write_text(html,encoding="utf-8")

    return output_file

def executor(url: str, raw_path: Path, timeout:int):

    print("Fetching screener page...")
    content= fetch_screener(url,timeout)
    print(f"Downloaded {len(content):,} characters of HTML")
    output = save_raw_html(content,raw_path)
    print(f"Content saved to: {raw_path}")