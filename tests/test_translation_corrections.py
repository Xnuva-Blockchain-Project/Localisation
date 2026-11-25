import copy
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from pathlib import Path
from unittest.mock import patch

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "tools")
)

import translation_corrections as corrections


class TranslationCorrectionTests(unittest.TestCase):

    def setUp(self):

        temporary = tempfile.TemporaryDirectory()

        self.addCleanup(temporary.cleanup)

        self.directory = Path(temporary.name)

        self.rule = {
            "language": "xx",
            "context": "Example",
            "source": "Amount: %1",
            "comment": "",
            "numerus": "no",
            "original_forms": ["Incorrect amount"],
            "replacement_forms": ["Correct amount: %1"],
            "original_attributes": {
                "type": "unfinished"
            },
            "review_status": "provisional",
            "category": "formatting"
        }

    def write_catalogue(
        self,
        project="example",
        text="Incorrect amount"
    ):

        root = ET.Element("TS", {"language": "xx"})

        context = ET.SubElement(root, "context")

        ET.SubElement(context, "name").text = "Example"

        message = ET.SubElement(context, "message")

        ET.SubElement(message, "source").text = \
            "Amount: %1"

        ET.SubElement(
            message,
            "translation",
            {"type": "unfinished"}
        ).text = text

        unrelated = ET.SubElement(context, "message")

        ET.SubElement(unrelated, "source").text = \
            "Unrelated"

        ET.SubElement(unrelated, "translation").text = \
            "Preserved text"

        path = self.directory / f"{project}_xx.ts"

        ET.ElementTree(root).write(
            path,
            encoding="utf-8",
            xml_declaration=True
        )

        return path

    def apply(self, project="example", rules=None):

        if rules is None:
            rules = [self.rule]

        with patch.object(corrections, "RULES", rules):

            return corrections.apply_translation_corrections(
                self.directory, project
            )

    def test_exact_correction(self):

        path = self.write_catalogue()

        report = self.apply()

        translation = ET.parse(path).find(
            "./context/message/translation"
        )

        self.assertEqual(report["applied"], 1)

        self.assertEqual(
            translation.text, "Correct amount: %1"
        )

        self.assertEqual(
            translation.get("type"), "unfinished"
        )

    def test_unrelated_translation_preserved(self):

        path = self.write_catalogue()

        self.apply()

        messages = ET.parse(path).findall(
            "./context/message"
        )

        self.assertEqual(
            messages[1].findtext("translation"),
            "Preserved text"
        )

    def test_changed_original_rejected(self):

        path = self.write_catalogue(
            text="Unexpected translation"
        )

        before = path.read_bytes()

        with self.assertRaises(ValueError):
            self.apply()

        self.assertEqual(path.read_bytes(), before)

    def test_changed_attributes_rejected(self):

        path = self.write_catalogue()

        root = ET.parse(path).getroot()

        root.find(
            "./context/message/translation"
        ).attrib.clear()

        ET.ElementTree(root).write(path)

        before = path.read_bytes()

        with self.assertRaises(ValueError):
            self.apply()

        self.assertEqual(path.read_bytes(), before)

    def test_missing_catalogue_reported(self):

        report = self.apply()

        self.assertEqual(report["applied"], 0)
        self.assertEqual(report["skipped"], 1)

        self.assertEqual(
            report["skipped_rules"][0]["reason"],
            "catalogue_not_present"
        )

    def test_project_independent_application(self):

        self.write_catalogue(project="anothercoin")

        report = self.apply("anothercoin")

        self.assertEqual(report["applied"], 1)

    def test_missing_source_key_reported(self):

        self.write_catalogue()

        self.rule["source"] = "Unknown source"

        report = self.apply()

        self.assertEqual(report["applied"], 0)

        self.assertEqual(
            report["skipped_rules"][0]["reason"],
            "source_key_not_present"
        )

    def test_ambiguous_source_rejected(self):

        path = self.write_catalogue()

        root = ET.parse(path).getroot()
        context = root.find("context")

        context.append(
            copy.deepcopy(context.find("message"))
        )

        ET.ElementTree(root).write(path)

        before = path.read_bytes()

        with self.assertRaises(ValueError):
            self.apply()

        self.assertEqual(path.read_bytes(), before)

    def test_plural_forms_preserved(self):

        path = self.write_catalogue()

        root = ET.parse(path).getroot()

        message = root.find("./context/message")

        message.set("numerus", "yes")

        message.find("source").text = "%n items"

        translation = message.find("translation")
        translation.text = None

        ET.SubElement(
            translation, "numerusform"
        ).text = "One item"

        ET.SubElement(
            translation, "numerusform"
        ).text = "Many items"

        ET.ElementTree(root).write(path)

        self.rule["source"] = "%n items"
        self.rule["numerus"] = "yes"

        self.rule["original_forms"] = [
            "One item", "Many items"
        ]

        self.rule["replacement_forms"] = [
            "%n item", "%n items"
        ]

        report = self.apply()

        self.assertEqual(report["applied"], 1)

        forms = ET.parse(path).findall(
            "./context/message/translation/numerusform"
        )

        self.assertEqual(
            [form.text for form in forms],
            ["%n item", "%n items"]
        )

    def test_validation_failure_prevents_writes(self):

        path = self.write_catalogue()

        before = path.read_bytes()

        invalid = copy.deepcopy(self.rule)

        invalid["source"] = "Unrelated"

        invalid["original_forms"] = [
            "Wrong expected text"
        ]

        with self.assertRaises(ValueError):

            self.apply(
                rules=[self.rule, invalid]
            )

        self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
