# %%

import glob
import csv
import openpyxl
import collections

import openpyxl.cell

data_all = collections.defaultdict(list)
for f_name in sorted(glob.glob("/home/vilda/Downloads/wmt25.wave1_v3.accounts/accounts/*.csv")):
    langs, domain, wave = (
        f_name.split("/")[-1]
        .removeprefix("wmt25")
        .removesuffix("v3")
        .removesuffix(".csv")
        .split("I")
    )
    langs = langs[:3] + "-" + langs[3:]

    with open(f_name, "r") as f:
        data = [(x["URL"], x["ConfirmationToken"]) for x in csv.DictReader(f)]

    data_all[langs].append((domain, wave, data))

# %%
# create new worksheet
wb = openpyxl.Workbook()
# add new worksheet (not ws.active)

for langs, data_multi in data_all.items():
    ws = wb.create_sheet(langs)
    ws.append(["URL", "Token", "Domain", "Wave", "Notes"])
    for cell in ws["A1:E1"][0]:
        cell.font = openpyxl.styles.Font(bold=True)

    for domain, wave, data in data_multi:
        ws.append([])
        ws.append([
            f"https://appraise-wmt.azurewebsites.net/campaign-status/wmt25{langs.replace("-", "")}I{domain}I{wave}/",
            "status",
        ])
        # set background color
        ws[f"A{ws.max_row}"].fill = openpyxl.styles.PatternFill(start_color="edaa6f", end_color="edaa6f", fill_type="solid")


        for i, (url, token) in enumerate(data):
            ws.append([url, token, domain, wave])

wb.save("/home/vilda/Downloads/credentials_wave1.xlsx")
