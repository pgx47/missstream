import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DEEPSEEK_API_KEY", "test-key")

import generate_article as gen
import validate_content as vc


def make_root(tmp: Path, mdx: str, images=()) -> Path:
    guides = tmp / "src/content/guides"
    guides.mkdir(parents=True)
    (guides / "demo.mdx").write_text(mdx, encoding="utf-8")
    for asin in images:
        out = tmp / "public/images/products"
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{asin}.webp").write_bytes(b"img")
    return tmp


class GuideLinkTests(unittest.TestCase):
    def test_resolve_asin_matches_exact_then_prefix(self):
        known = {
            gen._norm_name("Fifine AM8 blanc"): "B0C74G9RLH",
            gen._norm_name("Logitech G733 LIGHTSPEED (blanc)"): "B07W6FQ658",
        }
        self.assertEqual(gen.resolve_asin("Fifine AM8", known), "B0C74G9RLH")
        self.assertEqual(gen.resolve_asin("Logitech G733 LIGHTSPEED", known), "B07W6FQ658")
        self.assertIsNone(gen.resolve_asin("Produit Inconnu", known))

    def test_body_boxes_get_the_frontmatter_asin(self):
        products = [{"nom": "Fifine AM8 blanc", "asin": "B0C74G9RLH"}]
        body = '<AffiliateBox nom="Fifine AM8" />'
        with patch.object(gen, "enrich_products"):
            result = gen.enrich_body_boxes(body, products)
        self.assertIn('asin="B0C74G9RLH"', result)

    def test_prune_drops_products_and_boxes_without_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            images = Path(tmp)
            (images / "B0C74G9RLH.webp").write_bytes(b"img")
            article = {
                "products": [
                    {"nom": "Fifine AM8", "asin": "B0C74G9RLH"},
                    {"nom": "Produit fantôme", "asin": "B000000000"},
                    {"nom": "Sans asin"},
                ],
                "body": (
                    '<AffiliateBox nom="Fifine AM8" asin="B0C74G9RLH" />\n\n'
                    '<AffiliateBox nom="Autre" />\n'
                ),
            }
            with patch.object(gen, "PRODUCTS_IMG_DIR", images):
                gen.prune_unlinked(article)
        self.assertEqual([p["nom"] for p in article["products"]], ["Fifine AM8"])
        self.assertIn("B0C74G9RLH", article["body"])
        self.assertNotIn('nom="Autre"', article["body"])


class GuideValidationTests(unittest.TestCase):
    def test_box_without_asin_blocks_publication(self):
        mdx = "---\ntitle: T\nproducts: []\n---\n\n<AffiliateBox nom=\"X\" />\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp), mdx)
            errors = vc.guide_errors(root)
        self.assertTrue(any("encart sans ASIN" in e for e in errors), errors)

    def test_dead_asin_without_image_blocks_publication(self):
        mdx = (
            "---\ntitle: T\nproducts:\n- nom: X\n  asin: B000000000\n---\n\n"
            '<AffiliateBox nom="X" asin="B000000000" />\n'
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp), mdx)
            errors = vc.guide_errors(root)
        self.assertTrue(any("image produit absente" in e for e in errors), errors)

    def test_linked_guide_passes(self):
        mdx = (
            "---\ntitle: T\nproducts:\n- nom: X\n  asin: B0C74G9RLH\n---\n\n"
            '<AffiliateBox nom="X" asin="B0C74G9RLH" />\n'
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp), mdx, images=["B0C74G9RLH"])
            self.assertEqual(vc.guide_errors(root), [])

    def test_legacy_six_dash_frontmatter_is_still_read(self):
        mdx = (
            "---\ntitle: T\nproducts:\n- nom: X\n  asin: B0C74G9RLH\n------\n\n"
            '<AffiliateBox nom="X" asin="B0C74G9RLH" />\n'
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp), mdx, images=["B0C74G9RLH"])
            self.assertEqual(vc.guide_errors(root), [])


if __name__ == "__main__":
    unittest.main()
