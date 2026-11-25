"""Presentation-only cryptocurrency identity validation."""

import json
import re
from pathlib import Path


REQUIRED_FIELDS = {
    "schema_version",
    "project_id",
    "project_name",
    "application_name",
    "organisation",
    "ticker",
    "base_unit_singular",
    "base_unit_plural",
    "executables",
    "payment_uri_label",
    "fallback_language",
}

EXECUTABLE_FIELDS = {
    "launcher",
    "daemon",
    "cli",
    "gui",
    "wallet",
    "transaction",
    "utility",
}


def require_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Invalid text field: {field}")

    if any(ord(char) < 32 for char in value):
        raise ValueError(f"Control character in {field}")

    if any(char in value for char in "{}%"):
        raise ValueError(f"Reserved character in {field}")

    return value


def validate_identity(data):
    if not isinstance(data, dict):
        raise ValueError("Identity must be a JSON object")

    if set(data) != REQUIRED_FIELDS:
        raise ValueError("Unexpected or missing identity fields")

    if type(data["schema_version"]) is not int:
        raise ValueError("Invalid schema version type")

    if data["schema_version"] != 1:
        raise ValueError("Unsupported identity schema")

    for field in REQUIRED_FIELDS - {
        "schema_version", "executables"
    }:
        require_text(data[field], field)

    if not re.fullmatch(
        r"[a-z][a-z0-9-]*", data["project_id"]
    ):
        raise ValueError("Invalid project identifier")

    if not re.fullmatch(
        r"[A-Z0-9]{2,10}", data["ticker"]
    ):
        raise ValueError("Invalid ticker")

    if not re.fullmatch(
        r"[a-z][a-z0-9+.-]*:",
        data["payment_uri_label"]
    ):
        raise ValueError("Invalid payment URI label")

    if data["fallback_language"] != "en":
        raise ValueError("Unsupported fallback language")

    executables = data["executables"]

    if not isinstance(executables, dict):
        raise ValueError("Invalid executable inventory")

    if set(executables) != EXECUTABLE_FIELDS:
        raise ValueError("Unexpected or missing executables")

    for field, value in executables.items():
        require_text(value, field)

        if not re.fullmatch(r"[A-Za-z0-9._-]+", value):
            raise ValueError(f"Invalid executable name: {field}")

        if value in {".", ".."}:
            raise ValueError(f"Invalid executable name: {field}")

    if len(set(executables.values())) != len(executables):
        raise ValueError("Duplicate executable names")

    return data


def reject_duplicate_keys(pairs):
    result = {}

    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value

    return result


def load_identity(path):
    data = json.loads(
        Path(path).read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_keys,
    )

    return validate_identity(data)
