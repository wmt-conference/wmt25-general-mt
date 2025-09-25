# WMT25 General Machine Translation

This repository contains data and metadata for the [WMT25 General Machine Translation Shared Task](https://www2.statmt.org/wmt25/).
Data:
- `data/wmt25-genmt.jsonl` all sources and system translations
- `data/wmt25-genmt-humeval.jsonl` all sources, system translations, and human annotations
- `data/wmt25-genmt-humeval_control.jsonl` annotated control tasks for all annotators

# Human Evaluation Data

The human evaluation data is stored as `jsonl`, so can be parsed as:
```python
import json
with open("wmt25-genmt-humeval.jsonl", "r") as f:
    data = [json.loads(x) for x in f.readlines()]
```

Each line corresponds to one source segment. Each line is a dictionary with the following keys and structure:
```python
{
  # maps from system names to annotations
  # if this is empty, then the segment wasn't selected for human evaluation (about 50% of data)
  "scores": {                      
    "sysA": {
      "human1": 90,                # score from the first round of annotations
      "annotator1": "pseudoname",  # pseudo-anonymized annotator ID valid within the whole WMT25 annotations
      "errors1": [                 # list of errors
        {
          "start_i": 20,           # start character in the translation
          "end_i": 25,             # end character in the translation (inclusive)
          "severity": "minor",     # severity can be "minor" or "major"
        },
        ...                        # there can be 0 or more errors for each annotation
      ],
      "times1": [...],             # array with two values: first and last interaction with the segment
      "human2": 95,                # score from the second round of annotations
      "annotator2": "pseudoname",  # pseudo-anonymized annotator ID valid within the whole WMT25 annotations
      "errors2": [...],
      "times2": [...],
    },
    "sysB": {
        ...
    },
    "sysC": {
        ...
    }
  },
  "src_text": "hello..",           # source segment (string)
  "tgt_text": {                    # maps from system names to translations
    "sysA": "Hallo..",
    "sysB": "Hallo!",
    ...
  },
  # segment/document identifier with the described sturcture (separated by _#_)
  "doc_id": "lang1-lan2_variant#_domain_#_documentname_#_segmentid"
}
```

As an example, see:
```python
{
  "scores": {
    "Mistral-Medium": {
      "human1": 100,
      "errors1": [],
      "annotator1": "cesdeub309",
      "human2": 100,
      "errors2": [],
      "annotator2": "cesdeuf702"
    },
    "Gemma-3-27B": {
      "human1": 80,
      "errors1": [],
      "annotator1": "cesdeub307"
    },
    "Algharb": {
      "human1": 50,
      "errors1": [
        {
          "start_i": 45,
          "end_i": 69,
          "severity": "minor"
        }
      ],
      "annotator1": "cesdeub312"
    },
    "Claude-4": {
      "human1": 66,
      "errors1": [
        {
          "start_i": 51,
          "end_i": 66,
          "severity": "minor"
        }
      ],
      "annotator1": "cesdeub312",
      "human2": 100,
      "errors2": [],
      "annotator2": "cesdeuf706"
    },
    "GemTrans": {
      "human1": 100,
      "errors1": [],
      "annotator1": "cesdeub312",
      "human2": 100,
      "errors2": [],
      "annotator2": "cesdeuf707"
    },
    "TowerPlus-9B": {
      "human1": 30,
      "errors1": [
        {
          "start_i": 45,
          "end_i": 55,
          "severity": "major"
        },
        {
          "start_i": 57,
          "end_i": 77,
          "severity": "minor"
        }
      ],
      "annotator1": "cesdeub312",
      "human2": 60,
      "errors2": [
        {
          "start_i": 49,
          "end_i": 55,
          "severity": "major"
        },
        {
          "start_i": 61,
          "end_i": 76,
          "severity": "major"
        }
      ],
      "annotator2": "cesdeuf705"
    },
    "Yolu": {
      "human1": 75,
      "errors1": [
        {
          "start_i": 52,
          "end_i": 67,
          "severity": "minor"
        }
      ],
      "annotator1": "cesdeub313"
    },
    "SRPOL": {
      "human1": 100,
      "errors1": [],
      "annotator1": "cesdeub314"
    },
    "IRB-MT": {
      "human1": 80,
      "errors1": [
        {
          "start_i": 20,
          "end_i": 40,
          "severity": "major"
        },
        {
          "start_i": 74,
          "end_i": 86,
          "severity": "major"
        }
      ],
      "annotator1": "cesdeub314",
      "human2": 88,
      "errors2": [
        {
          "start_i": 20,
          "end_i": 30,
          "severity": "major"
        },
        {
          "start_i": 32,
          "end_i": 40,
          "severity": "major"
        },
        {
          "start_i": 74,
          "end_i": 86,
          "severity": "minor"
        }
      ],
      "annotator2": "cesdeuf705"
    },
    "CUNI-MH-v2": {
      "human1": 85,
      "errors1": [
        {
          "start_i": 56,
          "end_i": 64,
          "severity": "major"
        }
      ],
      "annotator1": "cesdeub311"
    },
    "Shy": {
      "human1": 100,
      "errors1": [],
      "annotator1": "cesdeub311"
    },
    "DeepSeek-V3": {
      "human1": 100,
      "errors1": [],
      "annotator1": "cesdeub30d",
      "human2": 100,
      "errors2": [],
      "annotator2": "cesdeuf706"
    },
    "Wenyiil": {
      "human1": 100,
      "errors1": [],
      "annotator1": "cesdeub30d"
    },
    "refA": {
      "human1": 90,
      "errors1": [
        {
          "start_i": 71,
          "end_i": 81,
          "severity": "minor"
        }
      ],
      "annotator1": "cesdeub302",
      "human2": 95,
      "errors2": [
        {
          "start_i": 63,
          "end_i": 69,
          "severity": "minor"
        }
      ],
      "annotator2": "cesdeuf706"
    },
    "Laniqo": {
      "human1": 100,
      "errors1": [],
      "annotator1": "cesdeub308"
    },
    "CommandA-MT": {
      "human1": 90,
      "errors1": [
        {
          "start_i": 25,
          "end_i": 33,
          "severity": "major"
        }
      ],
      "annotator1": "cesdeub30a"
    },
    "Gemma-3-12B": {
      "human1": 100,
      "errors1": [],
      "annotator1": "cesdeub30a",
      "human2": 100,
      "errors2": [],
      "annotator2": "cesdeuf705"
    },
    "Gemini-2.5-Pro": {
      "human1": 72,
      "errors1": [],
      "annotator1": "cesdeub315"
    },
    "GPT-4.1": {
      "human1": 90,
      "errors1": [
        {
          "start_i": 56,
          "end_i": 70,
          "severity": "minor"
        }
      ],
      "annotator1": "cesdeub304",
      "human2": 100,
      "errors2": [],
      "annotator2": "cesdeuf704"
    },
    "CommandA": {
      "human1": 100,
      "errors1": [],
      "annotator1": "cesdeub306",
      "human2": 100,
      "errors2": [],
      "annotator2": "cesdeuf705"
    },
    "UvA-MT": {
      "human1": 100,
      "errors1": [],
      "annotator1": "cesdeub306",
      "human2": 100,
      "errors2": [],
      "annotator2": "cesdeuf705"
    }
  },
  "src_text": "Ina T. hodnotí sexy pokusy hvězd: Myslivcová přestřelila!",
  "tgt_text": {
    "refA": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat es diesmal übertrieben!",
    "Yolu": "Ina T. bewertet sexy Auftritte der Stars: Myslivcová hat übertrieben!",
    "SalamandraTA": "Ina T. bewertet die sexy Stunt-Versuche der Stars: Myslivcova hat es übertrieben!",
    "CommandA-MT": "Ina T. bewertet die sexy Auftritte der Stars: Myslivcová hat es übertrieben!",
    "CUNI-MH-v2": "Ina T. bewertet sexy Versuche der Stars: Myslivcová hat überzogen!",
    "DLUT_GTCOM": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat übers Ziel hinausgeschossen!",
    "Algharb": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat übertrieben",
    "GemTrans": "Ina T. bewertet die aufreizenden Outfits der Stars: Myslivcová hat es übertrieben!",
    "IRB-MT": "Ina T. bewertet die provokanten Auftritte von Prominenten: Myslivcová hat überschritten!",
    "Laniqo": "Ina T. bewertet die Versuche der Stars, sexy zu sein: Myslivcová hat übertrieben!",
    "IR-MultiagentMT": "Ina T. bewertet die sexy Auftritte der Stars: Myslivcová hat die Zielscheibe verfehlt!",
    "Wenyiil": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat übertrieben",
    "Shy": "Ina T. bewertet sexy Versuche der Stars: Myslivcová hat übertrieben!",
    "SRPOL": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat es übertrieben!",
    "TranssionMT": "Ina T. bewertet die sexy Versuche der Stars: Denkerin erschoss!",
    "TranssionTranslate": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat übers Ziel hinausgeschossen!",
    "UvA-MT": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat es übertrieben!",
    "AyaExpanse-32B": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat überzogen!",
    "AyaExpanse-8B": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová schießt daneben!",
    "Claude-4": "Ina T. bewertet sexy Versuche der Stars: Myslivcová hat übertrieben!",
    "CommandA": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat übertrieben!",
    "DeepSeek-V3": "Ina T. bewertet sexy Versuche der Stars: Myslivcová hat es übertrieben!",
    "Gemini-2.5-Pro": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat übertrieben!",
    "Gemma-3-12B": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat es übertrieben!",
    "Gemma-3-27B": "Ina T. bewertet aufreizende Versuche von Stars: Myslivcová hat es übertrieben!",
    "Llama-4-Maverick": "Ina T. bewertet die sexy Anläufe der Stars: Myslivcová schießt über das Ziel hinaus!",
    "ONLINE-B": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat übers Ziel hinausgeschossen!",
    "ONLINE-G": "Ina T. review die sexy Experimente der Stars: Der Jäger erschossen!",
    "ONLINE-W": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat es übertrieben!",
    "Qwen3-235B": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat übertrieben!",
    "CommandR7B": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová übertreibt es!",
    "GPT-4.1": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat übertrieben!",
    "Llama-3.1-8B": "Ina T. bewertet sexy Versuche von Stars: Myslivcová übertrifft sich!",
    "Mistral-7B": "Ina T. bewertet sexuelle Versuche von Stars: Myslivcová scheiterte!",
    "Qwen2.5-7B": "Ina T. bewertet sexy Versuche der Stars: Myslivcová hat Schuss!",
    "Mistral-Medium": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat übertrieben!",
    "TowerPlus-9B": "Ina T. bewertet die sexy Versuche der Stars: Die Jägerin hat daneben gefeuert!",
    "TowerPlus-72B": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat übers Ziel hinausgeschossen!",
    "EuroLLM-9B": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat überzogen!",
    "EuroLLM-22B": "Ina T. bewertet die sexy Versuche der Stars: Myslivcová hat übertrieben!",
    "NLLB": "Ina T. bewertet die sexy Versuche der Stars:"
  },
  "doc_id": "cs-de_DE_#_news_#_blesk.cz.112043_#_0"
}
```

All annotators also annotated the same few segments for each of the languages, which helps in establishing their reliability.
The annotation format is slightly different, namely scores map to systems which map to lists instead of dictionaries.
The lists are in the following format:
```python
[
    {
        "human": 90,               # final translation score
        "annotator": "pseudoname", # pseudoanonymized, compatible with all other annotations
        "errors": [                # list of errors as above
            ...
        ],
        "times": [...]
    },
    {
        "human": 80,               # final translation score by another annotator
        "annotator": "pseudoname", # pseudoanonymized, compatible with all other annotations
        "errors": [                # list of errors as above
            ...
        ],
        "times": [...]
    },
]
```

The video and screenshot assets are hosted at [data.statmt.org/wmt25/general-mt/wmt25_genmt_assets.zip](https://data.statmt.org/wmt25/general-mt/wmt25_genmt_assets.zip) and items optionally have `video` or `screenshot` keys which point to the path inside of this archive.