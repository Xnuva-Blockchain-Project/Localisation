"""Build project-specific Qt localisation resources."""

import argparse
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET

from pathlib import Path

from identity import load_identity
from branding import render_mapping
from filter_catalogues import source_inventory


MODULE = Path(__file__).resolve().parents[1]
TOOLS = MODULE / "tools"


def digest(path):

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def run_tool(name, *arguments):

    subprocess.run(
        [
            sys.executable,
            str(TOOLS / name),
            *map(str, arguments),
        ],
        check=True,
    )


def main():

    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument("--identity", required=True)
    parser.add_argument("--source-inventory", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--lrelease", required=True)

    parser.add_argument(
        "--templates",
        default=str(
            MODULE /
            "migration/common-templates-v2.json"
        ),
    )

    parser.add_argument(
        "--legacy-pattern",
        default=None,
    )

    args = parser.parse_args()

    identity_path = Path(
        args.identity
    ).resolve(strict=True)

    inventory_path = Path(
        args.source_inventory
    ).resolve(strict=True)

    templates = Path(
        args.templates
    ).resolve(strict=True)

    lrelease = Path(
        args.lrelease
    ).resolve(strict=True)

    inherited = MODULE / "common/inherited/qt"

    output = Path(args.output).resolve()

    if output.exists():
        raise ValueError("Output directory already exists")

    if (
        output == MODULE
        or MODULE in output.parents
        or output in MODULE.parents
    ):
        raise ValueError("Output overlaps module source")

    identity = load_identity(identity_path)

    template_data = json.loads(
        templates.read_text(encoding="utf-8")
    )

    mapping = render_mapping(
        template_data,
        identity,
    )

    active = source_inventory(
        ET.parse(inventory_path).getroot()
    )

    for item in mapping:

        matching = [
            key for key in active
            if key[:2] == (
                item["context"], item["new"]
            )
        ]

        obsolete = [
            key for key in active
            if key[:2] == (
                item["context"], item["old"]
            )
        ]

        if not matching or obsolete:
            raise ValueError(
                f"Incompatible source mapping: {item}"
            )

    output.mkdir(parents=True)

    generated = output / "generated"
    filtered = output / "filtered"
    qm = output / "qm"
    logs = output / "logs"

    qm.mkdir()
    logs.mkdir()

    print("Project:", identity["project_id"], flush=True)
    print("Portable templates:", len(mapping), flush=True)
    print("Active source keys:", len(active), flush=True)

    run_tool(
        "generate_catalogues.py",
        "--identity", identity_path,
        "--templates", templates,
        "--source", inherited,
        "--output", generated,
    )

    run_tool(
        "validate_catalogues.py",
        "--identity", identity_path,
        "--templates", templates,
        "--source", inherited,
        "--generated", generated,
        "--report", output / "integrity-report.json",
    )

    filter_arguments = [
        "--source-inventory", inventory_path,
        "--catalogues", generated,
        "--output", filtered,
    ]

    if args.legacy_pattern is not None:

        filter_arguments.extend([
            "--legacy-pattern",
            args.legacy_pattern,
        ])

    run_tool(
        "filter_catalogues.py",
        *filter_arguments,
    )

    catalogues = sorted(filtered.glob("*.ts"))

    if not catalogues:
        raise ValueError("No filtered catalogues")

    for path in catalogues:

        destination = qm / (path.stem + ".qm")

        with (
            logs / (path.stem + ".log")
        ).open("wb") as log:

            subprocess.run(
                [
                    str(lrelease),
                    str(path),
                    "-qm",
                    str(destination),
                ],
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
            )

        if destination.stat().st_size == 0:
            raise ValueError(
                f"Empty compiled catalogue: {destination}"
            )

    run_tool(
        "generate_resources.py",
        "--identity", identity_path,
        "--qm-directory", qm,
        "--output", output / "translations.qrc",
    )

    report = {
        "project_id": identity["project_id"],
        "identity_sha256": digest(identity_path),
        "source_inventory_sha256": digest(inventory_path),
        "templates_sha256": digest(templates),
        "portable_templates": len(mapping),
        "active_source_keys": len(active),
        "catalogues": len(catalogues),
        "compiled_catalogues": {
            path.name: digest(path)
            for path in sorted(qm.glob("*.qm"))
        },
    }

    (output / "build-report.json").write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )

    print("Compiled catalogues:", len(catalogues))
    print("PASS: localisation build completed")


if __name__ == "__main__":
    main()
