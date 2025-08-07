# %%

import scipy.stats
import statistics
import numpy as np
import json
with open("../data/wmt25-genmt-humeval.jsonl", "r") as f:
    data = [json.loads(line) for line in f]

langs_all = {
    x["doc_id"].split("_#_")[0]
    for x in data
}

# %%

# paired t-test

for langs in langs_all:
    data_local = [
        x for x in data
        if x["doc_id"].startswith(langs + "_#_")
    ]

    # take all systems
    systems = {sys for x in data_local for sys in x["scores"].keys()}
    # take only segments with all data
    # data_good = [x for x in data_local if set(x["scores"].keys()) == systems]

    if not systems:
        continue

    # should be aligned
    systems = {
        sys: [
            # default to NaN but consider everything
            v["scores"].get(sys, {"human": np.nan})["human"]
            for v in data_local
        ]
        for sys in systems
    }
    # sort systems
    systems = sorted(
        systems.items(),
        key=lambda x: statistics.mean([a for a in x[1] if not np.isnan(a)]),
        reverse=True,
    )
    annotated_count = len([
        x for l in data_local for x in l["scores"].values()
        if not np.isnan(x["human"])
    ])
    if annotated_count < 1000:
        continue
    print(
        langs.split("_")[0],
        annotated_count
    )
    sys_v_prev = None
    for sys, sys_v in systems:
        if (
            sys_v_prev is not None and
            # paired t-test
            scipy.stats.ttest_rel(
                sys_v_prev, sys_v,
                # makes sure that comparisons are on the same segments
                nan_policy="omit",
                alternative="greater"
            )[1] < 0.05
        ):
            print(" "*10, "-"*15)
        print(
            f"{sys:>20}: {statistics.mean([a for a in sys_v if not np.isnan(a)]):.1f}")
        sys_v_prev = sys_v

    print("\n")
