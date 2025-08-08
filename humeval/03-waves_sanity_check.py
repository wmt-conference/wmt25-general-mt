# %%

import glob
import json
import collections

# this should pass
for fname in glob.glob("../appraise/*wave1_tasks.json"):
# this should fail
# for fname in glob.glob("/home/vilda/Downloads/v4_wave1/appraise/*wave1_tasks.json"):
    with open(fname, "r") as f:
        data = [x["items"] for x in json.load(f)]
        # flatten
        data = [x for l in data for x in l if "-tutorial" not in x["targetID"]]
        check_len = collections.Counter([x["targetID"] for x in data]).most_common()

        check_sourceid = collections.defaultdict(set)
        for line in data:
            check_sourceid[line["targetID"]].add(line["sourceID"])

        print(
            len(check_len),
            # make sure all sytems have the same layout
            all(check_len[0][1] == x[1] for x in check_len),
            # make sure all sourceIDs are the same for each targetID
            all(list(check_sourceid.values())[0] == x for x in check_sourceid.values()),
            # check if refA is present
            "refA" in check_sourceid,
        )


# %%
import csv
import json

data_out = []

for fname in [
    "/home/vilda/Downloads/wmt25.wave1_v4.scores.2025-07-31/scores/wmt25engrusIliteraryIwave1v4.scores.csv",
    "/home/vilda/Downloads/wmt25.wave1_v4.scores.2025-07-31/scores/wmt25engrusIspeechIwave1v4.scores.csv",
    "/home/vilda/Downloads/wmt25.wave1_v4.scores.2025-07-31/scores/wmt25engukrIspeechIwave1v4.scores.csv",
]:
    with open(fname, "r") as f:
        data = list(csv.reader(f))
        # if len(data) < :
        #     continue
        data = [{"user": x[0], "sourceID": x[1], "targetID": x[2], "score": float(x[7]), "errors": json.loads(x[10])} for x in data]
        data_out += data

with open("../tmp/toloka_tmp.jsonl", "w") as f:
    # jsonl
    for line in data_out:
        f.write(json.dumps(line) + "\n")


# %%
import glob
import json
import collections
import itertools
# extract list of documents that are being annotated

data_out = collections.defaultdict(lambda: collections.defaultdict(set))
for fname in itertools.chain(
    glob.glob("../appraise_v5/*wave1_tasks.json"),
    glob.glob("../appraise_v4/wmt25engitaI*wave1_tasks.json"),
    glob.glob("../appraise_v5ma/wmt25engmasI*wave1v5_tasks.json"),
):
    with open(fname, "r") as f:
        data_local = json.load(f)
    data_local = [i for l in data_local for i in l["items"]]
    for item in data_local:
        doc_id = item["documentID"]
        if "tutorial" in doc_id:
            continue
        lp = doc_id.split("_#_")[0]
        data_out[lp][doc_id].add(item["targetID"])

with open("../tmp/sweta_v5.json", "w") as f:
    json.dump(
        {lp: {d: sorted(list(sys)) for d, sys in v.items()} for lp, v in data_out.items()},
        f,
        indent=2,
    )

data_out = collections.defaultdict(lambda: collections.defaultdict(set))
for fname in glob.glob("../appraise_v6/*wave2v6_tasks.json"):
    with open(fname, "r") as f:
        data_local = json.load(f)
    data_local = [i for l in data_local for i in l["items"]]
    for item in data_local:
        doc_id = item["documentID"]
        if "tutorial" in doc_id:
            continue
        lp = doc_id.split("_#_")[0]
        data_out[lp][doc_id].add(item["targetID"])

with open("../tmp/sweta_v6.json", "w") as f:
    json.dump(
        {lp: {d: sorted(list(sys)) for d, sys in v.items()} for lp, v in data_out.items()},
        f,
        indent=2,
    )

# %%
# check that the documents are the same between v5 and v6

with open("../tmp/sweta_v5.json", "r") as f:
    data_v5 = json.load(f)
with open("../tmp/sweta_v6.json", "r") as f:
    data_v6 = json.load(f)

print(set.symmetric_difference(set(data_v5.keys()), set(data_v6.keys())))

for lp in set.intersection(set(data_v5.keys()), set(data_v6.keys())):
    # document IDs are sorted
    if data_v5[lp] != data_v6[lp]:
        print(lp)
    assert data_v5[lp] == data_v6[lp], f"Mismatch in {lp}"
    print(len(data_v5[lp]), len(data_v6[lp]), data_v5[lp])


with open("../tmp/sweta_v6_simple.json", "w") as f:
    json.dump(
        {
            lp: {
                "docs": sorted(list(v.keys())),
                "systems": sorted(list(set.union(*map(set, v.values()))))
            }
            for lp, v in data_v6.items()
        },
        f,
        indent=2,
    )
# %%

"""
for f in appraise_v5/*wave1_tasks.json; do
    diff $f appraise_v6/$(basename $f);
done;
"""