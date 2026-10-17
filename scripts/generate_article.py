#!/usr/bin/env python3
"""Génère un guide d'achat MDX pour missstream.xyz via DeepSeek.

- Lit le prochain topic `pending` dans scripts/topics.json
- Appel LLM structuré (tool call) : title, description, slug, body, faq, products, imagePrompt
- Auto-refill : si <=2 topics pending, le LLM en injecte 15 nouveaux
- Image : Pollinations -> Unsplash -> pool local public/images/fallbacks/
- Écrit src/content/guides/{slug}.mdx et met topics.json à jour
"""

import json
import os
import random
import re
import sys
import urllib.parse
from pathlib import Path

import requests
import yaml
from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
TOPICS_FILE = Path(__file__).parent / "topics.json"
GUIDES_DIR = ROOT / "src/content/guides"
IMG_DIR = ROOT / "public/images/guides"
FALLBACK_DIR = ROOT / "public/images/fallbacks"

# Chaîne de fallback LLM : DeepSeek -> OpenRouter -> Anthropic (endpoint compatible OpenAI)
if os.environ.get("DEEPSEEK_API_KEY"):
    _base, _key, _model = "https://api.deepseek.com", os.environ["DEEPSEEK_API_KEY"], "deepseek-flash"
elif os.environ.get("OPENROUTER_API_KEY"):
    _base, _key, _model = "https://openrouter.ai/api/v1", os.environ["OPENROUTER_API_KEY"], "deepseek/deepseek-v4.1-flash"
elif os.environ.get("ANTHROPIC_API_KEY"):
    _base, _key, _model = "https://api.anthropic.com/v1/", os.environ["ANTHROPIC_API_KEY"], "claude-sonnet-4-5"
else:
    _base = _key = _model = None

client = OpenAI(
    base_url=os.environ.get("LLM_BASE_URL") or _base,
    api_key=_key,
)
MODEL = os.environ.get("LLM_MODEL") or _model or "deepseek-flash"

SITE_CONTEXT = """Tu es la rédactrice en chef de "Miss Stream" (missstream.xyz), blog dédié aux setups
de streaming esthétiques, cozy et pastel pour créatrices de contenu (Twitch, YouTube, TikTok).
Cible : débutantes et passionnées qui veulent un setup beau ET performant, budget 100-300 EUR/produit.
Angle : retour d'expérience, utilité réelle, intégration dans une pièce de vie, coloris dispo."""

EDITORIAL_RULES = """Style : ton informatif, direct, bienveillant, orienté retour d'expérience.
INTERDIT : "Plongeons dans l'univers", "Il est important de noter", "En conclusion", "Dans le monde
de", jargon tech-bro, emojis dans le texte, prix en euros figés, promesses mensongères, rendus clipart.

Conversion (sans jamais mentir) :
- TITRE : structure magnétique et factuelle ("Pourquoi tout le monde s'arrache X", "L'erreur que
  font 90% des streameuses avec Y", "Le secret des setups qui rendent bien en caméra"). Curiosité
  forte, zéro clickbait mensonger.
- INTRO : technique PAS (Problem-Agitation-Solution) — nomme une frustration réelle du lecteur,
  agite-la en une phrase, puis annonce que le guide la résout.
- Tout en haut du body : tableau Markdown "Le choix de la rédaction" de 3 lignes (Meilleur global /
  Meilleur budget / Coup de cœur design) : produit + conclusion en 5 mots max.
- Toujours : paragraphes courts, concret, comparatifs honnêtes (chaque produit a des défauts)."""


def load_topics() -> list[dict]:
    return json.loads(TOPICS_FILE.read_text(encoding="utf-8"))


def save_topics(topics: list[dict]) -> None:
    TOPICS_FILE.write_text(
        json.dumps(topics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def published_guides() -> list[tuple[str, str]]:
    """(slug, title) des guides déjà publiés, pour le maillage interne."""
    out = []
    for f in sorted(GUIDES_DIR.glob("*.mdx")):
        m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', f.read_text(encoding="utf-8"), re.M)
        out.append((f.stem, m.group(1) if m else f.stem))
    return out


def refill_topics(topics: list[dict]) -> list[dict]:
    print("Backlog faible : génération de 15 nouveaux topics longue traîne...")
    existing = [t["keyword"] for t in topics]
    prompt = f"""{SITE_CONTEXT}

Voici les mots-clés déjà couverts : {json.dumps(existing, ensure_ascii=False)}

Propose 15 nouveaux mots-clés d'intention d'achat longue traîne (ex: "meilleur bras de micro blanc
pour setup pastel"), jamais identiques aux existants, orientés achat de matériel de streaming
esthétique. Pour chacun, donne 2-4 noms de produits Amazon réels et vendus en France
(ex: "Fifine AM8 blanc", "Razer Kraken Kitty V2 Quartz").

Réponds en JSON : {{"topics": [{{"keyword": str, "categorie": str, "produits": [str]}}]}}"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.6,
    )
    data = json.loads(resp.choices[0].message.content)
    new_topics = [
        {
            "keyword": t["keyword"],
            "categorie": t.get("categorie", "setup"),
            "produits": t.get("produits", []),
            "status": "pending",
        }
        for t in data.get("topics", [])
        if t.get("keyword") and t["keyword"] not in existing
    ]
    topics.extend(new_topics)
    print(f"+{len(new_topics)} topics ajoutés")
    return topics


ARTICLE_TOOL = {
    "type": "function",
    "function": {
        "name": "publish_guide",
        "description": "Publie un guide d'achat complet",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Titre H1, 60-70 car., avec le mot-clé"},
                "description": {"type": "string", "description": "Meta description < 160 car."},
                "slug": {"type": "string", "description": "slug URL, kebab-case, sans accents"},
                "body": {
                    "type": "string",
                    "description": "Corps Markdown : ## sections, 1200-1800 mots, 2 liens internes obligatoires",
                },
                "faq": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "answer": {"type": "string"},
                        },
                        "required": ["question", "answer"],
                    },
                    "description": "3-5 questions réelles de créatrices",
                },
                "products": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "nom": {"type": "string"},
                            "asin": {"type": "string", "description": "ASIN Amazon 10 car. si certain, sinon omets"},
                            "couleur": {"type": "string"},
                            "badge": {"type": "string"},
                            "pointsForts": {"type": "array", "items": {"type": "string"}},
                            "pointsFaibles": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["nom", "pointsForts", "pointsFaibles"],
                    },
                    "description": "3-5 produits réels vendus sur amazon.fr",
                },
                "imagePrompt": {
                    "type": "string",
                    "description": "Prompt anglais pour photo réaliste du setup décrit",
                },
            },
            "required": ["title", "description", "slug", "body", "faq", "products", "imagePrompt"],
        },
    },
}


def generate_article(topic: dict, internal_links: list[tuple[str, str]]) -> dict:
    links_md = "\n".join(f"- [{t}](/articles/{s}/)" for s, t in internal_links) or "(aucun encore)"
    prompt = f"""{SITE_CONTEXT}

{EDITORIAL_RULES}

Rédige un guide complet pour le mot-clé : "{topic['keyword']}"
Catégorie : {topic.get('categorie', 'setup')}
Produits suggérés (adapte si pertinent) : {json.dumps(topic.get('produits', []), ensure_ascii=False)}

Maillage interne OBLIGATOIRE : intègre naturellement au moins 2 de ces liens Markdown dans le corps :
{links_md}

Appelle la fonction publish_guide avec le guide complet."""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        tools=[ARTICLE_TOOL],
        temperature=0.5,
    )
    msg = resp.choices[0].message
    if msg.tool_calls:
        return json.loads(msg.tool_calls[0].function.arguments)
    content = re.sub(r"^```(json|markdown|mdx)?\n|```$", "", msg.content.strip())
    return json.loads(content)


def upload_r2(data: bytes, slug: str) -> str | None:
    """Upload vers R2 si configuré (R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY,
    CLOUDFLARE_ACCOUNT_ID, R2_BUCKET, R2_PUBLIC_URL). Sinon None."""
    ak, sk, acct, bucket, pub = (
        os.environ.get(k)
        for k in ("R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "CLOUDFLARE_ACCOUNT_ID",
                  "R2_BUCKET", "R2_PUBLIC_URL")
    )
    if not all((ak, sk, acct, bucket, pub)):
        return None
    try:
        import boto3
        from io import BytesIO

        boto3.client(
            "s3",
            endpoint_url=f"https://{acct}.r2.cloudflarestorage.com",
            aws_access_key_id=ak,
            aws_secret_access_key=sk,
            region_name="auto",
        ).upload_fileobj(
            BytesIO(data), bucket, f"{slug}.webp",
            ExtraArgs={"ContentType": "image/webp"},
        )
        print(f"Image uploadée sur R2 ({bucket})")
        return f"{pub.rstrip('/')}/{slug}.webp"
    except Exception as e:
        print(f"Upload R2 impossible, fallback local : {e}")
        return None


def save_image(raw: bytes, slug: str) -> str:
    """Convertit en WebP, upload R2 si configuré, sinon public/images/guides/."""
    try:
        from PIL import Image
        import io

        img = Image.open(io.BytesIO(raw)).convert("RGB")
        img.thumbnail((1600, 1600))
        buf = io.BytesIO()
        img.save(buf, "WEBP", quality=82)
        raw = buf.getvalue()
    except Exception as e:
        print(f"Pillow indisponible ({e}), image brute conservée")

    if r2_url := upload_r2(raw, slug):
        return r2_url

    IMG_DIR.mkdir(parents=True, exist_ok=True)
    out = IMG_DIR / f"{slug}.webp"
    out.write_bytes(raw)
    return f"/images/guides/{slug}.webp"


def get_image(image_prompt: str, slug: str) -> str:
    """Pollinations -> Unsplash -> pool local. Jamais d'échec."""
    full_prompt = (
        f"{image_prompt}. A bright, airy, modern desk setup for a female streamer. "
        "Predominantly white, light cream and soft pastel pink palette. Soft natural "
        "daylight from a window, no harsh shadows. Clean white desk, cozy details like a "
        "potted succulent or pastel mug, soft lavender ambient backlight. Professional "
        "editorial photography, 35mm lens, high resolution, photorealistic, Pinterest "
        "'cozy desk setup' aesthetic. NO dark rooms, NO red/blue/green neon gamer lights, "
        "NO black leather furniture, no 3D render, no cartoon, no clipart, no text."
    )

    # Niveau 1 : Unsplash (vraies photos), requêtes biaisées pastel/clair
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if key:
        try:
            words = re.sub(r"[^a-zA-Z ]", "", image_prompt).split()[:4]
            topical = " ".join(words)
            q = urllib.parse.quote(random.choice(
                [f"{topical} pastel", f"{topical} white desk", f"{topical} aesthetic"]
            ))
            results = r.json().get("results", [])
            if results:
                img = requests.get(random.choice(results)["urls"]["regular"], timeout=30).content
                print("Image Unsplash")
                return save_image(img, slug)
        except Exception as e:
            print(f"Échec Unsplash : {e}")

    # Niveau 2 : Pollinations/FLUX (FLUX, gratuit)
    try:
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(full_prompt)}?width=1200&height=630&nologo=true"
        r = requests.get(url, timeout=90)
        if r.status_code == 200 and len(r.content) > 10000:
            print("Image Pollinations")
            return save_image(r.content, slug)
    except Exception as e:
        print(f"Échec Pollinations : {e}")

    # Niveau 3 : pool local WebP
    pool = sorted(FALLBACK_DIR.glob("*.webp"))
    if pool:
        print("Image fallback locale")
        return f"/images/fallbacks/{random.choice(pool).name}"

    return "/images/fallbacks/news-fallback-1.webp"


def write_mdx(article: dict, image: str) -> Path:
    GUIDES_DIR.mkdir(parents=True, exist_ok=True)
    for p in article.get("products", []):
        if p.get("asin") and not re.fullmatch(r"[A-Za-z0-9]{10}", p["asin"]):
            p.pop("asin")

    frontmatter = {
        "title": article["title"],
        "description": article["description"],
        "publishDate": __import__("datetime").date.today().isoformat(),
        "image": image,
        "category": "guides",
        "faq": article.get("faq", []),
        "products": article.get("products", []),
    }
    body = article["body"].replace("```markdown", "").replace("```", "").strip()
    mdx = "---\n" + yaml.dump(frontmatter, allow_unicode=True, sort_keys=False) + "---\n\n" + body + "\n"
    path = GUIDES_DIR / f"{article['slug']}.mdx"
    path.write_text(mdx, encoding="utf-8")
    return path


def main() -> int:
    topics = load_topics()
    pending = [t for t in topics if t.get("status") == "pending"]
    if len(pending) <= 2:
        topics = refill_topics(topics)
        pending = [t for t in topics if t.get("status") == "pending"]
    if not pending:
        print("Aucun topic pending malgré le refill.")
        return 0

    topic = pending[0]
    slug_guess = re.sub(r"[^a-z0-9]+", "-", topic["keyword"].lower()).strip("-")
    if (GUIDES_DIR / f"{slug_guess}.mdx").exists():
        topic["status"] = "done"
        save_topics(topics)
        print("Déjà publié, skip.")
        return 0

    print(f"Génération du guide : {topic['keyword']}")
    internal = published_guides()
    article = generate_article(topic, internal)
    image = get_image(article["imagePrompt"], article["slug"])
    path = write_mdx(article, image)

    topic["status"] = "done"
    topic["slug"] = article["slug"]
    save_topics(topics)
    print(f"Guide publié : {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
