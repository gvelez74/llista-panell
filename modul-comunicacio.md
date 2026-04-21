# Mòdul Comunicació

Generació de contingut editorial per a Llista.cat via Claude API. Integra l'estilometria del projecte.

## Formats disponibles (`COMM_TIPUS`)

| Clau | Etiqueta | Notes |
|------|----------|-------|
| `blog` | Article Blog | SEO optimitzat, amb opcions de longitud |
| `instagram` | Instagram | Caption + hashtags |

## Tons disponibles (`COMM_TOS`)

| Clau | Descripció |
|------|------------|
| `proper` | Informal, càlid |
| `professional` | Formal, rigorós |
| `entusiasta` | Energètic, motivador |
| `informatiu` | Clar, neutre |
| `humoristic` | Lleuger, amb gràcia |

## Longituds (només blog, `COMM_LENGTHS`)

| Clau | Paraules |
|------|----------|
| `curt` | 600–900 |
| `mitjà` | 900–1.400 |
| `llarg` | 1.400–2.000 |
| `extens` | 2.000–3.000 |

## System prompts

- **`BLOG_SYSTEM_PROMPT`** — Expert SEO. Estructura Xataka + to Accent Obert. E-E-A-T, H1/H2/H3, FAQs, SEO semàntic.
- **`INSTAGRAM_SYSTEM_PROMPT`** — Expert contingut digital. 150-300 paraules, primera línia com a ganxo, 5-8 hashtags, emojis funcionals (màx 4), CTA "Descobreix-los a llista.cat".

Tots dos prompts incorporen l'estilometria completa del projecte. Detall: [`.claude/skills/contingut-llista/estilometria.md`](.claude/skills/contingut-llista/estilometria.md)

## Model i API

- Model: `claude-haiku-4-5-20251001`
- Clau: `localStorage('llista_api_key')`

## Historial

Els continguts generats es guarden a `localStorage('llista_comm_hist')` (JSON). Accessibles des de la pestanya Historial.

## Instruccions del mòdul

El panell d'instruccions per tipus de contingut està **ocult per defecte** (`commInstruccionsVisible = false`). L'usuari el pot desplegar manualment.
