# %%

import statistics
import numpy as np
import json
import os
import collections
import utils

os.makedirs("../generated/", exist_ok=True)
with open("../data/wmt25-genmt-humeval.jsonl", "r") as f:
    data = [json.loads(line) for line in f]
    data = [x for x in data if x["scores"] != {}]

DOMAINS = ['literary', 'speech', 'social', 'news']


def human_color(x):
    if np.isnan(x):
        return "white"
    x = max(0, min(100, (x-60)*3))
    return f"SeaGreen3!{x:.0f}!Firebrick3!50"


with open("../generated/domain_difficulty.tex", "w") as f:
    print(
        r"\begin{tabular}{lp{8mm}p{8mm}p{8mm}p{8mm}p{8mm}}",
        r"\toprule",
        sep="\n",
        file=f,
    )
    print(
        "", *[
            (
                r"\bf " + (
                    x.capitalize()
                    .replace("Literary", r"\hspace{-5mm} Literary")
                    .replace("Speech", r"\hspace{-2mm} Speech")
                )
            )
            for x in DOMAINS],
        r"\bf Avg. \\",
        sep=" & ",
        file=f,
    )
    print(
        r"\midrule",
        file=f,
    )
    for langs in {x["doc_id"].split("_#_", 1)[0] for x in data}:
        # domains = {x["doc_id"].split("_#_", 2)[1] for x in data_local}

        lang1, lang2 = langs.split("_")[0].split("-")
        print(
            utils.LANG_TO_LONG[lang1].replace(
                "English", "En.").replace("Czech", "Cz."),
            r"${\rightarrow}$",
            utils.LANG_TO_LONG[lang2].replace(
                "Egyptian", "Egy.").replace("Cyrilic", "Cyr."),
            " & ",
            sep="",
            file=f,
        )
        domain_scores = []
        for domain in DOMAINS:
            data_local = [x for x in data if x["doc_id"].startswith(
                langs + "_#_" + domain + "_#_")]
            if not data_local:
                print(" & ", end=" ", file=f)
                continue

            # find best system scores
            sys_avg = collections.defaultdict(list)
            for line in data_local:
                for sys, sys_v in line["scores"].items():
                    sys_avg[sys] += [sys_v[0]["score"], sys_v[1]["score"]]
            sys_top = max([statistics.mean(v) for v in sys_avg.values()])
            print(
                r"\cellcolor{" +
                human_color(sys_top) + r"}" + f"{sys_top:.1f} & ",
                end=" ",
                file=f,
            )
            domain_scores.append(sys_top)
        domain_scores = statistics.mean(domain_scores)
        print(
            r"\cellcolor{" + human_color(domain_scores) + r"}" +
            f"{domain_scores:.1f} \\\\",
            file=f,
        )
    print(
        r"\bottomrule",
        r"\end{tabular}",
        sep="\n",
        file=f,
    )
