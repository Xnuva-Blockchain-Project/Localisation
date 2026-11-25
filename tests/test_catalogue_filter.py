import re
import sys
import unittest
import xml.etree.ElementTree as ET

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from filter_catalogues import (
    DEFAULT_PATTERN,
    filter_catalogue,
    source_inventory,
)


FIXTURE = """
<TS version="2.1" language="es">
<context>
<name>Example</name>
<message>
<source>Settings</source>
<translation>Configuración</translation>
</message>
<message>
<source>Send coins</source>
<translation>Enviar bitcoins</translation>
</message>
<message>
<source>Old wallet message</source>
<translation>Mensaje antiguo</translation>
</message>
<message>
<source>Bitcoin protocol reference</source>
<translation>Referencia del protocolo Bitcoin</translation>
</message>
<message numerus="yes">
<source>%n coins</source>
<translation>
<numerusform>%n bitcoin</numerusform>
<numerusform>%n bitcoins</numerusform>
</translation>
</message>
</context>
</TS>
"""


class CatalogueFilterTests(unittest.TestCase):

    def setUp(self):

        self.root = ET.fromstring(FIXTURE)

        self.active = source_inventory(self.root)

        self.active.remove((
            "Example",
            "Old wallet message",
            "",
            "no",
        ))

        self.pattern = re.compile(
            DEFAULT_PATTERN,
            re.IGNORECASE,
        )

    def result(self):

        return filter_catalogue(
            self.root,
            self.active,
            self.pattern,
        )

    def test_obsolete_source_excluded(self):

        result, counts, _ = self.result()

        self.assertEqual(
            counts["excluded_inactive"], 1
        )

        self.assertNotIn(
            "Old wallet message",
            [x.text for x in result.iter("source")],
        )

    def test_stale_translation_suppressed(self):

        result, counts, _ = self.result()

        message = result.findall("context/message")[1]

        translation = message.find("translation")

        self.assertEqual(
            translation.get("type"), "unfinished"
        )

        self.assertFalse(translation.text)

        self.assertEqual(
            counts["suppressed_translations"], 2
        )

    def test_generic_translation_preserved(self):

        result, _, _ = self.result()

        self.assertEqual(
            result.findtext(
                "context/message/translation"
            ),
            "Configuración",
        )

    def test_technical_reference_preserved(self):

        result, counts, _ = self.result()

        self.assertEqual(
            counts["active_source_candidates"], 1
        )

        self.assertIn(
            "Referencia del protocolo Bitcoin",
            [x.text for x in result.iter("translation")],
        )

    def test_plural_metadata_preserved(self):

        result, _, _ = self.result()

        message = result.findall("context/message")[-1]

        self.assertEqual(
            message.get("numerus"), "yes"
        )

        self.assertEqual(
            message.findtext("source"), "%n coins"
        )

        self.assertEqual(
            len(message.find("translation")), 0
        )

    def test_original_catalogue_unchanged(self):

        before = ET.tostring(self.root)

        self.result()

        self.assertEqual(
            ET.tostring(self.root), before
        )

    def test_complete_message_accounting(self):

        _, counts, _ = self.result()

        self.assertEqual(counts["input_messages"], 5)
        self.assertEqual(counts["output_messages"], 4)

        self.assertEqual(
            counts["retained_unchanged"], 2
        )


if __name__ == "__main__":
    unittest.main()
