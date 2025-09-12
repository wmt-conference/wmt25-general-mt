# %%

import statistics
import numpy as np
import json
import os
import matplotlib.pyplot as plt
import collections

os.makedirs("../generated/", exist_ok=True)
with open("../data/wmt25-genmt-humeval.jsonl", "r") as f:
    data = [json.loads(line) for line in f]
    data = [x for x in data if x["scores"] != {}]

data_agg_topsys = []
data_agg_avgtgt = []
data_agg_toptgt = []

for lp in {x["doc_id"].split("_#_", 1)[0] for x in data}:
    data_local = [x for x in data if x["doc_id"].startswith(lp + "_#_")]
    
    # avg translation
    data_agg_avgtgt += [
        x
        for line in data
        for sys_v in line["scores"].values()
        for x in (
            ([sys_v["human1"]] if "human1" in sys_v else []) + 
            ([sys_v["human2"]] if "human2" in sys_v else [])
        )
    ]

    # best translation
    data_agg_toptgt += [
        max([
            statistics.mean(
                ([sys_v["human1"]] if "human1" in sys_v else []) + 
                ([sys_v["human2"]] if "human2" in sys_v else [])
            )
            for sys_v in line["scores"].values()
        ])
        for line in data
    ]

    # best system
    sys_avg = collections.defaultdict(list)
    for line in data_local:
        for sys, sys_v in line["scores"].items():
            sys_avg[sys] += (
                ([sys_v["human1"]] if "human1" in sys_v else []) + 
                ([sys_v["human2"]] if "human2" in sys_v else [])
            )
    sys_top = max(sys_avg.keys(), key=lambda k: statistics.mean(sys_avg[k]))
    data_agg_topsys += sys_avg[sys_top]


data_agg_toptgt = [x for x in data_agg_toptgt if not np.isnan(x)]

# %%

COLORS = [
    "#bc272d",  # red
    "#50ad9f",  # green
    "#0000a2",  # blue
    "#e0c016",  # yellow
    "#6a5371",  # purple
]
plt.rcParams["axes.prop_cycle"] = plt.cycler(color=COLORS)
plt.rcParams["font.family"] = "serif"

plt.figure(figsize=(3.5, 2))

bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
plt.hist(
    [data_agg_avgtgt, data_agg_topsys, data_agg_toptgt],
    bins=bins,
    density=True,
    label=["All", "Top system", "Top translation"],
)
plt.ylabel("Frequency")
plt.yticks([])
plt.xticks(bins)
plt.xlabel("ESA Score")
plt.gca().spines[["top", "right"]].set_visible(False)

handles = plt.gca().get_legend_handles_labels()
plt.tight_layout(pad=0.2)
plt.savefig("../generated/headroom.pdf")
plt.show()

# only legend
plt.figure(figsize=(3.5, 0.5))
plt.legend(
    *handles,
    loc="center",
    ncol=3,
    frameon=False,
    handletextpad=0.2,
    columnspacing=1.4,
)
# turn off axis
plt.gca().spines[["left", "top", "right", "bottom"]].set_visible(False)
plt.xticks([])
plt.yticks([])
plt.tight_layout(pad=0)
plt.savefig("../generated/headroom_legend.pdf")
plt.show()