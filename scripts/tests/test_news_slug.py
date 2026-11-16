import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from seo_text import SLUG_MAX, is_article_url, slugify, title_key


class SlugTests(unittest.TestCase):
    def test_long_title_is_cut_on_a_word_boundary(self):
        slug = slugify(
            "Black Friday 2026 – La souris Logitech MX Master 4 Graphite à 99,99 € (-10%)"
        )
        self.assertLessEqual(len(slug), SLUG_MAX)
        self.assertFalse(slug.endswith("-"), slug)
        self.assertEqual(slug, "black-friday-2026-la-souris-logitech-mx-master-4-graphite")

    def test_no_dangling_fragment_after_truncation(self):
        # Reproduit le slug fautif `...-graphite-a-` : le fragment d'une lettre doit sauter.
        slug = slugify("Black Friday la souris Logitech MX Master 4 Graphite absolument geniale")
        self.assertLessEqual(len(slug), SLUG_MAX)
        self.assertGreater(len(slug.split("-")[-1]), 1, f"fragment orphelin dans {slug}")

    def test_short_title_is_kept_whole(self):
        self.assertEqual(slugify("Razer Quartz 2026"), "razer-quartz-2026")

    def test_accents_are_transliterated(self):
        self.assertEqual(slugify("Éclairage d'intérieur"), "eclairage-d-interieur")

    def test_empty_input_does_not_raise(self):
        self.assertEqual(slugify(""), "")
        self.assertEqual(slugify("€€€ !!!"), "")

    def test_title_key_ignores_case_accents_and_punctuation(self):
        self.assertEqual(
            title_key("Black Friday 2026 – La souris Logitech à 99,99 €"),
            title_key("black friday 2026 la souris logitech a 99 99"),
        )

    def test_article_url_ignores_bare_domains(self):
        self.assertTrue(is_article_url("https://www.elgato.com/fr/p/stream-deck-neo"))
        self.assertFalse(is_article_url("https://www.elgato.com/"))
        self.assertFalse(is_article_url(""))


if __name__ == "__main__":
    unittest.main()
