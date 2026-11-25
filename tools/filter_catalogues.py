"""Project catalogues onto an authoritative application inventory.

Inherited catalogues remain immutable. Unreviewed branding
candidates may be suppressed in experimental output only.
"""

import argparse
import copy
import json
import re
import xml.etree.ElementTree as ET

from collections import Counter
from pathlib import Path

from generate_catalogues import serialise_catalogue


DEFAULT_PATTERN = (
    r"\b(?:bitcoin|bitcoins|btc|taox|taocoin|"
    r"satoshi|satoshis)\b"
)


def message_key(context, message):

    if message.get("id"):
        raise ValueError("ID-based translation requires review")

    source = message.find("source")

    if source is None or len(source):
        raise ValueError("Unsupported source structure")

    return (
        context,
        source.text or "",
        message.findtext("comment", ""),
        message.get("numerus", "no"),
    )


def source_inventory(root):

    if root.tag != "TS":
        raise ValueError("Invalid source inventory")

    keys = set()

    for context in root.findall("context"):

        name = context.findtext("name", "")

        for message in context.findall("message"):

            key = message_key(name, message)

            if key in keys:
                raise ValueError(
                    f"Duplicate source inventory key: {key}"
                )

            keys.add(key)

    if not keys:
        raise ValueError("Empty source inventory")

    return keys


def filter_catalogue(root, active, pattern):

    if root.tag != "TS":
        raise ValueError("Invalid catalogue root")

    result = copy.deepcopy(root)

    totals = Counter()
    findings = []

    for context in result.findall("context"):

        name = context.findtext("name", "")

        for message in context.findall("message"):

            totals["input_messages"] += 1

            key = message_key(name, message)

            if key not in active:

                context.remove(message)

                totals["excluded_inactive"] += 1
                continue

            translation = message.find("translation")

            text = (
                "".join(translation.itertext())
                if translation is not None
                else ""
            )

            source_match = bool(pattern.search(key[1]))
            translated_match = bool(pattern.search(text))

            if source_match:

                # Preserve source-level technical or historical
                # references for explicit engineering review.

                totals["active_source_candidates"] += 1

                findings.append({
                    "action": "review_active_source",
                    "key": key,
                    "translation": text,
                })

                totals["retained_unchanged"] += 1

            elif translated_match:

                # Conservative English fallback.
                # Never guess a translation or replace words
                # blindly inside a translated sentence.

                findings.append({
                    "action": "suppressed_translation",
                    "key": key,
                    "translation": text,
                })

                message.remove(translation)

                ET.SubElement(
                    message,
                    "translation",
                    {"type": "unfinished"},
                )

                totals["suppressed_translations"] += 1

            else:

                totals["retained_unchanged"] += 1

        if not context.findall("message"):
            result.remove(context)

    totals["output_messages"] = sum(
        1 for context in result.findall("context")
        for message in context.findall("message")
    )

    assert totals["input_messages"] == (
        totals["excluded_inactive"]
        + totals["suppressed_translations"]
        + totals["retained_unchanged"]
    )

    assert totals["output_messages"] == (
        totals["suppressed_translations"]
        + totals["retained_unchanged"]
    )

    return result, totals, findings


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--source-inventory", required=True)
    parser.add_argument("--catalogues", required=True)
    parser.add_argument("--output", required=True)

    parser.add_argument(
        "--legacy-pattern",
        default=DEFAULT_PATTERN,
    )

    args = parser.parse_args()

    inventory = ET.parse(
        args.source_inventory
    ).getroot()

    active = source_inventory(inventory)

    pattern = re.compile(
        args.legacy_pattern,
        re.IGNORECASE,
    )

    source = Path(args.catalogues).resolve()
    output = Path(args.output).resolve()

    if (
        source == output
        or source in output.parents
        or output in source.parents
    ):
        raise ValueError("Overlapping source/output paths")

    if output.exists():
        raise ValueError("Output directory already exists")

    files = sorted(source.glob("*.ts"))

    if not files:
        raise ValueError("No input catalogues")

    prepared = []
    totals = Counter()
    findings = []

    for path in files:

        root = ET.parse(path).getroot()

        filtered, counts, entries = filter_catalogue(
            root,
            active,
            pattern,
        )

        totals.update(counts)

        for entry in entries:
            entry["catalogue"] = path.name

        findings.extend(entries)

        prepared.append((
            path.name,
            serialise_catalogue(filtered),
        ))

    output.mkdir(parents=True)

    for name, content in prepared:
        (output / name).write_bytes(content)

    totals["catalogues"] = len(files)
    totals["active_source_keys"] = len(active)

    report = {
        "summary": dict(totals),
        "findings": findings,
        "policy": "experimental-conservative-fallback",
    }

    (output / "filter-report.json").write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )

    for key, value in sorted(totals.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
