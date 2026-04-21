# Agent de factures — Llista.cat

Script diari que processa factures PDF/imatge, extreu camps amb Claude Vision i els insereix a Supabase.

## Arxius

| Fitxer | Funció |
|--------|--------|
| `agent-factures.py` | Script principal |
| `Factures/` | Safata d'entrada (deixa aquí les factures) |
| `Factures entrades/` | Arxiu (mogut automàticament amb data) |
| `agent-factures.log` | Log d'operacions (generat automàticament) |

## Configuració (primera vegada)

Necessites dues variables d'entorn. Afegeix-les al teu `~/.zshrc`:

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
export SUPABASE_KEY="eyJ..."   # service_role key de Supabase (no la publishable)
```

> La `SUPABASE_KEY` ha de ser la **service_role** key (Settings → API a Supabase), no la publishable.

Recàrrega: `source ~/.zshrc`

## Execució manual

```bash
cd "/Users/gvelez/Library/CloudStorage/OneDrive-FundaciópuntCAT/Gerard Velez/3. Projectes/1. llista/99. Agents llista"
python3 agent-factures.py
```

## Cron diari (8:00h)

El cron ja s'ha configurat via CronCreate. Executa cada dia a les 8:00.  
Pots veure'l amb `/cron-list` o amb `crontab -l` al terminal.

## Flux

1. Llegeix tots els fitxers de `Factures/` (PDF, PNG, JPG, WEBP, GIF)
2. Per cada fitxer, envia a Claude Vision (`claude-haiku-4-5-20251001`) amb el prompt d'extracció
3. Claude retorna JSON amb: `concept`, `description`, `amount`, `month`, `categoria`
4. Insereix a `llista_finances` amb `type='expense'`, `is_budget=false`
5. Mou el fitxer a `Factures entrades/` amb sufix `_YYYY-MM-DD`
6. Registra al log

## Camps extrets

| Camp Supabase | Significat | Exemple |
|---------------|------------|---------|
| `concept` | Nom del proveïdor | `"Google"`, `"Freelance disseny"` |
| `description` | Concepte/descripció | `"Subscripció anual"`, `"Consultoria SEO"` |
| `amount` | Import sense IVA (€) | `82.64` |
| `month` | Mes factura (0=Gener) | `3` (Abril) |
| `categoria` | Categoria | `"TECNOLOGIA"` |

## Categories disponibles

`COMUNICACIÓ` · `TECNOLOGIA` · `CONSULTORIA` · `PERSONAL` · `ESPAIS` · `SERVEIS` · `SUBVENCIONS` · `ALTRES`

## Errors comuns

- **"Falta ANTHROPIC_API_KEY"** → Exporta la variable d'entorn (veure Configuració)
- **"Falta SUPABASE_KEY"** → Exporta la service_role key
- **JSON invàlid de Claude** → La factura pot ser il·legible; revisa el fitxer manualment
- **Error inserint** → Comprova que la taula `llista_finances` existeix (usa el botó "⊞ SQL taula" del panell)
