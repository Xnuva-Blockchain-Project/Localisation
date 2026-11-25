"""Render explicitly reviewed presentation templates."""

import argparse
import json
import re
from pathlib import Path

from identity import load_identity, validate_identity


TOKEN = re.compile(r"\{\{([a-z_]+)\}\}")
PLACEHOLDER = re.compile(r"%(?:L?\d+|Ln|n)")


def branding_values(identity):
    identity = validate_identity(identity)

    values = {
        key: value
        for key, value in identity.items()
        if isinstance(value, str)
    }

    values.update({
        f"executable_{key}": value
        for key, value in identity["executables"].items()
    })

    return values


def render_template(template, identity):
    if not isinstance(template, str) or not template:
        raise ValueError("Invalid branding template")

    values = branding_values(identity)

    def replace(match):
        key = match.group(1)

        if key not in values:
            raise ValueError(f"Unknown branding token: {key}")

        return values[key]

    result = TOKEN.sub(replace, template)

    if "{" in result or "}" in result:
        raise ValueError("Unresolved branding token")

    if sorted(PLACEHOLDER.findall(template)) != sorted(
        PLACEHOLDER.findall(result)
    ):
        raise ValueError("Translation placeholders changed")

    return result


def render_mapping(mapping, identity):
    if not isinstance(mapping, list):
        raise ValueError("Mapping must be a list")

    result = []
    old_keys = set()
    new_keys = set()

    for entry in mapping:
        if set(entry) != {"context", "old", "template"}:
            raise ValueError("Unexpected mapping fields")

        context = entry["context"]
        old = entry["old"]

        if not isinstance(context, str) or not context:
            raise ValueError("Missing translation context")

        if not isinstance(old, str) or not old:
            raise ValueError("Missing original source key")

        new = render_template(entry["template"], identity)

        if sorted(PLACEHOLDER.findall(old)) != sorted(
            PLACEHOLDER.findall(new)
        ):
            raise ValueError("Source placeholders changed")

        old_key = (context, old)
        new_key = (context, new)

        if old_key in old_keys or new_key in new_keys:
            raise ValueError("Duplicate translation key")

        old_keys.add(old_key)
        new_keys.add(new_key)

        result.append({
            "context": context,
            "old": old,
            "new": new,
        })

    if not result:
        raise ValueError("Empty branding mapping")

    return result


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--identity", required=True)
    parser.add_argument("--templates", required=True)

    args = parser.parse_args()

    identity = load_identity(args.identity)

    mapping = json.loads(
        Path(args.templates).read_text(encoding="utf-8")
    )

    print(json.dumps(
        render_mapping(mapping, identity),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
