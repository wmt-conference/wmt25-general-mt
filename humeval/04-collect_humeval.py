# %%
# load all data

import csv
import glob
import json
import itertools

data_csv = []
for fname in itertools.chain(
    glob.glob("/home/vilda/Downloads/campaign_results_v4/*.csv"),
    glob.glob("/home/vilda/Downloads/campaign_results_v5/*.csv")
):
    # we can drop the fname information as we can extract it from the document ids
    with open(fname, "r") as f:
        data_csv += list(csv.reader(f))

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

# %%

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
        "doc_id": v["doc_id"],
    } 
    for k, v in data.items()
    for i, src in enumerate(v["src_text"])
}

# %%

# find translations and other metadata
for line in data_csv:
    # ['engcesc401', 'cs-en-tutorial1', 'cs-en-tutorial1', 'TGT', 'eng', 'ces', '100', 'cs-en-tutorial1', 'False', '[]', '1754386211.242', '1754386211.242']
    account, model, sourceID, _, _, _, score, _, _, errors, time1, time2 = line
    if "tutorial" in sourceID:
        continue
    langs, domain, docid, segid = sourceID.split("_#_")
    mqm = json.loads(errors)
    for x in mqm:
        x.pop("error_type")
    data[sourceID]["scores"][model] = {"human": float(score), "errors": mqm, "annotator": account}

# save
with open("../data/wmt25-genmt-humeval.jsonl", "w") as f:
    f.writelines([json.dumps(x, ensure_ascii=False) + "\n" for x in data.values()])

# %%

"""
tar -czf data/TMP_Aug11-wmt25-genmt-humeval.jsonl.gz data/TMP_Aug11-wmt25-genmt-humeval.jsonl
"""