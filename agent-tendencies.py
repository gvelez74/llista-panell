#!/usr/bin/env python3
"""
Agent de tendències — Llista.cat
Cada dia a les 7:00h investiga les 5 principals novetats per categoria
usant Perplexity (cerca web en temps real) i les desa a Supabase.
"""

import os
import sys
import json
import logging
from datetime import date
from pathlib import Path

import httpx
from supabase import create_client

# ── Configuració ──────────────────────────────────────────────────────────────

BASE_DIR       = Path(__file__).parent
LOG_FILE       = BASE_DIR / "agent-tendencies.log"

SUPABASE_URL   = "https://dqwteqgdwmivepkdtehy.supabase.co"
SUPABASE_KEY   = os.environ.get("SUPABASE_KEY", "")
PERPLEXITY_KEY = os.environ.get("PERPLEXITY_API_KEY", "")

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_MODEL = "sonar"

CATEGORIES = [
    {
        "id": "algoritmes",
        "nom": "Algoritmes",
        "context": "algorithm changes on YouTube, TikTok, Instagram, X/Twitter affecting content creator reach, visibility and engagement in 2025",
    },
    {
        "id": "metriques",
        "nom": "Mètriques i Analytics",
        "context": "new metrics, analytics tools, measurement standards and KPIs for content creators and social media platforms in 2025",
    },
    {
        "id": "plataformes",
        "nom": "Tendències de Plataformes",
        "context": "platform feature launches, monetization changes, policy updates on YouTube, TikTok, Instagram, LinkedIn, Twitch in 2025",
    },
    {
        "id": "economia",
        "nom": "Economia de Creadors",
        "context": "creator economy trends, brand deals, creator funds, sponsorship rates, monetization models, creator business news in 2025",
    },
    {
        "id": "ia-contingut",
        "nom": "IA i Contingut",
        "context": "AI tools for content creation, generative AI impact on creators, AI regulation for social media, synthetic media trends in 2025",
    },
    {
        "id": "mercat-hispanic",
        "nom": "Mercat Hispanòfon",
        "context": "content creator trends in Spain, Latin America and Catalan-speaking markets, Hispanic digital media and creator ecosystem news in 2025",
    },
]

SYSTEM_PROMPT = """Ets un expert analista de la indústria de la creació de contingut digital.
La teva missió és identificar les novetats i tendències més rellevants per als creadors de contingut,
amb especial atenció a les implicacions per a l'ecosistema de creadors en català i el mercat hispanòfon.

Quan analitzis cada tendència, valora si representa:
- "oportunitat": benefici potencial per als creadors en català
- "risc": amenaça o repte per als creadors en català
- "neutre": informació rellevant sense impacte directe clar

Respon SEMPRE en català i retorna SEMPRE un JSON vàlid sense cap text addicional."""

RESEARCH_PROMPT = """Investiga les 5 novetats o tendències més importants i recents sobre: {context}

Geogràficament cobreix: Catalunya/Espanya, Europa i USA/global.

Per cada troballa retorna un objecte JSON amb exactament aquests camps:
- "titol": títol descriptiu i concís (màx 12 paraules)
- "resum": anàlisi de 3-4 frases que expliqui QUÈ ha passat, PER QUÈ és rellevant i QUIN IMPACTE té per als creadors en català
- "font": nom de la publicació o plataforma font
- "url": URL de la font (si disponible, sinó "")
- "valoracio": "oportunitat", "risc" o "neutre"

Retorna EXCLUSIVAMENT un array JSON de 5 objectes, sense text addicional ni markdown."""

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

# ── Helpers ───────────────────────────────────────────────────────────────────

def research_category(cat: dict) -> list[dict]:
    """Crida Perplexity per obtenir les 5 tendències d'una categoria."""
    prompt = RESEARCH_PROMPT.format(context=cat["context"])

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": PERPLEXITY_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        "max_tokens": 2048,
        "temperature": 0.2,
    }

    with httpx.Client(timeout=60) as client:
        res = client.post(PERPLEXITY_URL, headers=headers, json=body)
        res.raise_for_status()

    raw = res.json()["choices"][0]["message"]["content"].strip()

    # Elimina possibles code fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    items = json.loads(raw)
    if not isinstance(items, list):
        raise ValueError(f"Resposta inesperada (no és array): {raw[:200]}")

    return items[:5]


def save_to_supabase(sb, categoria_id: str, categoria_nom: str, items: list[dict], cerca_date: str) -> int:
    """Insereix els ítems a llista_tendencies. Retorna el nombre inserit."""
    records = []
    for item in items:
        valoracio = item.get("valoracio", "neutre").lower()
        if valoracio not in ("oportunitat", "risc", "neutre"):
            valoracio = "neutre"
        records.append({
            "categoria_id":  categoria_id,
            "categoria_nom": categoria_nom,
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
    if not PERPLEXITY_KEY:
        log.error("Falta PERPLEXITY_API_KEY. Exporta-la al teu entorn.")
        sys.exit(1)
    if not SUPABASE_KEY:
        log.error("Falta SUPABASE_KEY. Exporta-la al teu entorn.")
        sys.exit(1)

    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    cerca_date = date.today().isoformat()

    log.info("Iniciant recerca de tendències — %s", cerca_date)

    total_ok = 0
    total_errors = 0

    for cat in CATEGORIES:
        log.info("→ Categoria: %s", cat["nom"])
        try:
            items = research_category(cat)
            saved = save_to_supabase(sb, cat["id"], cat["nom"], items, cerca_date)
            log.info("  ✓ %d tendències desades", saved)
            total_ok += saved
        except Exception as e:
            log.error("  ✗ Error a '%s': %s", cat["nom"], e)
            total_errors += 1

    log.info("Fet. %d tendències desades, %d categories amb error.", total_ok, total_errors)


if __name__ == "__main__":
    main()
