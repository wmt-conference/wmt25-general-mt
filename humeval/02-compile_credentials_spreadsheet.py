# %%

import glob
import csv
import openpyxl
import collections

data_all = collections.defaultdict(list)
for f_name in sorted(glob.glob("/home/vilda/Downloads/wave1.credentials/*.csv")):
    langs, domain, wave = f_name.split("/")[-1].removeprefix("wmt25").removesuffix(".csv").split("I")
    langs = langs[:3] + "-" + langs[3:]

    with open(f_name, "r") as f:
        data = [x["URL"] for x in csv.DictReader(f)]

    data_all[langs].append((domain, wave, data))

# %%
# create new worksheet
wb = openpyxl.Workbook()
# add new worksheet (not ws.active)

for langs, data_multi in data_all.items():
    ws = wb.create_sheet(langs)
    ws.append(["URL", "Domain", "Wave", "Booked by", "Notes"])
    for cell in ws["A1:E1"][0]:
        cell.font = openpyxl.styles.Font(bold=True)

    for domain, wave, data in data_multi:
        for i, url in enumerate(data):
            ws.append([url, domain, wave])

wb.save("/home/vilda/Downloads/wmt25_credentials.xlsx")