"""Generate Qt resource aliases for project catalogues."""

import argparse
import json
import re
import xml.etree.ElementTree as ET

from pathlib import Path


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--identity", required=True)
    parser.add_argument("--qm-directory", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    identity = json.loads(
        Path(args.identity).read_text()
    )

    project = identity["project_id"]

    assert re.fullmatch(
        r"[a-z][a-z0-9-]*", project
    )

    directory = Path(args.qm_directory).resolve()
    output = Path(args.output).resolve()

    assert not output.exists()

    prefix = project + "_"

    root = ET.Element("RCC")

    resources = ET.SubElement(
        root,
        "qresource",
        {"prefix": "/translations"},
    )

    aliases = set()

    for path in sorted(directory.glob("*.qm")):

        assert path.name.startswith(prefix)
        assert path.stat().st_size > 0

        alias = path.stem[len(prefix):]

        assert re.fullmatch(
            r"[A-Za-z0-9_@-]+", alias
        )

        assert alias not in aliases

        aliases.add(alias)

        element = ET.SubElement(
            resources,
            "file",
            {"alias": alias},
        )

        element.text = str(path)

    assert aliases

    assert identity["fallback_language"] in aliases

    ET.indent(root, space="    ")

    ET.ElementTree(root).write(
        output,
        encoding="utf-8",
        xml_declaration=True,
    )

    print("Project:", project)
    print("Resource aliases:", len(aliases))
    print("PASS: project-independent resource aliases")


if __name__ == "__main__":
    main()
