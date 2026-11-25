import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "tools"))

from identity import load_identity
from branding import render_mapping


class ExpandedTemplateTests(unittest.TestCase):

    def setUp(self):

        self.identity = load_identity(
            ROOT / "identity/denzuve.json"
        )

        self.original = json.loads(
            (
                ROOT /
                "migration/common-gui-templates.json"
            ).read_text()
        )

        self.expanded = json.loads(
            (
                ROOT /
                "migration/common-templates-v2.json"
            ).read_text()
        )

    def test_original_inventory_preserved(self):

        self.assertEqual(len(self.original), 15)

        self.assertEqual(
            self.expanded[:15],
            self.original,
        )

    def test_expanded_inventory(self):

        self.assertEqual(len(self.expanded), 25)

        mapping = render_mapping(
            self.expanded,
            self.identity,
        )

        self.assertEqual(len(mapping), 25)

    def test_retired_intro_key_excluded(self):

        self.assertFalse(any(
            item["context"] == "Intro"
            and item["old"] == "Bitcoin"
            for item in self.expanded
        ))

    def test_core_wallet_placeholder(self):

        mapping = render_mapping(
            self.expanded,
            self.identity,
        )

        core = [
            item for item in mapping
            if item["context"] == "bitcoin-core"
        ]

        self.assertEqual(len(core), 1)

        self.assertEqual(core[0]["old"].count("%s"), 1)
        self.assertEqual(core[0]["new"].count("%s"), 1)

        self.assertIn(
            "denzuve-wallet",
            core[0]["new"],
        )

        self.assertIn(
            "version 1 dumpfiles",
            core[0]["new"],
        )

    def test_five_coin_expanded_portability(self):

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
                    self.expanded,
                    identity,
                )

                self.assertEqual(len(result), 25)

                core = next(
                    item for item in result
                    if item["context"] == "bitcoin-core"
                )

                self.assertIn(
                    project + "-wallet",
                    core["new"],
                )

                self.assertEqual(
                    core["new"].count("%s"), 1
                )

                if name != "Denzuve":

                    self.assertFalse(any(
                        "denzuve" in item["new"].lower()
                        for item in result
                    ))


if __name__ == "__main__":
    unittest.main()
