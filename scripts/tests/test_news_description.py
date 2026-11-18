import os
import sys
import unittest
from pathlib import Path

# fetch_news construit un client OpenAI à l'import : une clé factice suffit.
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import fetch_news  # noqa: E402


class NewsDescriptionTests(unittest.TestCase):
    def test_markdown_and_media_name_never_leak(self):
        summary = (
            "EmilyCC, la streameuse qui diffuse sa vie en direct sur Twitch depuis "
            "cinq ans Le Monde.fr. ## EmilyCC, cinq ans de vie en direct sur Twitch "
            "Le Monde.fr met en…"
        )
        body = (
            "EmilyCC diffuse sa vie en direct depuis cinq ans. Elle raconte son "
            "quotidien, son setup et sa régularité de stream."
        )
        desc = fetch_news.build_description(summary, body)
        self.assertNotIn("#", desc)
        self.assertNotIn("Le Monde.fr", desc)
        self.assertLessEqual(len(desc), 160)
        self.assertGreaterEqual(len(desc), 80)

    def test_truncated_summary_is_replaced_by_body(self):
        summary = (
            "En Espagne, une enquête ouverte contre TikTok pour diffusion présumée "
            "de contenus pédocriminels Le Monde.fr. ## Une enquête en Espagne En…"
        )
        body = (
            "Une enquête a été ouverte en Espagne contre TikTok. "
            "La plateforme est accusée de diffusion présumée de contenus pédocriminels."
        )
        desc = fetch_news.build_description(summary, body)
        self.assertNotIn("…", desc)
        self.assertNotIn("#", desc)
        self.assertTrue(desc.startswith("Une enquête"))

    def test_markdown_heading_is_not_a_description(self):
        desc = fetch_news.build_description("", "## TikTok Shop change la logistique\nLe social commerce prend du volume.")
        self.assertNotIn("#", desc)
        self.assertTrue(desc.startswith("TikTok Shop"))

    def test_empty_everything_returns_fallback(self):
        self.assertEqual(fetch_news.build_description("", ""), fetch_news.FALLBACK_DESCRIPTION)

    def test_output_never_has_hash_or_double_spaces(self):
        for summary, body in [
            ("Résumé > avec *markdown* …", "Corps **gras** et `code` utile pour un setup."),
            ("", "# Titre\n\nParagraphe suffisamment long pour servir de description propre."),
        ]:
            desc = fetch_news.build_description(summary, body)
            self.assertNotIn("#", desc)
            self.assertNotIn("  ", desc)
            self.assertFalse(desc.startswith((">", "*", "`")))


if __name__ == "__main__":
    unittest.main()
