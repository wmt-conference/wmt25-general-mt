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

with open("/home/vilda/Downloads/toloka_tmp.jsonl", "w") as f:
    # jsonl
    for line in data_out:
        f.write(json.dumps(line) + "\n")