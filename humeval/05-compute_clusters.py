# %%

import scipy.stats
import statistics
import numpy as np
import json
import os
import tqdm

os.makedirs("../generated/", exist_ok=True)
with open("../data/wmt25-genmt-humeval.jsonl", "r") as f:
    data = [json.loads(line) for line in f]

langs_all = {
    x["doc_id"].split("_#_")[0]
    for x in data
}

# %%

# paired t-test
cluster_count = 0
system_count = 0


def safe_average(l):
    return np.average([
        x for x in l if not np.isnan(x)
    ])


def get_significance(a: list[float], b: list[float]) -> bool:
    return scipy.stats.wilcoxon(
        [
            a-b
            for a, b in zip(a, b)
            if not (np.isnan(a) or np.isnan(b))
        ],
        alternative="greater",
    ).pvalue < 0.05
    # return scipy.stats.permutation_test(
    #     [[
    #         a-b
    #         for a, b in zip(a, b)
    #         if not (np.isnan(a) or np.isnan(b))
    #     ]],
    #     statistic=np.mean,
    #     n_resamples=1000,
    #     permutation_type="samples",
    #     alternative="greater",
    # ).pvalue < 0.05


with open("../generated/clusters.txt", "w") as f:
    for langs in tqdm.tqdm(langs_all):
        data_local = [
            x for x in data
            if x["doc_id"].startswith(langs + "_#_")
        ]

        # take all systems
        systems = {sys for x in data_local for sys in x["scores"].keys()}

        if not systems:
            continue

        # should be aligned
        systems = {
            sys: [
                # default to NaN but consider everything
                # flatten out human scores and treat them as two separate segments
                v["scores"].get(sys, {}).get(f"human{wave_i}", np.nan)
                for v in data_local
                for wave_i in [1, 2]

                # # average out scores
                # safe_average([
                #     v["scores"].get(sys, {}).get(f"human{wave_i}", np.nan)
                #     for wave_i in [1, 2]
                # ])
                # for v in data_local
            ]
            for sys in systems
        }
        # sort systems
        systems = sorted(
            systems.items(),
            key=lambda x: statistics.mean([a for a in x[1] if not np.isnan(a)]),
            reverse=True,
        )
        annotated_count = sum([
            ("human1" in x) + ("human2" in x)
            for l in data_local
            for x in l["scores"].values()
        ])
        if annotated_count < 500:
            continue
        print(
            langs.split("_")[0],
            annotated_count,
            file=f,
        )
        sys_v_prev = None
        for sys, sys_v in systems:
            if (
                sys_v_prev is not None and
                get_significance(sys_v_prev, sys_v)
            ):
                cluster_count += 1
                print(" "*10, "-"*15, file=f)
            print(
                f"{sys:>20}:",
                f"{statistics.mean([a for a in sys_v if not np.isnan(a)]):.1f}",
                file=f
            )
            sys_v_prev = sys_v

        print("\n", file=f)
        system_count += len(systems)

print(f"{system_count/cluster_count:.2f} models per cluster")

# %%

with open("../data/systems_humeval.json", "r") as f:
    systems_metadata = json.load(f)

def does_cluster_end_here(i, ranks) -> bool:
    ranks_below = ranks[:i]
    ranks_above = ranks[i:]
    return all([b <= i for a, b in ranks_below]) and all([a > i for a, b in ranks_above])

def system_name(s):
    if s == "refA":
        return "Human"
    else:
        return s.replace("_", r"\_")
    
def human_color(x):
    if x < 50:
        return "SeaGreen3!0!Firebrick3!50"
    else:
        x = x - 50
        x = min(50, x*1.2)
        return f"SeaGreen3!{x*2:.0f}!Firebrick3!50"

LANG_TO_LONG = {
    "it": "Italian",
    "ja": "Japanese",
    "sr": "Serbian (Cyrilic)",
    "uk": "Ukrainian",
    "ar": "Arabic (Egyptian)",
    "et": "Estonian",
    "mas": "Masai",
    "cs": "Czech",
    "de": "German",
    "zh": "Chinese",
    "ru": "Russian",
    "is": "Icelandic",
    "bho": "Bhojpuri",
    "en": "English",
}

with open("../generated/generated_human_ranking.tex", "w") as f:
    for langs in tqdm.tqdm(langs_all):
        data_local = [
            x for x in data
            if x["doc_id"].startswith(langs + "_#_")
        ]

        # take all systems
        systems = {sys for x in data_local for sys in x["scores"].keys()}

        if not systems:
            continue

        lang1, lang2 = langs.split("_")[0].split("-")
        print(r"""
\begin{table}
\centering
\small
\textbf{""",
        LANG_TO_LONG[lang1],
        r"$\rightarrow$",
        LANG_TO_LONG[lang2],
        r"}",
r"""
\begin{tabular}{C{8mm}L{30mm}C{9mm}C{10mm}}
Rank & System & Human & AutoRank \\
\midrule""",
        sep="",
        file=f)


        # should be aligned
        systems = {
            sys: [
                # default to NaN but consider everything
                # flatten out human scores and treat them as two separate segments
                v["scores"].get(sys, {}).get(f"human{wave_i}", np.nan)
                for v in data_local
                for wave_i in [1, 2]

                # # average out scores
                # safe_average([
                #     v["scores"].get(sys, {}).get(f"human{wave_i}", np.nan)
                #     for wave_i in [1, 2]
                # ])
                # for v in data_local
            ]
            for sys in systems
        }
        # sort systems
        systems = sorted(
            systems.items(),
            key=lambda x: statistics.mean([a for a in x[1] if not np.isnan(a)]),
            reverse=True,
        )

        systems_info = []
        for sysA_i, (sysA, sysA_v) in enumerate(systems):
            rank_start = sysA_i + 1
            rank_end = sysA_i + 1
            for sysB, sysB_v in systems[:sysA_i][::-1]:
                if get_significance(sysB_v, sysA_v):
                    break
                rank_start -= 1

            rank_end = sysA_i + 1
            for sysB, sysB_v in systems[sysA_i+1:]:
                if get_significance(sysA_v, sysB_v):
                    break
                rank_end += 1
            systems_info.append((
                sysA,
                np.mean([a for a in sysA_v if not np.isnan(a)]),
                (rank_start, rank_end),
            ))
        
        for sys_i, (sysA, sysA_mean, (rank_start, rank_end)) in enumerate(systems_info):
            mean_str = f"{sysA_mean:.1f}"
            mean_str = (r"\phantom{0}" * (4-len(mean_str))) + mean_str   

            if sysA == "refA":
                autorank_str = ""
            else:
                autorank_str = f"{systems_metadata[langs][sysA]['autorank']:.1f}"
                autorank_str = (r"\phantom{0}" * (4-len(autorank_str))) + autorank_str
            print(
                (
                    r"\constrained "
                    if sysA == "refA" or systems_metadata[langs][sysA]["constrained"] else
                    r"\unconstrained "
                ) +
                f"{rank_start}-{rank_end}",
                system_name(sysA),
                r"\cellcolor{" + human_color(sysA_mean) + r"} " + mean_str,
                r"\cellcolor{white} " + autorank_str,
                sep=" & ",
                end="\\\\\n",
                file=f,
            )
            if sys_i+1 != len(systems_info) and does_cluster_end_here(sys_i+1, [x[2] for x in systems_info]):
                print(r"\cmidrule{1-3}", file=f)
        
        print(
r"""\bottomrule
\end{tabular}
\end{table}
""",
            file=f,
        )

        print("\n"*2, file=f)