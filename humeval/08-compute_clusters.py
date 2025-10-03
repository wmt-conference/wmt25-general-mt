# %%

import scipy.stats
import statistics
import numpy as np
import json
import os
import tqdm
import utils

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


with open("../data/systems_humeval.json", "r") as f:
    systems_metadata_humeval = json.load(f)
    systems_metadata_humeval_not = {
        lang: {sys: d for sys, d in vals.items() if not d["will_humeval"]}
        for lang, vals in systems_metadata_humeval.items()
    }
    systems_metadata_humeval = {
        lang: {sys: d for sys, d in vals.items() if d["will_humeval"]}
        for lang, vals in systems_metadata_humeval.items()
    }

with open("../data/systems_metadata_updated3.json", "r") as f:
    systems_metadata = json.load(f)

def does_cluster_end_here(i, ranks) -> bool:
    ranks_below = ranks[:i]
    ranks_above = ranks[i:]
    return all([b <= i for a, b in ranks_below]) and all([a > i for a, b in ranks_above])

def system_name(sys):
    return {
        "CommandA-MT": "CommandA-WMT",
        "Shy": "Shy-hunyuan-MT",
        "TowerPlus-9B": "TowerPlus-9B[M]",
        "TowerPlus-72B": "TowerPlus-72B[M]",
        "EuroLLM-9B": "EuroLLM-9B[M]",
        "EuroLLM-22B": "EuroLLM-22B-pre.[M]",
        "RuZH": "RuZH-Eole",
        "refA": r"\textbf{Human}",
    }.get(sys, sys).replace("_", r"\_")


def system_unsupported(sys, langs):
    if sys == "refA":
        return " "
    elif systems_metadata[sys]["supported_lps"][langs] == "supported":
        return " "
    elif systems_metadata[sys]["supported_lps"][langs] == "unknown":
        return r"\unsupportedmaybe "
    else:
        return r"\unsupported "
    
def human_color(x):
    if np.isnan(x):
        return "white"
    if x < 50:
        return "SeaGreen3!0!Firebrick3!50"
    else:
        x = x - 50
        x = min(50, x*1.2)
        return f"SeaGreen3!{x*2:.0f}!Firebrick3!50"



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
        utils.LANG_TO_LONG[lang1],
        r"$\rightarrow$",
        utils.LANG_TO_LONG[lang2],
        r"} \\",
r"""
\begin{tabular}{C{8mm}L{31mm}C{9mm}C{10mm}""" + "".join(["C{8mm}" for _ in domains]) + r"""}
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
                autorank_str = f"{systems_metadata_humeval[langs][sysA]['autorank']:.1f}"
                autorank_str = (r"\phantom{0}" * (4-len(autorank_str))) + autorank_str
            rank_start = (r"\phantom{0}" * (2-len(str(rank_start)))) + str(rank_start)
            rank_end = str(rank_end) + (r"\phantom{0}" * (2-len(str(rank_end))))
            
            print(
                f"{rank_start}-{rank_end}",
                (
                    r"\constrained{"
                    if sysA == "refA" or systems_metadata_humeval[langs][sysA]["constrained"] else
                    r"\unconstrained{"
                ) +
                system_name(sysA) + "}" + system_unsupported(sysA, langs),
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
        
        print(r"\cmidrule{1-3}", file=f)
        print(
            r"\textcolor{black!60}{" + f"{sys_i+2}-{sys_i+2+len(systems_metadata_humeval_not[langs])}" + r"}",
            r"\multicolumn{2}{l}{\textcolor{black!50}{\constrained{" + f"{len(systems_metadata_humeval_not[langs])} systems not human-evaluated" + r"}}}",
            r"\textcolor{black!50}{...}",
            sep=" & ",
            end="\\\\\n",
            file=f,
        )

        print(
            r"\bottomrule",
            r"\end{tabular}\vspace{-2mm}",
            r"\end{table}",
            sep="\n",
            file=f,
        )

        print("\n"*2, file=f)



# % manual intervention for alignment
# \begin{table}
# \vspace{7.7cm}
# \end{table}

# go through the extended version and just clip the specific lines

with open("../generated/generated_human_ranking_ext.tex", "r") as f:
    text_ext = f.read().split("\n")

with open("../generated/generated_human_ranking.tex", "w") as f:
    text_base = ""
    for line in text_ext:
        if line.startswith(r"\begin{tabular}{C{8mm}L{31mm}C{9mm}C{10mm}"):
            line = r"\begin{tabular}{C{8mm}L{31mm}C{9mm}C{10mm}}"
            text_base += line + "\n"
        elif line.startswith(r"\textcolor{"):
            text_base += line + "\n"
        elif line.count("&") >= 2:
            line = "&".join(line.split("&")[:4]) + r" \\"
            text_base += line + "\n"
        else:
            text_base += line + "\n"
        
    f.write(text_base)