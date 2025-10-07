# %%
import json
import utils
import statistics
import collections
import scipy.stats
import itertools

with open("../data/wmt25-genmt-humeval.jsonl", "r") as f:
    data = [json.loads(line) for line in f]

with open("../data/wmt25-genmt-humeval_control.jsonl", "r") as f:
    data_ctrl = [json.loads(line) for line in f]

# %%
with open("../generated/humeval_overview.tex", "w") as f:

    print(
        r"\begin{tabular}{lccccccc}",
        r"\toprule",
        r"& \bf Annotations & \bf Ann./Sys. & \bf Time/Seg. & \bf Time/Word & \bf Minor/Major & \bf Annotators & \bf IAA \\",
        r"\midrule",
        file=f,
        sep="\n",
    )

    for langs in {x["doc_id"].split("_#_", 1)[0] for x in data}:
        lang1, lang2 = langs.split("_")[0].split("-")
        print(
            utils.LANG_TO_LONG[lang1],
            r"${\rightarrow}$",
            utils.LANG_TO_LONG[lang2],
            r"\hspace{-4mm}",
            sep="",
            file=f,
        )
        data_local = [x for x in data if x["doc_id"].startswith(langs + "_#_")]
        data_local_ctrl = [x for x in data_ctrl if x["doc_id"].startswith(langs + "_#_")]
        # total annotations
        annotations_total = len([
            None
            for line in data_local
            for sys_v in line["scores"].values()
            for k in sys_v
        ])
        systems_total = len({
            sys
            for line in data_local
            for sys in line["scores"].keys()
        })
        major_avg = statistics.mean([
            len([x for x in k["errors"] if x["severity"] != "major"])
            for line in data_local
            for sys_v in line["scores"].values()
            for k in sys_v
        ])
        minor_avg = statistics.mean([
            len([x for x in k["errors"] if x["severity"] != "minor"])
            for line in data_local
            for sys_v in line["scores"].values()
            for k in sys_v
        ])
        time_avg = statistics.mean([
            k["times"][1] - k["times"][0]
            for line in data_local
            for sys_v in line["scores"].values()
            for k in sys_v
        ])
        time_avg_srcword = statistics.mean([
            k["times"][1] - k["times"][0] / len(line["src_text"].split())
            for line in data_local
            for sys_v in line["scores"].values()
            for k in sys_v
        ])
        annotators = {
            k["annotator"]
            for line in data_local
            for sys_v in line["scores"].values()
            for k in sys_v
        }
        # print(list(data_local_ctrl[0]["scores"].values()))
        # print([d["annotator"] for d in data_local_ctrl[0]["scores"].values()])
        annotators_to_annotations = {
            annotator: [
                (line["doc_id"] + "_#_" + sys, d["human"])
                for line in data_local_ctrl
                for sys, sys_l in line["scores"].items()
                for d in sys_l if d["annotator"] == annotator
            ]
            for annotator in annotators
        }
        expected_length = collections.Counter([len(v) for v in annotators_to_annotations.values()]).most_common(1)[0][0]
        annotators_to_annotations = [
            [x[1] for x in sorted(v)]
            for v in annotators_to_annotations.values()
            if len(v) == expected_length
        ]
        if len(annotators_to_annotations) == 1:
            avg_iaa = float("nan")
        else:
            avg_iaa = statistics.mean([
                scipy.stats.pearsonr(v1, v2)[0]
                for v1, v2 in itertools.combinations(annotators_to_annotations, 2)
            ])

        print(
            "",
            f"{annotations_total:.0f}",
            f"{annotations_total/systems_total:.0f}",
            f"{time_avg:.1f}s",
            f"{time_avg_srcword:.1f}s",
            f"{major_avg:.1f}/{minor_avg:.1f}",
            f"{len(annotators):.0f}",
            f"{avg_iaa:.2f}",
            sep=" & ",
            end=" \\\\ \n",
            file=f,
        )
    print(
        r"\bottomrule",
        r"\end{tabular}",
        file=f,
        sep="\n",
    )
