# %%
# load all data

import csv
import glob
import json
import itertools

data_csv = []
for fname in itertools.chain(
    glob.glob("/home/vilda/Downloads/campaign_results_v4/*.csv"),
    glob.glob("/home/vilda/Downloads/campaign_results_v5/*.csv"),
    glob.glob("/home/vilda/Downloads/campaign_results_v6/*.csv"),
):
    if "wave1" in fname:
        wave_i = 1
    elif "wave2" in fname:
        wave_i = 2
    else:
        raise ValueError(f"Unknown wave in {fname}")

    # only allow eng-ita from v4 (ask Zouhar for an explanation)
    if "_v4/" in fname and "engita" not in fname:
        continue

    # we can drop the fname information as we can extract it from the document ids
    with open(fname, "r") as f:
        data_csv += [(wave_i, x) for x in csv.reader(f)]

with open("../data/wmt25-genmt.jsonl", "r") as f:
    data = [json.loads(line) for line in f]

data = [
    {
        # contains the language and domain as well
        "doc_id": x["doc_id"],
        "domain": x["domain"],
        "src_lang": x["src_lang"],
        "tgt_lang": x["tgt_lang"],
        "src_text": x["src_text"].split("\n\n"),
        "video": x["video"],
        "screenshot": x["screenshot"],
        "tgt_text": {"refA": x["refs"]["refA"]["ref"].split("\n\n")} if len(x["refs"]) != 0 else {},
        "words": (
            len(x["src_text"].split())
            if x["src_lang"] not in {"zh_CN", "ko_KR", "ja_JP"} else
            len(x["src_text"]) // 2
        )
    }
    for x in data
]
data = {
    x["doc_id"]: x for x in data
}

with open("../data/systems_metadata.json", "r") as f:
    systems = json.load(f).keys()
for system in systems:
    with open(f"../data/systems/{system}.jsonl", "r") as f:
        data_sys = [json.loads(x) for x in f.readlines()]
        for doc in data_sys:
            if doc["doc_id"] not in data:
                continue
            data[doc["doc_id"]]["tgt_text"][system] = doc["hypothesis"].split("\n\n")


# Appraise treats <br> as a single character so make sure we do the same conversion so the error spans match
data = {
    k: x | {"tgt_text": {k: [b.replace("<br>", "\n").replace("</br>", "\n") for b in v] for k, v in x["tgt_text"].items()}}
    for k, x in data.items()
}

# flatten data

data = {
    f"{k}_#_{i}": {
        "scores": {},
        "src_text": src,
        "tgt_text": {sys: sys_v[i] for sys, sys_v in v["tgt_text"].items()},
        "doc_id": v["doc_id"] + f"_#_{i}",
    } 
    for k, v in data.items()
    for i, src in enumerate(v["src_text"])
}


# load and parse annotator mapping
import openpyxl
import collections
import utils
import re

R_ACCOUNT = re.compile(r"https://appraise-wmt\.azurewebsites\.net/dashboard/sso/([^/]+)/[^/]+/")

wb = openpyxl.load_workbook("/home/vilda/Downloads/credentials_wave1v5_wave2v6.xlsx", data_only=True, read_only=True)
account_to_annotator = collections.defaultdict(dict)
for langs in {x["doc_id"].split("_#_", 1)[0].split("_", 1)[0] for x in data.values()}:
    lang1, lang2 = langs.split("-")
    langs_3 = utils.LANG_TO_3.get(lang1, "") + "-" + utils.LANG_TO_3.get(lang2, "")
    if not langs_3 in wb:
        continue
    ws = wb[langs_3]
    for row in ws.iter_rows(min_row=2, values_only=True):
        if len(row) < 5:
            continue
        url = row[0]
        user = row[4]
        if user is None or url is None or not url.startswith("https://"):
            continue
        if isinstance(user, float):
            user = f"annotator{user}"
        if user == "":
            user = "unknown"
        account = R_ACCOUNT.match(url).group(1)
        account_to_annotator[langs][account] = user

    # uniform pseudoname format
    account_to_annotator_lang = account_to_annotator[langs]
    users = sorted(set(account_to_annotator_lang.values()))
    user_to_normalized = {u: f"{langs}_#_annotator{i+1}" for i, u in enumerate(users) if u != "unknown"}
    account_to_annotator[langs] = {
        k: user_to_normalized[v] for k, v in account_to_annotator_lang.items()
        if v != "unknown"
    }
account_to_annotator = dict(account_to_annotator)
with open("../data/account_to_annotator.json", "w") as f:
    json.dump(account_to_annotator, f, ensure_ascii=False, indent=2)


# find translations and other metadata
for wave_i, line in data_csv:
    account, model, sourceID, _, _, _, score, _, _, errors, time1, time2 = line
    if "tutorial" in sourceID:
        continue
    langs, domain, docid, segid = sourceID.split("_#_")
    langs_simple = langs.split("_", 1)[0]
    mqm = json.loads(errors)
    for x in mqm:
        x.pop("error_type")
    # add to the scores
    data[sourceID]["scores"][model] = (
        data[sourceID]["scores"].get(model, {})
        | {
            f"human{wave_i}": float(score),
            f"errors{wave_i}": mqm,
            f"annotator{wave_i}": account_to_annotator[langs_simple].get(account, "unknown"),
            f"times{wave_i}": [min(float(time1), float(time2)), max(float(time1), float(time2))],
        }
    )

# save
with open("../data/wmt25-genmt-humeval.jsonl", "w") as f:
    f.writelines([json.dumps(x, ensure_ascii=False) + "\n" for x in data.values()])

# %%

"""
cp data/wmt25-genmt-humeval.jsonl data/TMP_Sep20-wmt25-genmt-humeval.jsonl
tar -czf data/TMP_Sep20-wmt25-genmt-humeval.jsonl.gz data/TMP_Sep20-wmt25-genmt-humeval.jsonl
"""