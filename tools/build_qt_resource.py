"""Generate Qt translation resource C++ in a fresh workspace."""

import argparse
import os
import subprocess
import sys
import tempfile

from pathlib import Path


TOOLS = Path(__file__).resolve().parent


def main():

    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument("--identity", required=True)
    parser.add_argument("--source-inventory", required=True)
    parser.add_argument("--templates", required=True)
    parser.add_argument("--lrelease", required=True)
    parser.add_argument("--rcc", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    output = Path(args.output).resolve()

    module = TOOLS.parent

    if module in output.parents:
        raise ValueError("Output overlaps module source")

    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix="localisation-work-",
        dir=output.parent,
    ) as workspace:

        root = Path(workspace)
        generated = root / "generated"
        candidate = root / "translations.cpp"

        subprocess.run([
            sys.executable,
            str(TOOLS / "build_localisation.py"),
            "--identity", args.identity,
            "--source-inventory", args.source_inventory,
            "--templates", args.templates,
            "--lrelease", args.lrelease,
            "--output", str(generated),
        ], check=True)

        # Fixed resource metadata timestamp.
        # This applies only to temporary compiled QM files.
        epoch = 946684800

        for path in sorted((generated / "qm").glob("*.qm")):
            os.utime(path, (epoch, epoch))

        environment = os.environ.copy()
        environment["SOURCE_DATE_EPOCH"] = str(epoch)

        subprocess.run([
            args.rcc,
            "--name", "xnuva_localisation",
            "--output", str(candidate),
            str(generated / "translations.qrc"),
        ], check=True, env=environment)

        # Canonicalise temporary paths in generated comments.
        # Resource payload and executable C++ remain untouched.
        content = candidate.read_text(encoding="utf-8")

        prefix = str(generated / "qm") + os.sep

        lines = content.splitlines(keepends=True)

        for index, line in enumerate(lines):

            if line.lstrip().startswith("//"):
                lines[index] = line.replace(
                    prefix,
                    "qm/",
                )

        candidate.write_text(
            "".join(lines),
            encoding="utf-8",
        )

        if not candidate.is_file():
            raise ValueError("Missing generated resource")

        if candidate.stat().st_size == 0:
            raise ValueError("Empty generated resource")

        # Publish only after complete successful generation.
        os.replace(candidate, output)

    print("PASS: Qt resource source generated:", output)


if __name__ == "__main__":
    main()
