# %%

import pandas as pd
import json

# Load workbook once
xls = pd.ExcelFile("/home/vilda/Downloads/autorank_v2.xlsx")

rows = []  # collect filtered rows from all sheets

for sheet in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet)

    # First column = system names (unnamed in the file)
    sys_col = df.columns[0]

    # Keep only rows where will_humeval is True (robust to strings like "TRUE", 1, etc.)
    mask = df["will_humeval"].astype(str).str.lower().isin(["true", "1", "yes", "y"])
    kept = df.loc[mask, [sys_col]].assign(sheet=sheet)

    # Normalize column names
    kept.columns = ["system", "sheet"]
    rows.append(kept)

# Combine & print
result = pd.concat(rows, ignore_index=True)

data_out = {}

for sheet, systems in result.groupby("sheet")["system"]:
    data_out[sheet] = systems.dropna().tolist()

with open("../data/systems_humeval.json", "w") as f:
    json.dump(data_out, f, indent=2)