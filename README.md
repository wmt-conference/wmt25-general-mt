# WMT25 General Machine Translation

This repository contains data and metadata for the [WMT25 General Machine Translation Shared Task](https://www2.statmt.org/wmt25/).
Data:
- `data/wmt25-genmt.jsonl` all sources and system translations
- `data/wmt25-genmt-humeval.jsonl` all sources, system translations, and human annotations
- `data/wmt25-genmt-humeval_control.jsonl` annotated control tasks for all annotators

# Human Evaluation Data

The human evaluation data is stored as `jsonl`, so can be downloaded as
```bash
wget https://github.com/wmt-conference/wmt25-general-mt/raw/refs/heads/main/data/wmt25-genmt-humeval.jsonl
```
and parsed as:
```python
import json
with open("wmt25-genmt-humeval.jsonl", "r") as f:
    data = [json.loads(x) for x in f.readlines()]
```

Each line corresponds to one source segment. Each line is a dictionary with the following keys and structure:
```python
{
  # maps from system names to annotations
  "scores": {                      
    "sysA": [
      {
        "score": 90,
        "annotator": "pseudoname",
        "errors": [                # list of errors
          {
            "start_i": 20,         # start character in the translation
            "end_i": 25,           # end character in the translation (inclusive)
            "severity": "minor",   # severity can be "minor" or "major"
          },
          ...                      # there can be 0 or more errors for each annotation
        ],
        "times": [...],            # array with two values: first and last interaction with the segment
      },
      {
        ...                        # second annotation
      }
    ],
    "sysB": [
        ...
    ],
    "sysC": [
        ...
    ]
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
    "Mistral-Medium": [
      {
        "score": 100,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1755438807.158,
          1755438807.158
        ],
        "errors": []
      },
      {
        "score": 100,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1756575443.399,
          1756575443.4
        ],
        "errors": []
      }
    ],
    "Gemma-3-27B": [
      {
        "score": 80,
        "annotator": "cs-de_#_annotator7",
        "times": [
          1756237713.918,
          1756237733.839
        ],
        "errors": []
      },
      {
        "score": 90,
        "annotator": "cs-de_#_annotator13",
        "times": [
          1757366130.251,
          1757366136.701
        ],
        "errors": [
          {
            "start_i": 37,
            "end_i": 39,
            "severity": "minor"
          }
        ]
      }
    ],
    "Algharb": [
      {
        "score": 50,
        "annotator": "cs-de_#_annotator13",
        "times": [
          1756060734.928,
          1756060741.547
        ],
        "errors": [
          {
            "start_i": 45,
            "end_i": 69,
            "severity": "minor"
          }
        ]
      },
      {
        "score": 70,
        "annotator": "cs-de_#_annotator11",
        "times": [
          1756979593.467,
          1756979593.467
        ],
        "errors": []
      }
    ],
    "Claude-4": [
      {
        "score": 66,
        "annotator": "cs-de_#_annotator13",
        "times": [
          1756066117.999,
          1756066124.125
        ],
        "errors": [
          {
            "start_i": 51,
            "end_i": 66,
            "severity": "minor"
          }
        ]
      },
      {
        "score": 100,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1756719413.716,
          1756719413.717
        ],
        "errors": []
      }
    ],
    "GemTrans": [
      {
        "score": 100,
        "annotator": "cs-de_#_annotator13",
        "times": [
          1756066567.631,
          1756066567.631
        ],
        "errors": []
      },
      {
        "score": 100,
        "annotator": "cs-de_#_annotator2",
        "times": [
          1756747372.719,
          1756747372.72
        ],
        "errors": []
      }
    ],
    "TowerPlus-9B": [
      {
        "score": 30,
        "annotator": "cs-de_#_annotator13",
        "times": [
          1756491604.246,
          1756491615.387
        ],
        "errors": [
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
        ]
      },
      {
        "score": 60,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1756655649.08,
          1756655665.612
        ],
        "errors": [
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
        ]
      }
    ],
    "Yolu": [
      {
        "score": 75,
        "annotator": "cs-de_#_annotator9",
        "times": [
          1756135199.154,
          1756135259.972
        ],
        "errors": [
          {
            "start_i": 52,
            "end_i": 67,
            "severity": "minor"
          }
        ]
      },
      {
        "score": 69,
        "annotator": "cs-de_#_annotator11",
        "times": [
          1756985004.427,
          1756985018.903
        ],
        "errors": [
          {
            "start_i": 21,
            "end_i": 29,
            "severity": "minor"
          }
        ]
      }
    ],
    "SRPOL": [
      {
        "score": 100,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1756210117.877,
          1756210117.877
        ],
        "errors": []
      },
      {
        "score": 68,
        "annotator": "cs-de_#_annotator11",
        "times": [
          1756992191.695,
          1756992191.695
        ],
        "errors": []
      }
    ],
    "IRB-MT": [
      {
        "score": 80,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1756216126.882,
          1756216159.457
        ],
        "errors": [
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
        ]
      },
      {
        "score": 88,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1756654506.152,
          1756654548.54
        ],
        "errors": [
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
        ]
      }
    ],
    "CUNI-MH-v2": [
      {
        "score": 85,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1756048185.039,
          1756048193.574
        ],
        "errors": [
          {
            "start_i": 56,
            "end_i": 64,
            "severity": "major"
          }
        ]
      },
      {
        "score": 90,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1757581711.301,
          1757581718.614
        ],
        "errors": [
          {
            "start_i": 56,
            "end_i": 64,
            "severity": "major"
          }
        ]
      }
    ],
    "Shy": [
      {
        "score": 100,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1756049048.458,
          1756049048.458
        ],
        "errors": []
      },
      {
        "score": 83,
        "annotator": "cs-de_#_annotator11",
        "times": [
          1757601482.326,
          1757601482.326
        ],
        "errors": []
      }
    ],
    "DeepSeek-V3": [
      {
        "score": 100,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1755800000.743,
          1755800000.743
        ],
        "errors": []
      },
      {
        "score": 100,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1756715162.242,
          1756715162.242
        ],
        "errors": []
      }
    ],
    "Wenyiil": [
      {
        "score": 100,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1755803606.239,
          1755803606.239
        ],
        "errors": []
      },
      {
        "score": 100,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1757533924.07,
          1757533925.665
        ],
        "errors": []
      }
    ],
    "refA": [
      {
        "score": 90,
        "annotator": "cs-de_#_annotator3",
        "times": [
          1754418958.805,
          1754418973.024
        ],
        "errors": [
          {
            "start_i": 71,
            "end_i": 81,
            "severity": "minor"
          }
        ]
      },
      {
        "score": 95,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1756717218.413,
          1756717225.13
        ],
        "errors": [
          {
            "start_i": 63,
            "end_i": 69,
            "severity": "minor"
          }
        ]
      }
    ],
    "Laniqo": [
      {
        "score": 100,
        "annotator": "cs-de_#_annotator2",
        "times": [
          1755374717.012,
          1755374717.012
        ],
        "errors": []
      },
      {
        "score": 100,
        "annotator": "cs-de_#_annotator8",
        "times": [
          1757058299.915,
          1757058302.799
        ],
        "errors": []
      }
    ],
    "CommandA-MT": [
      {
        "score": 90,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1755540155.23,
          1755540161.797
        ],
        "errors": [
          {
            "start_i": 25,
            "end_i": 33,
            "severity": "major"
          }
        ]
      },
      {
        "score": 85,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1757578901.919,
          1757578939.373
        ],
        "errors": [
          {
            "start_i": 25,
            "end_i": 33,
            "severity": "major"
          }
        ]
      }
    ],
    "Gemma-3-12B": [
      {
        "score": 100,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1755543099.033,
          1755543106.392
        ],
        "errors": []
      },
      {
        "score": 100,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1756656302.547,
          1756656302.547
        ],
        "errors": []
      }
    ],
    "Gemini-2.5-Pro": [
      {
        "score": 72,
        "annotator": "cs-de_#_annotator11",
        "times": [
          1756294650.115,
          1756294650.115
        ],
        "errors": []
      },
      {
        "score": 100,
        "annotator": "cs-de_#_annotator2",
        "times": [
          1757448632.904,
          1757448632.904
        ],
        "errors": []
      }
    ],
    "GPT-4.1": [
      {
        "score": 90,
        "annotator": "cs-de_#_annotator3",
        "times": [
          1754814944.67,
          1754814949.046
        ],
        "errors": [
          {
            "start_i": 56,
            "end_i": 70,
            "severity": "minor"
          }
        ]
      },
      {
        "score": 100,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1756625403.939,
          1756625407.598
        ],
        "errors": []
      }
    ],
    "CommandA": [
      {
        "score": 100,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1755079989.201,
          1755079989.201
        ],
        "errors": []
      },
      {
        "score": 100,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1756653717.864,
          1756653717.864
        ],
        "errors": []
      }
    ],
    "UvA-MT": [
      {
        "score": 100,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1755089919.57,
          1755089919.571
        ],
        "errors": []
      },
      {
        "score": 100,
        "annotator": "cs-de_#_annotator6",
        "times": [
          1756658820.274,
          1756658820.274
        ],
        "errors": []
      }
    ]
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
```bash
wget https://github.com/wmt-conference/wmt25-general-mt/raw/refs/heads/main/data/wmt25-genmt-humeval_control.jsonl
```

The video and screenshot assets are hosted at [data.statmt.org/wmt25/general-mt/wmt25_genmt_assets.zip](https://data.statmt.org/wmt25/general-mt/wmt25_genmt_assets.zip) and items optionally have `video` or `screenshot` keys which point to the path inside of this archive.