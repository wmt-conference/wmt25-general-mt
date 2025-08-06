# %%

import json
with open("../data/wmt25-genmt-humeval.jsonl", "r") as f:
    data = [json.loads(line) for line in f]

langs_all = {
    x["doc_id"].split("_#_")[0]
    for x in data
}

# %%
import collections
import statistics
import scipy.stats

# weak test

for langs in langs_all:
    data_local = [
        x for x in data
        if x["doc_id"].startswith(langs + "_#_")
    ]

    # consider systems with at least 10 annotations
    systems = collections.Counter([sys for x in data_local for sys in x["scores"].keys()])
    systems = {sys for sys, count in systems.items() if count >= 5}
    if not systems:
        continue

    systems = {
        sys: [
            v["scores"][sys]["human"] for v in data_local
            if sys in v["scores"]
        ]
        for sys in systems
    }
    # sort systems
    systems = sorted(systems.items(), key=lambda x: statistics.mean(x[1]), reverse=True)
    print(
        langs.split("_")[0],
        f"({sum([len(x["scores"]) for x in data_local])/sum([len(x["tgt_text"]) for x in data_local]):.1%})"
    )
    sys_v_prev = None
    for sys, sys_v in systems:
        if (
            sys_v_prev is not None and
            # Welch's independent t-test is not the strongest but right now 
            # we don't have all the values
            scipy.stats.ttest_ind(sys_v_prev, sys_v, equal_var=False)[1] < 0.10
        ):
            print(" "*10, "-"*15)
        print(f"{sys:>20}: {statistics.mean(sys_v):.1f}")
        sys_v_prev = sys_v
    
    print("\n")

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
    data_good = [x for x in data_local if set(x["scores"].keys()) == systems]

    if not data_good:
        continue

    # should be aligned
    systems = {
        sys: [
            v["scores"][sys]["human"]
            for v in data_good
        ]
        for sys in systems
    }
    # sort systems
    systems = sorted(systems.items(), key=lambda x: statistics.mean(x[1]), reverse=True)
    print(
        langs.split("_")[0],
        f"({len(data_good)/len(data_local):.1%})"
    )
    sys_v_prev = None
    for sys, sys_v in systems:
        if (
            sys_v_prev is not None and
            # paired t-test
            scipy.stats.ttest_rel(sys_v_prev, sys_v)[1] < 0.05
        ):
            print(" "*10, "-"*15)
        print(f"{sys:>20}: {statistics.mean(sys_v):.1f}")
        sys_v_prev = sys_v
    
    print("\n")