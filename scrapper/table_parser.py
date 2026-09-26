from pathlib import Path
from bs4 import BeautifulSoup

def load_html(file_path: Path) -> str:
  return file_path.read_text(encoding="utf-8")#load raw html file from saved file

def find_table(html: str, section_id: str):
  
  soup=BeautifulSoup(html,"html.parser")# create soup object

  section= soup.find("section",id=section_id)
  if section is None:
    raise ValueError(f"Section {section_id} not found")

  table = section.find("table",class_="data-table")
  if table is None:
    raise ValueError(f"Table was not found in the section {section_id}")

  return table

def extract_periods(table):

  periods=[]

  header_cells=table.select("th[data-date-key]")#th-> header cell, [date-date-key  ] only selects the <th> elemetnst that contain [date-date-key] atribute

  for cell in header_cells:
    period=cell.get_text(strip=True)
    date_key= cell.get("data-date-key")
    periods.append({
      "period": period,
      "date": date_key
    }) 

  return periods

def extract_rows(table,periods):

  rows=[]
  body_rows=table.select("tbody tr") # select every <tr> in every<tbody>
  for row in body_rows:#loop through rows
    cells= row.find_all("td")

    if not cells:
      continue

    row_name= cells[0].get_text(" ",strip=True) #each row's first column is the row name
    values=[]

    for cell in cells[1:]: # all subsequent are values used
      values.append(cell.get_text(" ",strip=True))

    if len(values) != len(periods):
      raise ValueError(f"Period/Value mismach for row '{row_name}'."
                       f"Expected{len(periods)} values, found {len(values)}")

    row_data={
      "name": row_name,
      "values": values
    }
    rows.append(row_data)
  return rows

def table_parser(html: str,section_id: str):

    table= find_table(
      html,
      section_id
    )

    periods=extract_periods(table)

    rows=extract_rows(table,periods)

    return {
      "section" : section_id,
      "periods" : periods,
      "rows" : rows
    }
