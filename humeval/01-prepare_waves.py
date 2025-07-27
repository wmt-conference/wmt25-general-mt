# %%

import json
import pathlib
import contextlib
import collections

LANGS = {
    "en-cs_CZ", "cs-uk_UA", "cs-de_DE", "en-et_EE", "en-is_IS", "en-ja_JP", "en-ar_EG", "en-sr_Cyrl_RS",
    "en-ru_RU", "en-uk_UA", "en-zh_CN", "en-it_IT",
    # "en-bho_IN", "en-mas_KE": come later
    # TODO: make sure that CAMPAIGN_NO here is correct

    # not used
    # "en-sr_Latn_RS", # for Serbian we use Cyrillic only
    # en-de_DE is not done this year
    # ja-zh_CN is done by Google
    # en-ko_KR is done by Google
}
LANG_TO_3 = {
    "en": "eng",
    "cs": "ces",
    "uk": "ukr",
    "de": "deu",
    "et": "est",
    "is": "isl",
    "ja": "jpn",
    "zh": "zho",
    "ar": "ara",
    "sr": "srp",
    "ru": "rus",
    "ko": "kor",
    "bho": "bho",
    "mas": "mas",
    "it": "ita",
}

with contextlib.chdir(pathlib.Path(__file__).parent.parent):
    with open("data/systems_humeval.json", "r") as f:
        systems_humeval = json.load(f)

    with open("data/wmt25-genmt.jsonl", "r") as f:
        data = [json.loads(x) for x in f.readlines()]
    # take only the information we need
    data = [
        {
            # contains the language and domain as well
            "doc_id": x["doc_id"],
            "domain": x["domain"],
            "src_lang": x["src_lang"],
            "tgt_lang": x["tgt_lang"],
            "src_text": x["src_text"].split("\n\n"),
            "video": x["video"],
            "screenshot": x["screenshot"],
            "tgt_text": {"refA": x["refs"]["refA"]["ref"].split("\n\n")} if len(x["refs"]) != 0 else {},
            "words": (
                len(x["src_text"].split())
                if x["src_lang"] not in {"zh_CN", "ko_KR", "ja_JP"} else
                len(x["src_text"]) // 2
            )
        }
        for x in data
        if x["src_lang"]+"-"+x["tgt_lang"] in LANGS
    ]
    assert len({x["doc_id"] for x in data}) == len(data), "Duplicates found in data"
    print(f"Loaded {len(data)} documents from WMT25 general collection")
    data = {
        x["doc_id"]: x for x in data
    }

    langs_omitted = set()

    # load translations
    with open("data/systems_metadata.json", "r") as f:
        systems = json.load(f).keys()
    for system in systems:
        sys_f = f"data/systems/{system}.jsonl"

        with open(sys_f, "r") as f:
            data_sys = [json.loads(x) for x in f.readlines()]
            for doc in data_sys:
                if doc["doc_id"] not in data:
                    langs_omitted.add(doc["doc_id"].split("_#_")[0])
                    continue
                data[doc["doc_id"]]["tgt_text"][system] = doc["hypothesis"].split("\n\n")

    print("Skipped document from following languages", langs_omitted)

    for doc in data.values():
        for system, tgt_text in doc["tgt_text"].items():
            # make sure all systems have the same number of segments
            assert len(doc["src_text"]) == len(tgt_text), (
                f"Document {doc['doc_id']} has different number of segments "
                f"({len(doc['src_text'])} vs {len(tgt_text)}) for system {system}"
            )

# %%

# treat each lang separatedly
data_agg = collections.defaultdict(list)
for doc in data.values():
    data_agg[(doc["src_lang"], doc["tgt_lang"])].append(doc)

for langs, data_local in data_agg.items():
    systems = set(data_local[0]["tgt_text"].keys())
    # make sure we have system translations for all
    for doc in data_local:
        assert set(doc["tgt_text"].keys()) == systems
    
    print(langs, len(systems))

    # sorted to make random selection robust
    systems = sorted(systems_humeval[f"{langs[0]}-{langs[1]}"])
    for doc in data_local:
        doc["tgt_text"] = {
            sys: doc["tgt_text"][sys]
            for sys in systems
        }

# flatten again
data = {doc["doc_id"] : doc for l in data_agg.values() for doc in l}

# %%
import fastchrf
import numpy as np
import statistics
import itertools

# treat each lang + domain separatedly
data_agg = collections.defaultdict(list)
for doc in data.values():
    data_agg[(doc["src_lang"], doc["tgt_lang"], doc["domain"])].append(doc)

data_agg_new = {}

prev_lang = None
for batch_name, data_local in data_agg.items():
    if prev_lang is not None and prev_lang != batch_name[:2]:
        print()
    prev_lang = batch_name[:2]

    diversity = [
        # statistics.mean([
        #     docA != docB
        #     for sysA, sysB in itertools.combinations(doc["tgt_text"].keys(), 2)
        #     for docA, docB in zip(doc["tgt_text"][sysA], doc["tgt_text"][sysB])
        # ])
        -np.mean([
            fastchrf.pairwise_chrf(
                [[doc["tgt_text"][sys][i] for sys in doc["tgt_text"].keys()]],
                [[doc["tgt_text"][sys][i] for sys in doc["tgt_text"].keys()]],
            )
            for i in range(len(list(doc["tgt_text"].values())[0]))
        ])
        for doc in data_local
    ]
    # sort from highest diversity
    data_local = [
        x[0] for x in
        sorted(zip(data_local, diversity), key=lambda x: x[1], reverse=True)
    ]


    # chunk into 20-hours waves (we have 4 domains so one wave is 80 hours ~= 1/2 of 200hrs)
    if batch_name[2] == "literary":
        # make sure literary (2 docs) is always two waves
        THRESHOLD = 10
    else:
        THRESHOLD = 20
    data_waves = [[]]
    for doc in data_local:
        if sum([doc["words"]*len(doc["tgt_text"]) for doc in data_waves[-1]]) * 0.8 / 60 /60 >= THRESHOLD:
            data_waves.append([])
        data_waves[-1].append(doc)
    
    # if last wave is less than 10 hours, merge it
    cost_last = sum([
        doc["words"] * len(doc["tgt_text"])
        for doc in data_waves[-1]
    ]) * 0.8 / 60 / 60
    if cost_last < 10:
        # if only one wave, just keep it
        if len(data_waves) > 1:
            data_waves[-2].extend(data_waves.pop())
    
    for wave_i, data_wave in enumerate(data_waves):
        cost = sum(
            doc["words"] * 0.8 * len(doc["tgt_text"])
            for doc in data_wave
        )
        print(
            f"{batch_name[0]+"-"+batch_name[1]+" (" + batch_name[2] + ", wave" + str(wave_i+1) +  ")":>35}",
            f"{cost/60/60:>3.0f}h",
            f"{len(data_wave):>2}docs",
            f"{sum([len(doc["src_text"]) for doc in data_wave]):>3}segs",
            f"{sum([doc["words"] for doc in data_wave]):>3}words",
        )

        # save selection
        data_agg_new[(*batch_name, f"wave{wave_i+1}")] = data_wave


# %%
import random
R_SHUFFLE = random.Random(0)

tasks_agg = collections.defaultdict(list)

for batch_name, data_local in data_agg_new.items():
    data_flat = [
        {
            **doc,
            "tgt_text": tgt,
            "system": sys,
        }
        for doc in data_local
        for sys, tgt in doc["tgt_text"].items()
    ]
    R_SHUFFLE.shuffle(data_flat)


    task = []
    for doc in data_flat:
        # approx number of words manageable in one hour
        if sum([doc["words"] for doc in task+[doc]]) >= 60*60 / 0.8:
            if task:
                tasks_agg[batch_name].append(task)
            task = []
        task.append(doc)
    if task:
        tasks_agg[batch_name].append(task)

    print(
        f"{batch_name[0]+"-"+batch_name[1]+" (" + batch_name[2] + "," + batch_name[3] + ")":>25}",
        f"{len(tasks_agg[batch_name]):>2} tasks",
        f"{sum([doc["words"] for doc in data_flat])*0.8/60/60:.0f}h",
    )
    
    # NOTE: no attention checks, otherwies we'd mix them in here

# %%


import json
import copy
import shutil
import os

with contextlib.chdir(pathlib.Path(__file__).parent.parent):
    # clean up appraise directory
    shutil.rmtree("appraise", ignore_errors=True)
    shutil.rmtree("appraise_output", ignore_errors=True)
    os.makedirs("appraise", exist_ok=True)
    os.makedirs("appraise_output", exist_ok=True)

    campaign_no = 1000
    for batch_name, tasks in tasks_agg.items():
        tasks_flat = []
        
        lang2 = batch_name[1].split("_")[0]
        with open(f"/home/vilda/ErrorSpanAnnotations/data/tutorial/{lang2}-en.esa.json", "r") as f:
            esa_tutorial = json.load(f)

        # turn to 3-letter codes
        lang1 = LANG_TO_3[batch_name[0].split("_")[0]]
        lang2 = LANG_TO_3[batch_name[1].split("_")[0]]
        

        for task in tasks:
            # load ESA tutorial at the beginning
            task_flat = [
                {
                    **line,
                    "isCompleteDocument": False,
                    # this works and doesn't get weirdly overwritten
                    "itemID": 0,
                } 
                for line in copy.deepcopy(esa_tutorial)
            ]
            item_id = 1
            for doc in task:
                # add video/screenshot
                if batch_name[2] == "speech":
                    assert len(doc["src_text"]) == 1, "Speech documents should have only one segment"
                    # add video
                    if doc["video"] is not None:
                        doc["src_text"][0] = f"""<video
                            src="https://vilda.net/t/wmt25/{doc["video"]}"
                            controls
                            disablepictureinpicture
                            preload="auto"
                            controlslist="nodownload"
                        ></video>"""
                if batch_name[2] == "social":
                    # add screenshot
                    if doc["screenshot"] is not None:
                        fname = doc["screenshot"].split("/")[-1]
                        doc["src_text"] = [
                            f"""<img src="https://vilda.net/t/wmt25/{doc["screenshot"]}/{fname}_{src_i+1}.png" alt="Screenshot" />"""
                            for src_i, _ in enumerate(doc["src_text"])
                        ]
                if batch_name[2] == "dialogue":
                    doc["src_text"] = [
                        src_line.replace("<br/>", "\n")
                        for src_line in doc["src_text"]
                    ]
                    doc["tgt_text"] = [
                        tgt_line.replace("<br/>", "\n")
                        for tgt_line in doc["tgt_text"]
                    ]

                for line_i, (src_line, tgt_line) in enumerate(zip(doc["src_text"], doc["tgt_text"])):
                    task_flat.append({
                        "mqm": [],
                        "documentID": doc["doc_id"],
                        "sourceID": doc["doc_id"] + "_#_" + str(line_i),
                        "targetID": doc["system"],
                        "sourceText": src_line,
                        "targetText": tgt_line,
                        "itemType": "TGT",
                        "isCompleteDocument": True,
                        # fake item_id that's unique within each batch
                        "itemID": item_id,
                    })
                    item_id += 1
            tasks_flat.append({
                "items": task_flat,
                "task": {
                    "batchNo": len(tasks_flat) + 1,
                    "randomSeed": 0,
                    "requiredAnnotations": 1,
                    "sourceLanguage": lang1,
                    "targetLanguage": lang2,
                },
            })
        
        manifest = {
            "CAMPAIGN_URL": "http://127.0.0.1:8000/dashboard/sso/",
            "CAMPAIGN_NAME": f"wmt25{lang1}{lang2}I{batch_name[2]}I{batch_name[3]}",
            "CAMPAIGN_KEY": f"wtm25{lang1}{lang2}I{batch_name[2]}I{batch_name[3]}",
            "CAMPAIGN_NO": campaign_no,
            "REDUNDANCY": 1,
            "TASKS_TO_ANNOTATORS": [
                [lang1, lang2, "uniform",  len(tasks_flat), len(tasks_flat)]
            ],

            "TASK_TYPE": "Document",
            "TASK_OPTIONS": "ESA;StaticContext"
        }
        campaign_no += 1
        with open(f"appraise/{manifest['CAMPAIGN_NAME']}_manifest.json", "w") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        with open(f"appraise/{manifest['CAMPAIGN_NAME']}_tasks.json", "w") as f:
            json.dump(tasks_flat, f, indent=2, ensure_ascii=False)


# %%

"""
for wave in 1 2; do
    zip /home/vilda/Downloads/v4_wave${wave}.zip appraise/*wave${wave}*.json
done;
"""

"""
rm -rf static appraise.log db.sqlite3 Batches
python3 manage.py migrate
python3 manage.py createsuperuser --no-input --username vilda --email vilem.zouhar@gmail.com
python3 manage.py collectstatic --no-post-process

# try adding all
for f_manifest in /home/vilda/wmt25-general-mt/appraise/wmt25*InewsIwave1_manifest.json; do
    f_tasks=${f_manifest/_manifest/_tasks}
    f_output=${f_manifest/_manifest.json/}
    f_output=$(basename "$f_output")
    echo "####### ${f_manifest} #######"
    python3 manage.py StartNewCampaign \
      ${f_manifest} \
    --batches-json ${f_tasks} \
    --csv-output /home/vilda/wmt25-general-mt/appraise_output/${f_output}.csv \
    --task-confirmation-tokens;
done

python3 manage.py runserver

python3 manage.py StartNewCampaign \
    /home/vilda/wmt25-general-mt/appraise/wmt25cesdeuIdialogueIwave1_manifest.json \
    --batches-json /home/vilda/wmt25-general-mt/appraise/wmt25cesdeuIdialogueIwave1_tasks.json \
    --csv-output /home/vilda/wmt25-general-mt/appraise_output/wmt25cesdeuIdialogueIwave1.csv

python3 manage.py StartNewCampaign \
    /home/vilda/wmt25-general-mt/appraise/wmt25cesdeuInewsIwave1_manifest.json \
    --batches-json /home/vilda/wmt25-general-mt/appraise/wmt25cesdeuInewsIwave1_tasks.json \
    --csv-output /home/vilda/wmt25-general-mt/appraise_output/wmt25cesdeuInewsIwave1.csv

"""