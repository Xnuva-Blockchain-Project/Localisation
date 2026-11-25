"""Independently validate generated Qt catalogue integrity."""

import argparse
import copy
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter

from identity import load_identity, reject_duplicate_keys
from branding import render_mapping


BRANDING = re.compile(
    r"\b(?:bitcoin|bitcoins|btc|taox|taocoin|satoshi|satoshis)\b",
    re.IGNORECASE,
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(element):
    return (
        element.tag,
        tuple(sorted(element.attrib.items())),
        element.text,
        element.tail,
        tuple(canonical(child) for child in element),
    )


def validate_pair(original, generated, mapping):

    require(original.tag == "TS", "Invalid original root")
    require(generated.tag == "TS", "Invalid generated root")

    index = {
        (item["context"], item["old"]): item["new"]
        for item in mapping
    }

    require(
        len(index) == len(mapping),
        "Duplicate mapping keys",
    )

    reconstructed = copy.deepcopy(generated)

    old_contexts = original.findall("context")
    new_contexts = reconstructed.findall("context")

    require(
        len(old_contexts) == len(new_contexts),
        "Context count changed",
    )

    totals = Counter()

    for old_context, new_context in zip(
        old_contexts, new_contexts
    ):

        name = old_context.findtext("name", "")

        require(
            name == new_context.findtext("name", ""),
            "Context identity changed",
        )

        old_messages = old_context.findall("message")
        new_messages = new_context.findall("message")

        require(
            len(old_messages) == len(new_messages),
            f"Message count changed: {name}",
        )

        totals["contexts"] += 1

        for old, new in zip(old_messages, new_messages):

            totals["messages"] += 1

            source = old.findtext("source", "")
            key = (name, source)

            if old.get("numerus") == "yes":
                totals["plural_messages"] += 1

            if old.find("comment") is not None:
                totals["disambiguated_messages"] += 1

            if key not in index:

                require(
                    canonical(old) == canonical(new),
                    f"Unauthorised message change: {key}",
                )

                totals["unchanged_messages"] += 1
                continue

            require(
                old.attrib == new.attrib,
                f"Message metadata changed: {key}",
            )

            require(
                new.findtext("source") == index[key],
                f"Incorrect migrated source: {key}",
            )

            translations = new.findall("translation")

            require(
                len(translations) == 1,
                f"Invalid translation inventory: {key}",
            )

            translation = translations[0]

            require(
                translation.attrib == {"type": "unfinished"},
                f"Invalid fallback status: {key}",
            )

            require(
                not (translation.text or "").strip()
                and len(translation) == 0,
                f"Stale translated content: {key}",
            )

            new_source = new.find("source")
            old_source = old.find("source")

            require(
                new_source is not None
                and old_source is not None,
                f"Missing source: {key}",
            )

            position = list(new).index(new_source)

            new.remove(new_source)
            new.insert(position, copy.deepcopy(old_source))

            new.remove(translation)

            for pos, child in enumerate(old):
                if child.tag == "translation":
                    new.insert(pos, copy.deepcopy(child))

            require(
                canonical(old) == canonical(new),
                f"Unexpected migration side effect: {key}",
            )

            totals["migrated_messages"] += 1

    require(
        canonical(original) == canonical(reconstructed),
        "Unexpected catalogue-level modification",
    )

    return totals


def audit_branding(root, filename):

    findings = []

    for context in root.findall("context"):

        name = context.findtext("name", "")

        for message in context.findall("message"):

            source = message.findtext("source", "")

            translation = message.find("translation")

            text = (
                "".join(translation.itertext())
                if translation is not None
                else ""
            )

            if BRANDING.search(source) or BRANDING.search(text):

                findings.append({
                    "catalogue": filename,
                    "context": name,
                    "source": source,
                    "translation": text,
                    "source_match": bool(BRANDING.search(source)),
                    "translation_match": bool(BRANDING.search(text)),
                })

    return findings


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--identity", required=True)
    parser.add_argument("--templates", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--generated", required=True)
    parser.add_argument("--report", required=True)

    args = parser.parse_args()

    identity = load_identity(args.identity)

    templates = json.loads(
        Path(args.templates).read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_keys,
    )

    mapping = render_mapping(templates, identity)

    source = Path(args.source)
    generated = Path(args.generated)

    files = sorted(source.glob("*.ts"))

    require(bool(files), "No source catalogues")

    expected_names = {
        identity["project_id"] + "_" + path.name[len("bitcoin_"):]
        for path in files
    }

    actual_names = {
        path.name for path in generated.glob("*.ts")
    }

    require(
        actual_names == expected_names,
        "Generated catalogue inventory mismatch",
    )

    totals = Counter()
    findings = []

    for path in files:

        name = (
            identity["project_id"]
            + "_"
            + path.name[len("bitcoin_"):]
        )

        original = ET.parse(path).getroot()
        output = ET.parse(generated / name).getroot()

        totals.update(
            validate_pair(original, output, mapping)
        )

        findings.extend(audit_branding(output, name))

    totals["catalogues"] = len(files)
    totals["branding_candidate_messages"] = len(findings)

    report = {
        "summary": dict(totals),
        "branding_candidates": findings,
    }

    Path(args.report).write_text(
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
