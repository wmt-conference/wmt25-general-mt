"""Write copies of the human evaluation files without YouTube sourced documents.

The speech domain of the WMT25 general MT human evaluation is sourced
entirely from YouTube. Those documents carry a doc_id whose source field
is vid_<video_id>, for example

    en-cs_CZ_#_speech_#_vid_3vpEaAjDgtI_#_0

and no vid_ document appears outside the speech domain, so dropping them
removes the speech domain and leaves every other domain untouched.

The inputs are never modified. For each one a sibling file with a
noyoutube suffix is written, so

    wmt25-genmt-humeval.jsonl
    wmt25-genmt-humeval_control.jsonl

produce

    wmt25-genmt-humeval-noyoutube.jsonl
    wmt25-genmt-humeval_control-noyoutube.jsonl

Kept lines are copied as raw bytes rather than re-serialized, so records
that survive are identical to their originals.

Run from the humeval directory.
"""

import json
import os

SUFFIX = "-noyoutube"

SOURCES = [
    "../data/wmt25-genmt-humeval.jsonl",
    "../data/wmt25-genmt-humeval_control.jsonl",
]


def is_youtube(doc_id):
    # doc_id is langpair_#_domain_#_source_#_index
    parts = doc_id.split("_#_")
    return len(parts) > 2 and parts[2].startswith("vid_")


def domain(doc_id):
    parts = doc_id.split("_#_")
    return parts[1] if len(parts) > 1 else ""


def filtered_name(fname):
    base, ext = os.path.splitext(fname)
    return base + SUFFIX + ext


def filter_file(fname):
    # write through a temporary file so an interrupted run leaves no
    # half-written output behind for the next step to pick up
    fname_out = filtered_name(fname)
    tmp = fname_out + ".tmp"
    kept = 0
    dropped = {}
    with open(fname, "rb") as f_in, open(tmp, "wb") as f_out:
        for line in f_in:
            doc_id = json.loads(line)["doc_id"]
            if is_youtube(doc_id):
                dropped[domain(doc_id)] = dropped.get(domain(doc_id), 0) + 1
            else:
                f_out.write(line)
                kept += 1
    os.replace(tmp, fname_out)
    return fname_out, kept, dropped


# %%
for fname in SOURCES:
    fname_out, kept, dropped = filter_file(fname)
    total = kept + sum(dropped.values())
    print(f"{fname} -> {fname_out}")
    print(f"  {total} documents, kept {kept}, removed {sum(dropped.values())}")
    for dom, count in sorted(dropped.items()):
        print(f"    {count} from {dom}")
