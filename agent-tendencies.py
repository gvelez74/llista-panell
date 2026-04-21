#!/usr/bin/env python3
"""
Agent de tendències — Llista.cat
Cada dia a les 7:00h llegeix RSS de fonts clau del sector, envia els articles
a Claude per anàlisi i desa les 5 principals tendències per categoria a Supabase.
No requereix Perplexity ni cap API de pagament addicional.
"""

import os
import sys
import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path

import httpx
import anthropic
from supabase import create_client

# ── Configuració ──────────────────────────────────────────────────────────────

BASE_DIR      = Path(__file__).parent
LOG_FILE      = BASE_DIR / "agent-tendencies.log"

SUPABASE_URL  = "https://dqwteqgdwmivepkdtehy.supabase.co"
SUPABASE_KEY  = os.environ.get("SUPABASE_KEY", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

MODEL         = "claude-sonnet-4-6"   # Sonnet per millor capacitat analítica
MAX_ARTICLES  = 30                    # Màxim articles per categoria per enviar a Claude
HOURS_BACK    = 72                    # Finestra temporal (hores)

# ── Fonts per categoria ───────────────────────────────────────────────────────

CATEGORIES = [
    {
        "id": "algoritmes",
        "nom": "Algoritmes",
        "focus": "algorithm changes on YouTube, TikTok, Instagram, X affecting creator reach and engagement",
        "feeds": [
            "https://blog.youtube/rss/",
            "https://www.socialmediatoday.com/rss.xml",
            "https://techcrunch.com/feed/",
            "https://www.theverge.com/rss/index.xml",
        ],
    },
    {
        "id": "metriques",
        "nom": "Mètriques i Analytics",
        "focus": "new metrics, analytics tools, measurement standards and KPIs for social media and content creators",
        "feeds": [
            "https://www.socialmediatoday.com/rss.xml",
            "https://sproutsocial.com/insights/feed/",
            "https://blog.hootsuite.com/feed/",
            "https://techcrunch.com/feed/",
        ],
    },
    {
        "id": "plataformes",
        "nom": "Tendències de Plataformes",
        "focus": "new features, monetization changes, policy updates on YouTube, TikTok, Instagram, LinkedIn, Twitch",
        "feeds": [
            "https://blog.youtube/rss/",
            "https://www.theverge.com/rss/index.xml",
            "https://techcrunch.com/feed/",
            "https://www.socialmediatoday.com/rss.xml",
            "https://mashable.com/feeds/rss/all",
        ],
    },
    {
        "id": "economia",
        "nom": "Economia de Creadors",
        "focus": "creator economy trends, brand deals, monetization, creator funds, sponsorships, business models for content creators",
        "feeds": [
            "https://www.theinformation.com/feed",
            "https://techcrunch.com/feed/",
            "https://www.businessinsider.com/rss",
            "https://www.socialmediatoday.com/rss.xml",
        ],
    },
    {
        "id": "ia-contingut",
        "nom": "IA i Contingut",
        "focus": "AI tools for content creation, generative AI impact on creators, AI regulation for social media platforms",
        "feeds": [
            "https://techcrunch.com/feed/",
            "https://www.theverge.com/rss/index.xml",
            "https://www.wired.com/feed/rss",
            "https://venturebeat.com/feed/",
        ],
    },
    {
        "id": "mercat-hispanic",
        "nom": "Mercat Hispanòfon",
        "focus": "content creator trends in Spain, Latin America and Catalan-speaking markets, Hispanic digital media news",
        "feeds": [
            "https://marketing4ecommerce.net/feed/",
            "https://www.puromarketing.com/rss/rss.xml",
            "https://www.xataka.com/feedburner.xml",
            "https://www.elconfidencial.com/rss/tecnologia.xml",
        ],
    },
]

SYSTEM_PROMPT = """Ets un expert analista sènior de la indústria de la creació de contingut digital.
La teva especialitat és identificar tendències rellevants per als creadors de contingut,
amb foco especial en l'ecosistema de creadors en català i el mercat hispanòfon.

Per cada tendència identificada, valores si representa:
- "oportunitat": benefici potencial per als creadors de contingut en català
- "risc": amenaça o repte per als creadors de contingut en català
- "neutre": informació rellevant però sense impacte directe clar

Respon SEMPRE en català. Retorna SEMPRE JSON vàlid sense cap text addicional."""

ANALYSIS_PROMPT = """Analitza els articles següents sobre: {focus}

ARTICLES RECENTS:
{articles}

A partir d'aquests articles (i el teu coneixement del sector), identifica les 5 tendències
o novetats més importants per als creadors de contingut en català.

Per cada tendència retorna un objecte JSON amb exactament aquests camps:
- "titol": títol descriptiu i concís (màx 12 paraules, en català)
- "resum": anàlisi de 3-4 frases en català: QUÈ ha passat, PER QUÈ és rellevant i QUIN IMPACTE té per als creadors en català
- "font": nom de la publicació font (de la llista d'articles o "Coneixement propi" si és d'elaboració pròpia)
- "url": URL de l'article font (si disponible, sinó "")
- "valoracio": "oportunitat", "risc" o "neutre"

Retorna EXCLUSIVAMENT un array JSON de 5 objectes, sense text addicional ni markdown.
Si no hi ha prou articles recents, complementa amb el teu coneixement actualitzat del sector."""

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ── RSS fetching ──────────────────────────────────────────────────────────────

def parse_date(date_str: str) -> datetime | None:
    """Intenta parsejar dates RSS en múltiples formats."""
    if not date_str:
        return None
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S GMT",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def fetch_rss(url: str, timeout: int = 15) -> list[dict]:
    """Descàrrega i parseja un feed RSS. Retorna llista d'articles."""
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            res = client.get(url, headers={"User-Agent": "LlistaCAT-TrendBot/1.0"})
            res.raise_for_status()
        root = ET.fromstring(res.text)
    except Exception as e:
        log.warning("  RSS no disponible (%s): %s", url, e)
        return []

    # Suport per RSS 2.0 i Atom
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items = []

    # RSS 2.0
    for item in root.findall(".//item"):
        title   = (item.findtext("title") or "").strip()
        link    = (item.findtext("link") or "").strip()
        desc    = (item.findtext("description") or "").strip()[:300]
        pubdate = item.findtext("pubDate") or item.findtext("dc:date", namespaces={"dc": "http://purl.org/dc/elements/1.1/"})
        if title:
            items.append({"title": title, "url": link, "summary": desc, "date_str": pubdate or ""})

    # Atom
    if not items:
        for entry in root.findall("atom:entry", ns):
            title   = (entry.findtext("atom:title", namespaces=ns) or "").strip()
            link_el = entry.find("atom:link", ns)
            link    = link_el.get("href", "") if link_el is not None else ""
            summary = (entry.findtext("atom:summary", namespaces=ns) or "").strip()[:300]
            pubdate = entry.findtext("atom:published", namespaces=ns) or entry.findtext("atom:updated", namespaces=ns)
            if title:
                items.append({"title": title, "url": link, "summary": summary, "date_str": pubdate or ""})

    return items


def collect_articles(cat: dict) -> list[dict]:
    """Recull articles recents de tots els feeds d'una categoria."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS_BACK)
    all_articles = []

    for feed_url in cat["feeds"]:
        articles = fetch_rss(feed_url)
        for a in articles:
            dt = parse_date(a["date_str"])
            if dt is None or dt >= cutoff:
                all_articles.append(a)

    # Elimina duplicats per URL
    seen = set()
    unique = []
    for a in all_articles:
        key = a["url"] or a["title"]
        if key not in seen:
            seen.add(key)
            unique.append(a)

    log.info("  %d articles recollits de %d feeds", len(unique), len(cat["feeds"]))
    return unique[:MAX_ARTICLES]


def format_articles(articles: list[dict]) -> str:
    """Formata els articles per al prompt de Claude."""
    if not articles:
        return "(No s'han trobat articles recents als feeds. Usa el teu coneixement actualitzat del sector.)"
    lines = []
    for i, a in enumerate(articles, 1):
        lines.append(f"{i}. [{a['title']}]({a['url']})")
        if a.get("summary"):
            lines.append(f"   {a['summary']}")
    return "\n".join(lines)

# ── Claude analysis ───────────────────────────────────────────────────────────

def analyze_with_claude(client: anthropic.Anthropic, cat: dict, articles: list[dict]) -> list[dict]:
    """Envia els articles a Claude i obté les 5 tendències estructurades."""
    articles_text = format_articles(articles)
    prompt = ANALYSIS_PROMPT.format(focus=cat["focus"], articles=articles_text)

    message = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    items = json.loads(raw)
    if not isinstance(items, list):
        raise ValueError(f"Resposta inesperada (no és array): {raw[:200]}")
    return items[:5]

# ── Supabase ──────────────────────────────────────────────────────────────────

def save_to_supabase(sb, cat: dict, items: list[dict], cerca_date: str) -> int:
    records = []
    for item in items:
        valoracio = (item.get("valoracio") or "neutre").lower()
        if valoracio not in ("oportunitat", "risc", "neutre"):
            valoracio = "neutre"
        records.append({
            "categoria_id":  cat["id"],
            "categoria_nom": cat["nom"],
            "titol":         (item.get("titol") or "")[:200],
            "resum":         item.get("resum") or "",
            "font":          (item.get("font") or "")[:200],
            "url":           (item.get("url") or "")[:500],
            "valoracio":     valoracio,
            "data_cerca":    cerca_date,
            "estat":         "pendent",
        })
    result = sb.table("llista_tendencies").insert(records).execute()
    return len(result.data) if result.data else 0

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not ANTHROPIC_KEY:
        log.error("Falta ANTHROPIC_API_KEY. Exporta-la al teu entorn.")
        sys.exit(1)
    if not SUPABASE_KEY:
        log.error("Falta SUPABASE_KEY. Exporta-la al teu entorn.")
        sys.exit(1)

    sb     = create_client(SUPABASE_URL, SUPABASE_KEY)
    claude = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    cerca_date = datetime.now().date().isoformat()

    log.info("Iniciant recerca de tendències — %s", cerca_date)

    total_ok = 0
    total_errors = 0

    for cat in CATEGORIES:
        log.info("→ Categoria: %s", cat["nom"])
        try:
            articles = collect_articles(cat)
            items    = analyze_with_claude(claude, cat, articles)
            saved    = save_to_supabase(sb, cat, items, cerca_date)
            log.info("  ✓ %d tendències desades", saved)
            total_ok += saved
        except Exception as e:
            log.error("  ✗ Error a '%s': %s", cat["nom"], e)
            total_errors += 1

    log.info("Fet. %d tendències desades, %d categories amb error.", total_ok, total_errors)


if __name__ == "__main__":
    main()
