"""Independently qualify filtered Qt translation catalogues."""

import argparse
import copy
import json
import re
import xml.etree.ElementTree as ET

from collections import Counter
from pathlib import Path


LEGACY = re.compile(
    r"\b(?:bitcoin|bitcoins|btc|taox|taocoin|"
    r"satoshi|satoshis)\b",
    re.IGNORECASE,
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inventory(path):
    root = ET.parse(path).getroot()

    require(root.tag == "TS", f"Invalid TS file: {path}")

    result = {}

    for context in root.findall("context"):

        name = context.findtext("name", "")

        for message in context.findall("message"):

            key = (
                name,
                message.findtext("source", ""),
                message.findtext("comment", ""),
                message.get("numerus", "no"),
            )

            require(
                key not in result,
                f"Duplicate key: {key}"
            )

            result[key] = message

    return root, result


def canonical(element):
    return (
        element.tag,
        tuple(sorted(element.attrib.items())),
        element.text,
        element.tail,
        tuple(canonical(x) for x in element),
    )


def comparison_key(element):
    clone = copy.deepcopy(element)

    # Ignore formatting whitespace outside the message.
    clone.tail = None

    return canonical(clone)


def runtime_record(key, action):

    return {
        "context": key[0],
        "source": key[1],
        "comment": key[2],
        "numerus": key[3] == "yes",
        "action": action,
    }


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--inventory", required=True)
    parser.add_argument("--expanded", required=True)
    parser.add_argument("--filtered", required=True)
    parser.add_argument("--runtime-input", required=True)
    parser.add_argument("--report", required=True)

    args = parser.parse_args()

    _, active = inventory(args.inventory)

    expanded = Path(args.expanded)
    filtered = Path(args.filtered)
    runtime = Path(args.runtime_input)

    old_files = sorted(expanded.glob("*.ts"))
    new_files = sorted(filtered.glob("*.ts"))

    require(
        [x.name for x in old_files]
        == [x.name for x in new_files],
        "Catalogue inventory changed",
    )

    totals = Counter()
    coverage = []

    for path in old_files:

        old_root, old = inventory(path)

        new_root, new = inventory(
            filtered / path.name
        )

        require(
            old_root.attrib == new_root.attrib,
            f"Catalogue metadata changed: {path.name}",
        )

        expected = set(old) & set(active)

        require(
            set(new) == expected,
            f"Incorrect active message inventory: {path.name}",
        )

        records = []
        counts = Counter()

        counts["input_messages"] = len(old)
        counts["output_messages"] = len(new)

        counts["excluded_inactive"] = len(
            set(old) - set(active)
        )

        counts["missing_active_keys"] = len(
            set(active) - set(new)
        )

        for key, before in old.items():

            if key not in active:
                continue

            after = new[key]

            translation = before.find("translation")

            old_text = (
                "".join(translation.itertext())
                if translation is not None
                else ""
            )

            suppress = (
                not LEGACY.search(key[1])
                and bool(LEGACY.search(old_text))
            )

            if suppress:

                updated = after.find("translation")

                require(
                    updated is not None,
                    f"Missing fallback marker: {key}",
                )

                require(
                    updated.attrib == {
                        "type": "unfinished"
                    },
                    f"Invalid fallback status: {key}",
                )

                require(
                    not (updated.text or "").strip()
                    and len(updated) == 0,
                    f"Stale translation retained: {key}",
                )

                # Restore the original translation in a copy
                # and verify that nothing else changed.
                restored = copy.deepcopy(after)

                restored.remove(
                    restored.find("translation")
                )

                position = list(before).index(
                    translation
                )

                restored.insert(
                    position,
                    copy.deepcopy(translation),
                )

                require(
                    comparison_key(restored)
                    == comparison_key(before),
                    f"Unexpected suppression side effect: {key}",
                )

                counts["suppressed_translations"] += 1

                records.append(
                    runtime_record(key, "fallback")
                )

            else:

                require(
                    comparison_key(before)
                    == comparison_key(after),
                    f"Unauthorised retained-message change: {key}",
                )

                counts["retained_unchanged"] += 1

                records.append(
                    runtime_record(key, "preserved")
                )

            translated = after.find("translation")

            if (
                translated is not None
                and "".join(
                    translated.itertext()
                ).strip()
            ):
                counts["nonempty_translation_entries"] += 1

                if translated.get("type") != "unfinished":
                    counts["nonempty_finished_entries"] += 1

            else:
                counts["empty_translation_entries"] += 1

            if LEGACY.search(key[1]):
                counts["active_source_branding"] += 1

            if translated is not None:

                text = "".join(
                    translated.itertext()
                )

                if LEGACY.search(text):
                    counts["residual_translation_branding"] += 1

        require(
            counts["input_messages"] == (
                counts["excluded_inactive"]
                + counts["retained_unchanged"]
                + counts["suppressed_translations"]
            ),
            "Incorrect message accounting",
        )

        totals.update(counts)

        coverage.append({
            "catalogue": path.name,
            **dict(counts),
        })

        (runtime / (path.stem + ".json")).write_text(
            json.dumps(
                records,
                ensure_ascii=False,
                sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )

    totals["catalogues"] = len(old_files)
    totals["active_source_keys"] = len(active)

    report = {
        "summary": dict(totals),
        "coverage": coverage,
    }

    Path(args.report).write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )

    for key, value in sorted(totals.items()):
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
