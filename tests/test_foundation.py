import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LocalisationFoundationTests(unittest.TestCase):

    def setUp(self):
        self.identity = json.loads(
            (ROOT / "identity/denzuve.json").read_text()
        )

        self.schema = json.loads(
            (ROOT / "schema/identity-v1.json").read_text()
        )

        self.mapping = json.loads(
            (
                ROOT / "migration/"
                "denzuve-gui-source-keys.json"
            ).read_text()
        )

    def test_required_identity_fields(self):
        self.assertEqual(
            set(self.identity),
            set(self.schema["required"])
        )

    def test_schema_version(self):
        self.assertEqual(
            self.identity["schema_version"], 1
        )

    def test_coin_identity(self):
        self.assertEqual(
            self.identity["project_name"], "Denzuve"
        )
        self.assertEqual(
            self.identity["ticker"], "DZUV"
        )

    def test_denomination_labels(self):
        self.assertEqual(
            self.identity["base_unit_singular"],
            "Princeps"
        )
        self.assertEqual(
            self.identity["base_unit_plural"],
            "Principes"
        )

    def test_english_fallback(self):
        self.assertEqual(
            self.identity["fallback_language"], "en"
        )

    def test_executable_inventory(self):
        expected = {
            "denzuve",
            "denzuved",
            "denzuve-cli",
            "denzuve-qt",
            "denzuve-wallet",
            "denzuve-tx",
            "denzuve-util"
        }

        self.assertEqual(
            set(self.identity["executables"].values()),
            expected
        )

    def test_migration_inventory(self):
        self.assertEqual(len(self.mapping), 15)

    def test_unique_migration_keys(self):
        keys = [
            (item["context"], item["old"])
            for item in self.mapping
        ]

        self.assertEqual(len(keys), len(set(keys)))

    def test_migration_placeholders(self):
        pattern = r"%(?:L?\d+|Ln|n)"

        for item in self.mapping:
            with self.subTest(context=item["context"]):
                self.assertEqual(
                    sorted(re.findall(
                        pattern, item["old"]
                    )),
                    sorted(re.findall(
                        pattern, item["new"]
                    ))
                )

    def test_migration_changes_are_nonempty(self):
        for item in self.mapping:
            self.assertTrue(item["context"])
            self.assertTrue(item["old"])
            self.assertTrue(item["new"])

            self.assertNotEqual(
                item["old"], item["new"]
            )

    def test_inherited_catalogues_retained(self):
        locale = ROOT / "common/inherited/qt"

        self.assertEqual(
            len(list(locale.glob("*.ts"))),
            100
        )


if __name__ == "__main__":
    unittest.main()
