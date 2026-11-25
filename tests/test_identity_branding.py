import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from identity import load_identity, validate_identity
from branding import render_mapping, render_template


class IdentityBrandingTests(unittest.TestCase):

    def setUp(self):
        self.identity = load_identity(
            ROOT / "identity/denzuve.json"
        )

        self.templates = json.loads(
            (
                ROOT /
                "migration/common-gui-templates.json"
            ).read_text()
        )

    def test_valid_identity(self):
        self.assertEqual(
            validate_identity(self.identity)["ticker"],
            "DZUV",
        )

    def test_missing_field_rejected(self):
        del self.identity["ticker"]

        with self.assertRaises(ValueError):
            validate_identity(self.identity)

    def test_unexpected_field_rejected(self):
        self.identity["consensus"] = {}

        with self.assertRaises(ValueError):
            validate_identity(self.identity)

    def test_invalid_ticker_rejected(self):
        self.identity["ticker"] = "dzuv"

        with self.assertRaises(ValueError):
            validate_identity(self.identity)

    def test_invalid_schema_version(self):
        self.identity["schema_version"] = True

        with self.assertRaises(ValueError):
            validate_identity(self.identity)

    def test_invalid_executable_rejected(self):
        self.identity["executables"]["daemon"] = "../daemon"

        with self.assertRaises(ValueError):
            validate_identity(self.identity)

    def test_unknown_token_rejected(self):
        with self.assertRaises(ValueError):
            render_template(
                "{{unknown_field}}",
                self.identity
            )

    def test_malformed_token_rejected(self):
        with self.assertRaises(ValueError):
            render_template(
                "{{project_name}",
                self.identity
            )

    def test_placeholder_change_rejected(self):
        mapping = [{
            "context": "Example",
            "old": "%1 wallet",
            "template": "{{project_name}} wallet",
        }]

        with self.assertRaises(ValueError):
            render_mapping(mapping, self.identity)

    def test_duplicate_mapping_rejected(self):
        mapping = self.templates + [self.templates[0]]

        with self.assertRaises(ValueError):
            render_mapping(mapping, self.identity)

    def test_plural_placeholder_preserved(self):
        self.assertEqual(
            render_template(
                "%n {{project_name}} connections",
                self.identity
            ),
            "%n Denzuve connections",
        )

    def test_denzuve_exact_equivalence(self):
        original = json.loads(
            (
                ROOT /
                "migration/denzuve-gui-source-keys.json"
            ).read_text()
        )

        expected = [
            {key: item[key] for key in ("context", "old", "new")}
            for item in original
        ]

        self.assertEqual(
            render_mapping(self.templates, self.identity),
            expected,
        )

    def test_five_coin_portability(self):
        coins = [
            ("Denzuve", "DZUV"),
            ("Aurzola", "AUZV"),
            ("Sestovi", "SEZQ"),
            ("Asveru", "ASVR"),
            ("Duprezo", "DPZE"),
        ]

        for name, ticker in coins:
            with self.subTest(coin=name):
                identity = copy.deepcopy(self.identity)
                project = name.lower()

                identity.update({
                    "project_id": project,
                    "project_name": name,
                    "application_name": name + " Core",
                    "ticker": ticker,
                    "payment_uri_label": project + ":",
                })

                identity["executables"] = {
                    "launcher": project,
                    "daemon": project + "d",
                    "cli": project + "-cli",
                    "gui": project + "-qt",
                    "wallet": project + "-wallet",
                    "transaction": project + "-tx",
                    "utility": project + "-util",
                }

                result = render_mapping(
                    self.templates, identity
                )

                self.assertEqual(len(result), 15)

                self.assertTrue(
                    any(name in item["new"] for item in result)
                )

                self.assertEqual(
                    render_template(
                        "{{ticker}} / {{base_unit_singular}}",
                        identity
                    ),
                    ticker + " / Princeps",
                )

                self.assertEqual(
                    render_template(
                        "{{executable_daemon}}",
                        identity
                    ),
                    project + "d",
                )

                self.assertEqual(
                    render_template(
                        "{{base_unit_plural}}",
                        identity
                    ),
                    "Principes",
                )

                if name != "Denzuve":
                    self.assertFalse(
                        any(
                            "Denzuve" in item["new"]
                            for item in result
                        )
                    )


if __name__ == "__main__":
    unittest.main()
