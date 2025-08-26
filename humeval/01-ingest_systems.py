# %%
import pandas as pd
import json

# Load workbook once
xls = pd.ExcelFile("../data/autorank_v2.xlsx")

rows = []  # collect filtered rows from all sheets

for sheet in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet)

    # First column = system names (unnamed in the file)
    sys_col = df.columns[0]

    # Keep only rows where will_humeval is True (robust to strings like "TRUE", 1, etc.)
    mask = df["will_humeval"].astype(str).str.lower().isin(["true", "1", "yes", "y"])

    # Select relevant columns
    kept = df.loc[mask, [sys_col, "is_constrained", "autorank"]].assign(sheet=sheet)

    # Normalize column names
    kept.columns = ["system", "is_contrained", "autorank", "sheet"]
    rows.append(kept)

# Combine
result = pd.concat(rows, ignore_index=True)

data_out = {}

for sheet, group in result.groupby("sheet"):
    systems = group.dropna(subset=["system"])
    data_out[sheet] = {
        row["system"]: {
            "constrained": row["is_contrained"],
            "autorank": row["autorank"]
        }
        for _, row in systems.iterrows()
    }

# Save to JSON
with open("../data/systems_humeval.json", "w") as f:
    json.dump(data_out, f, indent=2)


# %%
# normalize previously-generated

with open("../data/systems_humeval_old.json", "r") as f:
    data_out = json.load(f)

data_out = {k: sorted(v) for k, v in data_out.items()}

with open("../data/systems_humeval_old.json", "w") as f:
    json.dump(data_out, f, indent=2)