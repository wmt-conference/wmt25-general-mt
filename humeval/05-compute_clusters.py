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

def get_significance(a: list[float], b: list[float]) -> bool:
    assert len(b) % 2 == 0
    # wave1, wave2, wave1, wave2
    a = a + a
    # wave1, wave2, wave2, wave1
    b = b + b[len(b)//2:] + b[:len(b)//2]
    assert len(a) == len(b)
    return scipy.stats.wilcoxon(
        [
            a-b
            for a, b in zip(a, b)
            if not (np.isnan(a) or np.isnan(b))
        ],
        alternative="greater",
    ).pvalue < 0.05/2


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
                print(" "*10, "-"*15, file=f)
            print(
                f"{sys:>20}:",
                f"{statistics.mean([a for a in sys_v if not np.isnan(a)]):.1f}",
                file=f
            )
            sys_v_prev = sys_v

        print("\n", file=f)


# %%

with open("../data/systems_humeval.json", "r") as f:
    systems_metadata = json.load(f)

def does_cluster_end_here(i, ranks) -> bool:
    ranks_below = ranks[:i]
    ranks_above = ranks[i:]
    return all([b <= i for a, b in ranks_below]) and all([a > i for a, b in ranks_above])

def system_name(s):
    return {
        "CommandA-MT": "CommandA-WMT",
        "Shy": "Shy-hunyuan-MT",
        "TowerPlus-9B": "TowerPlus-9B[M]",
        "TowerPlus-72B": "TowerPlus-72B[M]",
        "EuroLLM-9B": "EuroLLM-9B[M]",
        "EuroLLM-22B": "EuroLLM-22B-pre.[M]",
        "RuZH": "RuZH-Eole",
        "refA": r"Human $\bullet$",
    }.get(s, s).replace("_", r"\_")
    
def human_color(x):
    if np.isnan(x):
        return "white"
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

with open("../generated/generated_human_ranking_ext.tex", "w") as f:
    for langs in tqdm.tqdm(langs_all):
        data_local = [
            x for x in data
            if x["doc_id"].startswith(langs + "_#_")
        ]
        domains = sorted({x["doc_id"].split("_#_")[1] for x in data_local})

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
        r"} \\",
r"""
\begin{tabular}{C{8mm}L{29mm}C{9mm}C{10mm}""" + "".join(["C{8mm}" for _ in domains]) + r"""}
Rank & System & Human & AutoRank & """ + " & ".join(domains) + r""" \\
\midrule""",
        sep="",
        file=f)


        # should be aligned
        systems = {
            sys: [
                # default to NaN but consider everything
                # flatten out human scores and treat them as two separate segments
                v["scores"].get(sys, {}).get(f"human{wave_i}", np.nan)
                for wave_i in [1, 2]
                for v in data_local
            ]
            for sys in systems
        }
        domain_names = [
            v["doc_id"].split("_#_")[1]
            for _wave_i in [1, 2]
            for v in data_local
        ]
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
                {
                    domain: np.mean([x for x, d in zip(sysA_v, domain_names) if d == domain and not np.isnan(x)])
                    for domain in domains
                },
                (rank_start, rank_end),
            ))
        
        for sys_i, (sysA, sysA_mean, sysA_domains, (rank_start, rank_end)) in enumerate(systems_info):
            mean_str = f"{sysA_mean:.1f}"
            mean_str = (r"\phantom{0}" * (4-len(mean_str))) + mean_str   

            if sysA == "refA":
                autorank_str = ""
            else:
                autorank_str = f"{systems_metadata[langs][sysA]['autorank']:.1f}"
                autorank_str = (r"\phantom{0}" * (4-len(autorank_str))) + autorank_str
            rank_start = (r"\phantom{0}" * (2-len(str(rank_start)))) + str(rank_start)
            rank_end = str(rank_end) + (r"\phantom{0}" * (2-len(str(rank_end))))
            
            print(
                f"{rank_start}-{rank_end}",
                (
                    r"{"
                    if sysA == "refA" or systems_metadata[langs][sysA]["constrained"] else
                    r"\hlc[gray!20]{"
                ) +
                system_name(sysA) + "}",
                r"\cellcolor{" + human_color(sysA_mean) + r"} " + mean_str,
                r"\cellcolor{white} " + autorank_str,
                *[
                    r"\cellcolor{" + human_color(sysA_domains[domain]) + r"} " + f"{sysA_domains[domain]:.1f}"
                    for domain in domains
                ],
                sep=" & ",
                end="\\\\\n",
                file=f,
            )
            if sys_i+1 != len(systems_info) and does_cluster_end_here(sys_i+1, [x[3] for x in systems_info]):
                print(r"\cmidrule{1-3}", file=f)
        
        print(
            r"\bottomrule",
            r"\end{tabular}",
            # make sure each table has the same height
            # r"\vspace{" + f"{(20-len(systems))*1.8:.1f}" + r"em}",
            r"\end{table}",
            sep="\n",
            file=f,
        )

        print("\n"*2, file=f)



# go through the extended version and just clip the specific lines

with open("../generated/generated_human_ranking_ext.tex", "r") as f:
    text_ext = f.read().split("\n")

with open("../generated/generated_human_ranking.tex", "w") as f:
    text_base = ""
    for line in text_ext:
        if line.startswith(r"\begin{tabular}{C{8mm}L{29mm}C{9mm}C{10mm}"):
            line = r"\begin{tabular}{C{8mm}L{29mm}C{9mm}C{10mm}}"
        elif line.count("&") >= 2:
            line = "&".join(line.split("&")[:4]) + r" \\"
        
        text_base += line + "\n"
    f.write(text_base)