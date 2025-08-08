# %%
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

import glob
import json

data = []
# rather than re-doing everything in 01-prepare_waves, let's just load the output of appraise_v6 and yank some segments from there
for fname in glob.glob("../appraise_v6/*_tasks.json"):
    with open(fname, "r") as f:
        data += [
            item
            for x in json.load(f)
            for item in x["items"]
            if "tutorial" not in item["documentID"]
        ]
langs = {x["sourceID"].split("_#_")[0] for x in data}

# %%
import random
import os
import shutil

shutil.rmtree("../appraise_ctrl", ignore_errors=True)
os.makedirs("../appraise_ctrl", exist_ok=True)

campaign_no = 2000
for lang in langs:
    R_LOCAL = random.Random(0)
    data_local = [
        x for x in data
        if x["sourceID"].split("_#_")[0] == lang
    ]
    domains = list({x["sourceID"].split("_#_")[1] for x in data_local})
    
    data_control = []

    for domain in domains:
        data_domain = [
            x for x in data_local
            if x["sourceID"].split("_#_")[1] == domain
        ]
        systems = list({x["targetID"] for x in data_local})
        docs = list({x["documentID"] for x in data_domain})

        data_control_local = []

        # each domain has budget of 7 segments
        while len(data_control_local) < 7:
            # pick random system for this snippet
            system = R_LOCAL.choice(systems)
            doc = R_LOCAL.choice(docs)
            # don't repeat the same doc
            docs.remove(doc)
            # don't repeat the same system
            systems.remove(system)

            data_tmp = [
                x for x in data_domain
                if x["targetID"] == system and x["documentID"] == doc
            ]
            # clip literary and social because they will be too long
            data_tmp = data_tmp[:7]
            data_control_local += data_tmp
        
        data_control += data_control_local
    
    # shuffle the control data on the level of documents
    data_control.sort(key=lambda x: hash(x["documentID"]))
    for line_i, line in enumerate(data_control):
        line["itemID"] = line_i+1
        line["isCompleteDocument"] = True
        
    lang2 = lang.split("-")[1].split("_")[0]
    with open(f"/home/vilda/ErrorSpanAnnotations/data/tutorial/{lang2}-en.esa.json", "r") as f:
        data_control = [
            x | {"itemID": 1000000+x_i, "isCompleteDocument": True}
            for x_i, x in enumerate(json.load(f))
        ] + data_control
    print(lang, len(data_control))

    lang1, lang2 = lang.split("-")[0], lang.split("-")[1].split("_")[0]
    lang1 = LANG_TO_3[lang1]
    lang2 = LANG_TO_3[lang2]

    manifest = {
        "CAMPAIGN_URL": "http://127.0.0.1:8000/dashboard/sso/",
        "CAMPAIGN_NAME": f"wmt25{lang1}{lang2}IctrlIwave1v7",
        "CAMPAIGN_KEY": f"wtm25{lang1}{lang2}Ictrlwave1v7",
        "CAMPAIGN_NO": campaign_no,
        "REDUNDANCY": 30,
        "TASKS_TO_ANNOTATORS": [
            [lang1, lang2, "uniform",  30, 1]
        ],
        "TASK_TYPE": "Document",
        "TASK_OPTIONS": "ESA;StaticContext"
    }

    campaign_no += 1
    with open(f"../appraise_ctrl/{manifest['CAMPAIGN_NAME']}_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    with open(f"../appraise_ctrl/{manifest['CAMPAIGN_NAME']}_tasks.json", "w") as f:
        json.dump([{
            "items": data_control,
            "task": {
                "batchNo": 1,
                "randomSeed": 0,
                "requiredAnnotations": 1,
                "sourceLanguage": lang1,
                "targetLanguage": lang2,
            },
        }],
        f,
        indent=2,
        ensure_ascii=False,
    )



# %%

"""
zip /home/vilda/Downloads/v7_ctrl.zip appraise_ctrl/*IctrlIwave1v7_*.json

rm -rf static appraise.log db.sqlite3 Batches
python3 manage.py migrate
python3 manage.py createsuperuser --no-input --username vilda --email vilem.zouhar@gmail.com
python3 manage.py collectstatic --no-post-process

python3 manage.py runserver

python3 manage.py StartNewCampaign \
    /home/vilda/wmt25-general-mt/appraise_ctrl/wmt25cesdeuIctrlIwave1_manifest.json \
    --batches-json /home/vilda/wmt25-general-mt/appraise_ctrl/wmt25cesdeuIctrlIwave1_tasks.json \
    --csv-output /home/vilda/wmt25-general-mt/appraise_output/wmt25cesdeuIctrlIwave1.csv

python3 manage.py StartNewCampaign \
    /home/vilda/wmt25-general-mt/appraise_ctrl/wmt25engcesIctrlIwave1_manifest.json \
    --batches-json /home/vilda/wmt25-general-mt/appraise_ctrl/wmt25engcesIctrlIwave1_tasks.json \
    --csv-output /home/vilda/wmt25-general-mt/appraise_output/wmt25engcesIctrlIwave1.csv
    
python3 manage.py StartNewCampaign \
    /home/vilda/wmt25-general-mt/appraise_ctrl/wmt25engukrIctrlIwave1_manifest.json \
    --batches-json /home/vilda/wmt25-general-mt/appraise_ctrl/wmt25engukrIctrlIwave1_tasks.json \
    --csv-output /home/vilda/wmt25-general-mt/appraise_output/wmt25engukrIctrlIwave1.csv

python3 manage.py StartNewCampaign \
    /home/vilda/wmt25-general-mt/appraise_ctrl/wmt25engsrpIctrlIwave1_manifest.json \
    --batches-json /home/vilda/wmt25-general-mt/appraise_ctrl/wmt25engsrrIctrlIwave1_tasks.json \
    --csv-output /home/vilda/wmt25-general-mt/appraise_output/wmt25engsrrIctrlIwave1.csv

python3 manage.py StartNewCampaign \
    /home/vilda/wmt25-general-mt/appraise_ctrl/wmt25engmasIctrlIwave1_manifest.json \
    --batches-json /home/vilda/wmt25-general-mt/appraise_ctrl/wmt25engmasIctrlIwave1_tasks.json \
    --csv-output /home/vilda/wmt25-general-mt/appraise_output/wmt25engmasIctrlIwave1.csv
"""