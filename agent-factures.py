#!/usr/bin/env python3
"""
Agent de factures — Llista.cat
Processa PDFs/imatges de `Factures/`, extreu dades amb Claude Vision,
insereix a Supabase (llista_finances) i mou els fitxers a `Factures entrades/`.
"""

import os
import sys
import base64
import json
import shutil
import logging
from datetime import datetime
from pathlib import Path

import anthropic
from supabase import create_client

# ── Configuració ──────────────────────────────────────────────────────────────

BASE_DIR      = Path(__file__).parent
INBOX_DIR     = BASE_DIR / "Factures"
DONE_DIR      = BASE_DIR / "Factures entrades"
LOG_FILE      = BASE_DIR / "agent-factures.log"

SUPABASE_URL  = "https://dqwteqgdwmivepkdtehy.supabase.co"
SUPABASE_KEY  = os.environ.get("SUPABASE_KEY", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SUPPORTED_EXT = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".gif"}
CATEGORIES    = ["COMUNICACIÓ","TECNOLOGIA","CONSULTORIA","PERSONAL",
                 "ESPAIS","SERVEIS","SUBVENCIONS","ALTRES"]

MONTH_ES = {"enero":0,"febrero":1,"marzo":2,"abril":3,"mayo":4,"junio":5,
            "julio":6,"agosto":7,"septiembre":8,"octubre":9,"noviembre":10,"diciembre":11}
MONTH_CA = {"gener":0,"febrer":1,"març":2,"abril":3,"maig":4,"juny":5,
            "juliol":6,"agost":7,"setembre":8,"octubre":9,"novembre":10,"desembre":11}

EXTRACT_PROMPT = f"""Analitza aquesta factura i retorna un JSON amb exactament aquests camps:

{{
  "concept":     "<Nom del proveïdor, ex: Google, Freelance Disseny>",
  "description": "<Concepte o descripció breu de la factura, ex: Subscripció anual, Consultoria SEO>",
  "amount":      <Import sense IVA, número decimal>,
  "month":       <Mes de la factura, 0=Gener, 11=Desembre>,
  "categoria":   "<Una de: {', '.join(CATEGORIES)}>"
}}

Regles:
- `amount` és SEMPRE sense IVA (base imposable). Si només veus el total amb IVA al 21%, divideix per 1.21.
- `month` és el mes de la data de la factura (0-indexat).
- `categoria` tria la que millor encaixi amb el servei/producte facturat.
- Retorna NOMÉS el JSON, sense text addicional.
"""

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

def load_file_as_base64(path: Path) -> tuple[str, str]:
    """Returns (base64_data, media_type)."""
    ext = path.suffix.lower()
    media_map = {
        ".pdf":  "application/pdf",
        ".png":  "image/png",
        ".jpg":  "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif":  "image/gif",
    }
    media_type = media_map.get(ext, "application/octet-stream")
    data = base64.standard_b64encode(path.read_bytes()).decode()
    return data, media_type


def extract_invoice_data(client: anthropic.Anthropic, file_path: Path) -> dict | None:
    """Uses Claude Vision to extract invoice fields from a file."""
    b64, media_type = load_file_as_base64(file_path)

    # PDFs need document source type; images use image source type
    if media_type == "application/pdf":
        content_block = {
            "type": "document",
            "source": {"type": "base64", "media_type": media_type, "data": b64},
        }
    else:
        content_block = {
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": b64},
        }

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": [content_block, {"type": "text", "text": EXTRACT_PROMPT}],
        }],
    )

    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        log.error("JSON invàlid rebut de Claude: %s", raw)
        return None

    # Validate required keys
    required = {"concept", "description", "amount", "month", "categoria"}
    if not required.issubset(data.keys()):
        log.error("Camps faltants a la resposta: %s", data)
        return None

    # Coerce types
    data["amount"] = float(data["amount"])
    data["month"]  = int(data["month"])
    if data["month"] < 0 or data["month"] > 11:
        data["month"] = datetime.now().month - 1
    if data["categoria"] not in CATEGORIES:
        data["categoria"] = "ALTRES"

    return data


def insert_to_supabase(sb, invoice: dict, filename: str) -> bool:
    """Inserts one invoice record into llista_finances."""
    record = {
        "project_id":  "llista-cat",
        "type":        "expense",
        "is_budget":   False,
        "categoria":   invoice["categoria"],
        "concept":     invoice["concept"],
        "description": invoice["description"],
        "amount":      invoice["amount"],
        "month":       invoice["month"],
    }
    result = sb.table("llista_finances").insert(record).execute()
    if result.data:
        log.info("✓ Inserida: %s → %s %.2f€ [%s]",
                 filename, invoice["concept"], invoice["amount"], invoice["categoria"])
        return True
    log.error("Error inserint %s: %s", filename, result)
    return False


def move_to_done(file_path: Path) -> Path:
    """Moves file to `Factures entrades/` adding today's date suffix."""
    today = datetime.now().strftime("%Y-%m-%d")
    new_name = f"{file_path.stem}_{today}{file_path.suffix}"
    dest = DONE_DIR / new_name
    # Avoid collisions
    counter = 1
    while dest.exists():
        new_name = f"{file_path.stem}_{today}_{counter}{file_path.suffix}"
        dest = DONE_DIR / new_name
        counter += 1
    shutil.move(str(file_path), str(dest))
    return dest

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not ANTHROPIC_KEY:
        log.error("Falta ANTHROPIC_API_KEY. Exporta-la al teu entorn.")
        sys.exit(1)
    if not SUPABASE_KEY:
        log.error("Falta SUPABASE_KEY. Exporta-la al teu entorn.")
        sys.exit(1)

    INBOX_DIR.mkdir(exist_ok=True)
    DONE_DIR.mkdir(exist_ok=True)

    files = [f for f in INBOX_DIR.iterdir()
             if f.is_file() and f.suffix.lower() in SUPPORTED_EXT]

    if not files:
        log.info("Cap fitxer nou a processar.")
        return

    log.info("Processant %d fitxer(s)...", len(files))

    claude = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    sb     = create_client(SUPABASE_URL, SUPABASE_KEY)

    ok = 0
    errors = 0
    for f in sorted(files):
        log.info("→ %s", f.name)
        try:
            invoice = extract_invoice_data(claude, f)
            if invoice is None:
                errors += 1
                continue
            if insert_to_supabase(sb, invoice, f.name):
                move_to_done(f)
                ok += 1
            else:
                errors += 1
        except Exception as exc:
            log.error("Error processant %s: %s", f.name, exc)
            errors += 1

    log.info("Fet. %d processades, %d errors.", ok, errors)


if __name__ == "__main__":
    main()
