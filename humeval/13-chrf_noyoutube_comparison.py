"""Compare chrF per system between the full data and the YouTube free data.

Scores every system in the human evaluation files with chrF against refA,
once on the original file and once on the file written by
09-filter_youtube.py, and reports the difference. The point is to show
whether dropping the YouTube sourced speech domain moves system scores or
reorders systems.

Scores are reported per language pair and per language pair and domain.
chrF is not comparable across languages, so nothing is pooled across
language pairs. A system is scored on the segments where refA exists and
that system produced an output. Language pairs without a reference cannot
be scored and are listed as skipped.

chrF statistics are additive over segments, so each segment is scored once
and the resulting counts are summed into whichever grouping is being
reported. Reference n-grams are extracted once per segment and shared by
every system, since they all score against the same reference.

Writes a markdown report. Output is deterministic, so re-running produces
an identical file unless the data changed.

Run from the humeval directory.
"""

import collections
import json
import os
import sys

from sacrebleu.metrics import CHRF

REPORT = "../analysis/chrf_noyoutube_comparison.md"

# (label, original file, YouTube free file)
PAIRS = [
    (
        "Human evaluation",
        "../data/wmt25-genmt-humeval.jsonl",
        "../data/wmt25-genmt-humeval-noyoutube.jsonl",
    ),
    (
        "Control",
        "../data/wmt25-genmt-humeval_control.jsonl",
        "../data/wmt25-genmt-humeval_control-noyoutube.jsonl",
    ),
]

REFERENCE = "refA"
YOUTUBE_DOMAIN = "speech"

# chrF2 as used for WMT reporting: character 6grams, beta 2, no word ngrams
chrf = CHRF()


def parse_doc_id(doc_id):
    parts = doc_id.split("_#_")
    return parts[0], parts[1]


def collect(fname):
    """Score every segment once and key the statistics by language pair,
    domain and system."""
    stats = collections.defaultdict(lambda: collections.defaultdict(list))
    segments = collections.Counter()
    unscorable = collections.Counter()

    with open(fname, "r") as f:
        for line in f:
            item = json.loads(line)
            lp, domain = parse_doc_id(item["doc_id"])
            segments[lp] += 1
            targets = item["tgt_text"]
            reference = targets.get(REFERENCE)
            if reference is None:
                unscorable[lp] += 1
                continue
            # the reference is shared by every system on this segment
            ref_info = chrf._extract_reference_info([reference])
            for system, hypothesis in targets.items():
                if system == REFERENCE:
                    continue
                stats[(lp, domain)][system].append(
                    chrf._compute_segment_statistics(hypothesis, ref_info)
                )
    return stats, segments, unscorable


def score(stat_rows):
    return chrf._aggregate_and_compute(stat_rows).score


def by_langpair(stats):
    """Collapse the domain axis: {lp: {system: (chrF, n)}}."""
    merged = collections.defaultdict(lambda: collections.defaultdict(list))
    for (lp, _domain), systems in stats.items():
        for system, rows in systems.items():
            merged[lp][system].extend(rows)
    return {
        lp: {s: (score(rows), len(rows)) for s, rows in systems.items()}
        for lp, systems in merged.items()
    }


def by_langpair_domain(stats):
    """{(lp, domain): {system: (chrF, n)}}."""
    return {
        key: {s: (score(rows), len(rows)) for s, rows in systems.items()}
        for key, systems in stats.items()
    }


def fmt_delta(value):
    return f"{value:+.2f}" if abs(value) >= 0.005 else "0.00"


def ranking(scores_lp, systems):
    """Systems ordered by chrF, best first, as {system: rank}."""
    order = sorted(systems, key=lambda s: (-scores_lp[s][0], s))
    return {system: i + 1 for i, system in enumerate(order)}


def build_section(label, fname_a, fname_b, out):
    print(f"  scoring {fname_a}", file=sys.stderr)
    stats_a, segments_a, _ = collect(fname_a)
    print(f"  scoring {fname_b}", file=sys.stderr)
    stats_b, segments_b, _ = collect(fname_b)

    lp_a, lp_b = by_langpair(stats_a), by_langpair(stats_b)
    dom_a, dom_b = by_langpair_domain(stats_a), by_langpair_domain(stats_b)

    out.append(f"## {label}")
    out.append("")
    out.append(f"`{os.path.basename(fname_a)}` vs `{os.path.basename(fname_b)}`")
    out.append("")

    skipped = sorted(lp for lp in segments_a if lp not in lp_a)
    if skipped:
        out.append(
            "Not scored, no `"
            + REFERENCE
            + "` on any segment: "
            + ", ".join(f"`{lp}`" for lp in skipped)
        )
        out.append("")

    # every domain other than the YouTube one keeps exactly the same
    # segments, so its score must not move at all
    unchanged, moved_unexpectedly = 0, []
    for key, systems in dom_a.items():
        if key[1] == YOUTUBE_DOMAIN:
            continue
        for system, (value, _n) in systems.items():
            other = dom_b.get(key, {}).get(system)
            if other is None:
                continue
            if other[0] == value:
                unchanged += 1
            else:
                moved_unexpectedly.append((key, system, value, other[0]))
    out.append(
        f"Check: {unchanged} of {unchanged + len(moved_unexpectedly)} retained"
        " language pair and domain scores are bit identical between the two"
        " files, as they must be when only `speech` segments are removed."
    )
    if moved_unexpectedly:
        out.append("")
        out.append("Unexpected movement in a retained domain:")
        for (lp, domain), system, a, b in moved_unexpectedly[:20]:
            out.append(f"* `{lp}` `{domain}` {system}: {a:.4f} to {b:.4f}")
    out.append("")

    details = []
    out.append("### Summary by language pair")
    out.append("")
    out.append(
        "| language pair | systems | segments | segments no YT | mean delta |"
        " min delta | max delta | rank changes |"
    )
    out.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for lp in sorted(lp_a):
        shared = sorted(set(lp_a[lp]) & set(lp_b.get(lp, {})))
        if not shared:
            continue
        deltas = {s: lp_b[lp][s][0] - lp_a[lp][s][0] for s in shared}
        rank_a, rank_b = ranking(lp_a[lp], shared), ranking(lp_b[lp], shared)
        moved = sum(1 for s in shared if rank_a[s] != rank_b[s])
        mean_delta = sum(deltas.values()) / len(deltas)
        out.append(
            f"| `{lp}` | {len(shared)} | {segments_a[lp]} | {segments_b.get(lp, 0)} |"
            f" {fmt_delta(mean_delta)} | {fmt_delta(min(deltas.values()))} |"
            f" {fmt_delta(max(deltas.values()))} | {moved} of {len(shared)} |"
        )
        details.append((lp, shared, deltas, rank_a, rank_b))
    out.append("")

    movers = sorted(
        ((abs(d), lp, s, d) for lp, shared, deltas, _, _ in details
         for s, d in deltas.items()),
        key=lambda x: (-x[0], x[1], x[2]),
    )
    if movers:
        out.append("### Largest score movements")
        out.append("")
        out.append("| language pair | system | chrF | chrF no YT | delta |")
        out.append("|---|---|---:|---:|---:|")
        for _, lp, system, delta in movers[:25]:
            out.append(
                f"| `{lp}` | {system} | {lp_a[lp][system][0]:.2f} |"
                f" {lp_b[lp][system][0]:.2f} | {fmt_delta(delta)} |"
            )
        out.append("")

    out.append("### Per system by language pair")
    out.append("")
    for lp, shared, deltas, rank_a, rank_b in details:
        out.append(f"#### `{lp}`")
        out.append("")
        out.append(
            "| system | chrF | n | chrF no YT | n no YT | delta | rank |"
            " rank no YT |"
        )
        out.append("|---|---:|---:|---:|---:|---:|---:|---:|")
        for system in sorted(shared, key=lambda s: (-lp_a[lp][s][0], s)):
            score_a, n_a = lp_a[lp][system]
            score_b, n_b = lp_b[lp][system]
            shift = ""
            if rank_a[system] != rank_b[system]:
                shift = f" ({rank_b[system] - rank_a[system]:+d})"
            out.append(
                f"| {system} | {score_a:.2f} | {n_a} | {score_b:.2f} | {n_b} |"
                f" {fmt_delta(deltas[system])} | {rank_a[system]} |"
                f" {rank_b[system]}{shift} |"
            )
        out.append("")

    out.append("### Per system by language pair and domain")
    out.append("")
    out.append(
        "chrF on the original file, split by domain. The `speech` column is"
        " the YouTube sourced data that the filter removes, so it is the"
        " only column that contributes to the delta. Every other column is"
        " unchanged by the filter."
    )
    out.append("")
    for lp, shared, deltas, _rank_a, _rank_b in details:
        domains = sorted(d for (l, d) in dom_a if l == lp)
        if not domains:
            continue
        # n is uniform across systems within a language pair and domain
        counts = {}
        for d in domains:
            systems_here = dom_a[(lp, d)]
            counts[d] = max((v[1] for v in systems_here.values()), default=0)
        out.append(f"#### `{lp}` by domain")
        out.append("")
        out.append(
            "segments per domain: "
            + ", ".join(f"{d} {counts[d]}" for d in domains)
        )
        out.append("")
        header = "| system | " + " | ".join(
            f"{d} (removed)" if d == YOUTUBE_DOMAIN else d for d in domains
        )
        out.append(header + " | all | all no YT | delta |")
        out.append("|---" * (len(domains) + 4) + "|")
        for system in sorted(shared, key=lambda s: (-lp_a[lp][s][0], s)):
            cells = []
            for d in domains:
                entry = dom_a[(lp, d)].get(system)
                cells.append(f"{entry[0]:.2f}" if entry else "")
            out.append(
                f"| {system} | "
                + " | ".join(cells)
                + f" | {lp_a[lp][system][0]:.2f} | {lp_b[lp][system][0]:.2f} |"
                f" {fmt_delta(deltas[system])} |"
            )
        out.append("")


# %%
out = []
out.append("# chrF with and without YouTube sourced documents")
out.append("")
out.append(
    "Effect of removing the YouTube sourced `speech` domain from the WMT25"
    " general MT human evaluation data on chrF."
)
out.append("")
out.append("## Method")
out.append("")
out.append(
    "* Metric is chrF2 from sacrebleu, character 6grams with beta 2 and no"
    " word ngrams, the configuration used for WMT reporting."
)
out.append(
    "* Scores are corpus level per language pair, and separately per"
    " language pair and domain. chrF is not comparable across languages,"
    " so nothing is pooled across language pairs."
)
out.append(
    f"* The reference is `{REFERENCE}`. A system is scored on the segments"
    " where the reference exists and that system produced an output."
    " Within a language pair and domain every system covers the same"
    " segments, so the segment count is reported once per group."
)
out.append(
    "* `delta` is the chrF on the YouTube free file minus the chrF on the"
    " original file. A positive delta means the system scores higher once"
    " YouTube documents are gone."
)
out.append(
    "* `rank` is the position of the system within its language pair, best"
    " first, ties broken by name. The bracketed number is how far the"
    " system moved."
)
out.append(
    "* Small domains give small segment counts, and a chrF over a handful"
    " of segments is noisy. The counts are reported so that those cells"
    " can be discounted."
)
out.append("")

for label, fname_a, fname_b in PAIRS:
    print(f"section: {label}", file=sys.stderr)
    build_section(label, fname_a, fname_b, out)

os.makedirs(os.path.dirname(REPORT), exist_ok=True)
with open(REPORT, "w") as f:
    f.write("\n".join(out).rstrip() + "\n")

print(f"wrote {REPORT}", file=sys.stderr)
