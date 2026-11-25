import copy
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from generate_catalogues import (
    generate_catalogue,
    serialise_catalogue,
)


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
        <numerusform>%n conexión Bitcoin</numerusform>
        <numerusform>%n conexiones Bitcoin</numerusform>
      </translation>
    </message>
  </context>
</TS>
"""

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


class CatalogueGeneratorTests(unittest.TestCase):

    def setUp(self):
        self.root = ET.fromstring(FIXTURE)

    def test_source_key_migration(self):
        result, count = generate_catalogue(
            self.root, MAPPING
        )

        self.assertEqual(count, 2)

        sources = [
            node.text for node in result.iter("source")
        ]

        self.assertIn("Denzuve wallet", sources)
        self.assertNotIn("Bitcoin wallet", sources)

    def test_unaffected_translation_preserved(self):
        result, _ = generate_catalogue(
            self.root, MAPPING
        )

        original = self.root.findall(
            "context/message"
        )[1]

        generated = result.findall(
            "context/message"
        )[1]

        self.assertEqual(
            ET.tostring(original),
            ET.tostring(generated),
        )

    def test_stale_translation_removed(self):
        result, _ = generate_catalogue(
            self.root, MAPPING
        )

        translation = result.find(
            "context/message/translation"
        )

        self.assertEqual(
            translation.get("type"), "unfinished"
        )

        self.assertFalse(translation.text)
        self.assertEqual(len(translation), 0)

    def test_plural_metadata_preserved(self):
        result, _ = generate_catalogue(
            self.root, MAPPING
        )

        message = result.findall(
            "context/message"
        )[2]

        self.assertEqual(
            message.get("numerus"), "yes"
        )

        self.assertEqual(
            message.findtext("source"),
            "%n Denzuve connections",
        )

        self.assertFalse(
            message.find("translation").findall(
                "numerusform"
            )
        )

    def test_original_tree_unchanged(self):
        original = ET.tostring(self.root)

        generate_catalogue(self.root, MAPPING)

        self.assertEqual(
            ET.tostring(self.root), original
        )

    def test_deterministic_output(self):
        first, _ = generate_catalogue(
            self.root, MAPPING
        )

        second, _ = generate_catalogue(
            self.root, MAPPING
        )

        self.assertEqual(
            serialise_catalogue(first),
            serialise_catalogue(second),
        )

    def test_key_collision_rejected(self):
        context = self.root.find("context")

        message = ET.SubElement(context, "message")

        ET.SubElement(
            message, "source"
        ).text = "Denzuve wallet"

        with self.assertRaises(ValueError):
            generate_catalogue(self.root, MAPPING)

    def test_ambiguous_key_rejected(self):
        context = self.root.find("context")

        context.append(
            copy.deepcopy(context.find("message"))
        )

        with self.assertRaises(ValueError):
            generate_catalogue(self.root, MAPPING)

    def test_disambiguation_requires_review(self):
        message = self.root.find("context/message")

        ET.SubElement(
            message, "comment"
        ).text = "Specific meaning"

        with self.assertRaises(ValueError):
            generate_catalogue(self.root, MAPPING)

    def test_invalid_root_rejected(self):
        with self.assertRaises(ValueError):
            generate_catalogue(
                ET.Element("invalid"), MAPPING
            )


if __name__ == "__main__":
    unittest.main()
