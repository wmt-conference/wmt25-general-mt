# %%
"""Remove YouTube sourced documents from the human evaluation files.

The speech domain of the WMT25 general MT human evaluation is sourced
entirely from YouTube. Those documents carry a doc_id whose source field
is vid_<video_id>, for example

    en-cs_CZ_#_speech_#_vid_3vpEaAjDgtI_#_0

and no vid_ document appears outside the speech domain, so dropping them
removes the speech domain and leaves every other domain untouched.

Both human evaluation files are filtered in place. Kept lines are written
back exactly as they were read, so the only change is whole records going
away. Re-running the script is a no-op.

Run from the humeval directory. Set DRY_RUN to True to report what would
be removed without touching anything.
"""

import json
import os

DRY_RUN = False

TARGETS = [
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


def filter_file(fname):
    # read and write bytes so that kept lines survive untouched, and stage
    # through a temporary file so an interrupted run cannot truncate the data
    tmp = fname + ".tmp"
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
    if DRY_RUN:
        os.remove(tmp)
    else:
        os.replace(tmp, fname)
    return kept, dropped


# %%
for fname in TARGETS:
    kept, dropped = filter_file(fname)
    total = kept + sum(dropped.values())
    print(fname)
    print(f"  {total} documents, kept {kept}, removed {sum(dropped.values())}")
    for dom, count in sorted(dropped.items()):
        print(f"    {count} from {dom}")
