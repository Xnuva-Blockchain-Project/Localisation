"""Generate native Qt TS catalogues from reviewed branding maps."""

import argparse
import copy
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from identity import load_identity, reject_duplicate_keys
from branding import render_mapping


def catalogue_keys(root):
    keys = set()

    for context in root.findall("context"):
        name = context.findtext("name", "")

        for message in context.findall("message"):
            source = message.findtext("source", "")
            comment = message.findtext("comment", "")

            key = (name, source, comment)

            if key in keys:
                raise ValueError(
                    f"Duplicate translation key: {key}"
                )

            keys.add(key)

    return keys


def generate_catalogue(root, mapping):

    if root.tag != "TS":
        raise ValueError("Invalid Qt TS root")

    result = copy.deepcopy(root)

    index = {
        (item["context"], item["old"]): item["new"]
        for item in mapping
    }

    if len(index) != len(mapping):
        raise ValueError("Duplicate migration key")

    changed = 0

    for context in result.findall("context"):
        name = context.findtext("name", "")

        matches = {}

        for message in context.findall("message"):
            source = message.findtext("source", "")
            key = (name, source)

            if key in index:
                matches.setdefault(key, []).append(message)

        for key, messages in matches.items():

            if len(messages) != 1:
                raise ValueError(
                    f"Ambiguous migration key: {key}"
                )

            message = messages[0]

            if message.find("comment") is not None:
                raise ValueError(
                    f"Disambiguation review required: {key}"
                )

            if message.get("id"):
                raise ValueError(
                    f"ID-based translation requires review: {key}"
                )

            source = message.find("source")

            if source is None or len(source):
                raise ValueError(
                    f"Complex source requires review: {key}"
                )

            new_text = index[key]

            if source.text == new_text:
                continue

            source.text = new_text

            translation = message.find("translation")

            if translation is not None:
                message.remove(translation)

            translation = ET.SubElement(
                message,
                "translation",
                {"type": "unfinished"},
            )

            # No stale translated branding is retained.
            # Preserve the message's numerus attribute.
            # Empty translations require runtime fallback
            # qualification before integration.

            changed += 1

    catalogue_keys(result)

    return result, changed


def serialise_catalogue(root):
    return (
        b'<?xml version="1.0" encoding="utf-8"?>\n'
        b'<!DOCTYPE TS>\n'
        + ET.tostring(root, encoding="utf-8")
        + b"\n"
    )


def generate_directory(source, destination, identity, mapping):

    source = Path(source).resolve()
    destination = Path(destination).resolve()

    if (
        source == destination
        or source in destination.parents
        or destination in source.parents
    ):
        raise ValueError("Source/output directories overlap")

    if destination.exists():
        raise ValueError("Output directory already exists")

    files = sorted(source.glob("*.ts"))

    if not files:
        raise ValueError("No inherited catalogues found")

    prepared = []
    report = []

    for path in files:

        if not path.name.startswith("bitcoin_") and not (
            path.name.startswith("bitcoin_zh-")
        ):
            raise ValueError(
                f"Unexpected catalogue filename: {path.name}"
            )

        root = ET.parse(path).getroot()

        generated, changed = generate_catalogue(
            root, mapping
        )

        suffix = path.name[len("bitcoin_"):]

        output_name = (
            identity["project_id"] + "_" + suffix
        )

        prepared.append((
            output_name,
            serialise_catalogue(generated)
        ))

        report.append({
            "source": path.name,
            "output": output_name,
            "changed_keys": changed,
        })

    destination.mkdir(parents=True)

    for name, content in prepared:
        (destination / name).write_bytes(content)

    summary = {
        "project_id": identity["project_id"],
        "catalogues": len(report),
        "changed_keys": sum(
            item["changed_keys"] for item in report
        ),
        "files": report,
    }

    (destination / "generation-report.json").write_text(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    return summary


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--identity", required=True)
    parser.add_argument("--templates", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    identity = load_identity(args.identity)

    templates = json.loads(
        Path(args.templates).read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_keys,
    )

    mapping = render_mapping(templates, identity)

    report = generate_directory(
        args.source,
        args.output,
        identity,
        mapping,
    )

    print("Project:", report["project_id"])
    print("Catalogues:", report["catalogues"])
    print("Changed source keys:", report["changed_keys"])


if __name__ == "__main__":
    main()
