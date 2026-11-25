import copy
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from generate_catalogues import generate_catalogue
from validate_catalogues import validate_pair, audit_branding


FIXTURE = """
<TS version="2.1" language="es">
<context>
<name>Example</name>
<message>
<source>Bitcoin wallet</source>
<translation>Cartera Bitcoin</translation>
</message>
<message>
<source>Settings</source>
<translation>Configuración</translation>
</message>
<message numerus="yes">
<source>%n Bitcoin connections</source>
<translation>
numerusform_placeholder
</translation>
</message>
</context>
</TS>
""".replace(
    "numerusform_placeholder",
    "<numerusform>%n conexión Bitcoin</numerusform>"
    "<numerusform>%n conexiones Bitcoin</numerusform>"
)

MAPPING = [
    {
        "context": "Example",
        "old": "Bitcoin wallet",
        "new": "Denzuve wallet",
    },
    {
        "context": "Example",
        "old": "%n Bitcoin connections",
        "new": "%n Denzuve connections",
    },
]


class CatalogueIntegrityTests(unittest.TestCase):

    def setUp(self):
        self.original = ET.fromstring(FIXTURE)

        self.generated, _ = generate_catalogue(
            self.original, MAPPING
        )

    def test_valid_generation(self):
        result = validate_pair(
            self.original, self.generated, MAPPING
        )

        self.assertEqual(result["messages"], 3)
        self.assertEqual(result["migrated_messages"], 2)
        self.assertEqual(result["unchanged_messages"], 1)

    def test_unrelated_translation_change_rejected(self):
        message = self.generated.findall(
            "context/message"
        )[1]

        message.find("translation").text = "Changed"

        with self.assertRaises(ValueError):
            validate_pair(
                self.original, self.generated, MAPPING
            )

    def test_context_change_rejected(self):
        self.generated.find("context/name").text = "Other"

        with self.assertRaises(ValueError):
            validate_pair(
                self.original, self.generated, MAPPING
            )

    def test_missing_message_rejected(self):
        context = self.generated.find("context")
        context.remove(context.find("message"))

        with self.assertRaises(ValueError):
            validate_pair(
                self.original, self.generated, MAPPING
            )

    def test_stale_translation_rejected(self):
        self.generated.find(
            "context/message/translation"
        ).text = "Cartera Bitcoin"

        with self.assertRaises(ValueError):
            validate_pair(
                self.original, self.generated, MAPPING
            )

    def test_plural_metadata_change_rejected(self):
        message = self.generated.findall(
            "context/message"
        )[2]

        del message.attrib["numerus"]

        with self.assertRaises(ValueError):
            validate_pair(
                self.original, self.generated, MAPPING
            )

    def test_language_change_rejected(self):
        self.generated.set("language", "fr")

        with self.assertRaises(ValueError):
            validate_pair(
                self.original, self.generated, MAPPING
            )

    def test_incorrect_source_key_rejected(self):
        self.generated.find(
            "context/message/source"
        ).text = "Incorrect wallet"

        with self.assertRaises(ValueError):
            validate_pair(
                self.original, self.generated, MAPPING
            )

    def test_branding_audit(self):
        findings = audit_branding(
            self.original, "fixture.ts"
        )

        self.assertEqual(len(findings), 2)

    def test_validator_does_not_modify_inputs(self):
        before = ET.tostring(self.generated)

        validate_pair(
            self.original, self.generated, MAPPING
        )

        self.assertEqual(
            before, ET.tostring(self.generated)
        )


if __name__ == "__main__":
    unittest.main()
