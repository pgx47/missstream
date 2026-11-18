import json
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

import generate_article  # noqa: E402


class KeywordSimilarityTests(unittest.TestCase):
    def test_two_winter_setup_topics_collide(self):
        self.assertTrue(
            generate_article.is_too_similar(
                "setup bureau ultra cozy pour les streams d hiver",
                "setup streaming cosy pour l hiver",
            )
        )

    def test_gift_topics_collide(self):
        self.assertTrue(
            generate_article.is_too_similar(
                "meilleur cadeau pour une streamer débutante",
                "idées cadeaux streameuse noël",
            )
        )

    def test_distinct_lighting_products_do_not_collide(self):
        self.assertFalse(
            generate_article.is_too_similar(
                "panneau LED blanc pour éclairage doux de stream",
                "softbox blanc pour éclairage de visage en stream",
            )
        )

    def test_unrelated_products_do_not_collide(self):
        self.assertFalse(
            generate_article.is_too_similar(
                "tapis de souris XXL pastel et bras de micro blanc",
                "support casque blanc pour bureau de créatrice stream",
            )
        )

    def test_near_identical_keywords_are_duplicates(self):
        self.assertTrue(
            generate_article.is_duplicate_topic(
                "setup cozy hiver", "setup cozy hiver 2026"
            )
        )
        self.assertFalse(
            generate_article.is_duplicate_topic(
                "panneau LED blanc pour éclairage doux de stream",
                "softbox blanc pour éclairage de visage en stream",
            )
        )

    def test_accents_and_plurals_are_normalised(self):
        self.assertEqual(
            generate_article.keyword_signature("Micros USB blancs et roses"),
            generate_article.keyword_signature("micro usb blanc rose"),
        )


class DescriptionTrimmingTests(unittest.TestCase):
    def test_long_description_is_cut_on_a_word_boundary(self):
        text = "Trois bureaux assis-debout blancs testés pour setup créateur : stabilité, bruit en live, gestion des câbles et intégration dans une pièce de vie avec un vrai bureau."
        out = generate_article.seo_description(text)
        self.assertLessEqual(len(out), 158)
        self.assertTrue(out.endswith("."))
        self.assertFalse(out.endswith(" ."))

    def test_short_description_is_untouched(self):
        text = "Trois mics testés."
        self.assertEqual(generate_article.seo_description(text), text)


class TopicsFileTests(unittest.TestCase):
    def setUp(self):
        self.topics = json.loads((SCRIPTS / "topics.json").read_text(encoding="utf-8"))

    def test_file_is_valid_and_keeps_known_statuses(self):
        statuses = {t.get("status") for t in self.topics}
        self.assertIn("pending", statuses)
        self.assertIn("done", statuses)

    def test_known_duplicate_topics_are_retired(self):
        by_keyword = {t.get("keyword"): t for t in self.topics}
        for keyword in (
            "setup streaming cosy pour l hiver",
            "les 5 meilleurs casques audio oreilles de chat",
            "Elgato Stream Deck Neo vs MK.2",
        ):
            self.assertEqual(by_keyword[keyword]["status"], "duplicate")

    def test_every_entry_still_has_a_keyword(self):
        self.assertTrue(all(t.get("keyword") for t in self.topics))


if __name__ == "__main__":
    unittest.main()
