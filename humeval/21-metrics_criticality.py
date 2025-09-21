# %%

import json
import statistics

with open("../data/wmt25-genmt-humeval.jsonl", "r") as f:
    data = [json.loads(line) for line in f]
    data = [x for x in data if x["scores"] != {}]

for line in data:
    for sys_v in line["scores"].values():
        sys_v["human"] = statistics.mean(
            [sys_v["human1"]] if "human1" in sys_v else [] +
            [sys_v["human2"]] if "human2" in sys_v else []
        )

# %%
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "serif"

fig, axs = plt.subplots(2, 7, figsize=(9, 3))
for ax, langs in zip(axs.flatten(), {x["doc_id"].split("_#_", 1)[0] for x in data}):
    data_y = [
        sys_v.get("human1", sys_v["human"])
        for line in data if line["doc_id"].startswith(langs + "_#_")
        for sys_v in line["scores"].values()
    ]
    data_y_0 = [y for y in data_y if y < 10]
    data_y_1 = [y for y in data_y if y >= 10 and y < 90]
    data_y_2 = [y for y in data_y if y >= 90]
    ax.hist(
        data_y_0,
        bins=10,
        range=(0, 100),
        density=False,
        color="#c9a",
    )
    ax.hist(
        data_y_1,
        bins=10,
        range=(0, 100),
        density=False,
        color="#ccc",
    )
    ax.hist(
        data_y_2,
        bins=10,
        range=(0, 100),
        density=False,
        color="#9ca",
    )
    ax.set_yticks([])
    lang1, lang2 = langs.split("_")[0].split("-")
    ax.text(
        x=0.5,
        y=1,
        s=f"{lang1}-{lang2}",
        transform=ax.transAxes,
        ha="center",
        va="top",
    )
    if ax in axs[-1, :]:
        ax.set_xlabel("Score", labelpad=-10)
    else:
        ax.set_xticks([])
    if ax in axs[:, 0]:
        ax.set_ylabel("Density")
    ax.spines[["top", "right"]].set_visible(False)

plt.tight_layout(pad=0)
plt.subplots_adjust(hspace=0.1)
plt.savefig("../generated/humeval_distribution.pdf")
plt.show()

# %%

metrics = [metric for metric in data[0]["scores"]["Gemini-2.5-Pro"].keys() if metric not in {"human1", "human", "errors2", "errors1", "annotator1", "times1", "annotator2", "times2"}]

langs_all_0 = ["en-ar_EG", "en-bho_IN", "en-sr_Cyrl_RS", "en-et_EE", "en-is_IS", "en-ru_RU"]
langs_all_2 = list({x["doc_id"].split("_#_", 1)[0] for x in data})

def format_cell(acc):    
    # if score < 0.25:
    #     color = "Firebrick3!30"
    # else:
        # score = min(1, (score-0.25)/0.75)
    color = f"Firebrick3!{100-acc*100:.0f}!SeaGreen3!{acc*100:.0f}"
    return r"\cellcolor{" + color + "} " + f"{acc:>4.0%}".replace("%", r"\%")

with open("../generated/criticality_prediction_0.tex", "w") as f0:
    print(
        r"\begin{tabular}{l" + "r"*len(langs_all_0)+ r"}",
        r"\toprule",
        file=f0,
    )
    print(
        r"\bf Metric",
        *[r"\rotatebox{90}{\bf " + langs.split("_")[0] + "}" for langs in langs_all_0],
        sep=" & ",
        end=" \\\\\n",
        file=f0,
    )
    print(r"\midrule", file=f0)
    metrics_out = []
    for metric in metrics:
        metrics_out_local = []
        for langs in langs_all_0:
            acc_0 = []
            for human_gold, human_metric in [("human1", "human2"), ("human2", "human1")]:
                if metric.startswith("human"):
                    metric = human_metric
                data_yhum = [
                    (sys_v.get(human_gold, sys_v["human"]), (line["doc_id"], sys))
                    for line in data if line["doc_id"].startswith(langs + "_#_")
                    for sys, sys_v in line["scores"].items()
                ]
                data_ymet = [
                    (sys_v[metric], (line["doc_id"], sys))
                    for line in data if line["doc_id"].startswith(langs + "_#_")
                    for sys, sys_v in line["scores"].items() if metric in sys_v
                ]
                data_yhum_0 = {doc_id for y_hum, doc_id in data_yhum if y_hum < 10}
                # take the bottom or top, whichever is better
                data_ymet.sort(key=lambda x: x[0])
                data_ymet_0 = {doc_id for y_met, doc_id in data_ymet[:len(data_yhum_0)]}
                acc_bot = 2 * len(data_yhum_0 & data_ymet_0) / (len(data_yhum_0)+len(data_ymet_0))
                data_ymet_0 = {doc_id for y_met, doc_id in data_ymet[-len(data_yhum_0):]}
                acc_top = 2 * len(data_yhum_0 & data_ymet_0) / (len(data_yhum_0)+len(data_ymet_0))
                acc_0.append(max(acc_bot, acc_top))

            metrics_out_local.append(statistics.mean(acc_0))
        metrics_out.append((metric, metrics_out_local))
    
    for metric, metric_v in sorted(metrics_out, key=lambda x: -statistics.mean(x[1])):
        print(
            f"{metric:>20}".replace('_', r'\_').replace("human1", "Human"),
            file=f0,
        )
        for acc_0 in metric_v:
            print(f" & {format_cell(acc_0)}", end="", file=f0)

        print("\\\\", file=f0)

    print(
        r"\bottomrule",
        r"\end{tabular}",
        file=f0
    )