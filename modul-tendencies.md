# Mòdul Tendències

Radar d'indústria que mostra les novetats i tendències del sector de la creació de contingut, amb valoració d'oportunitat o risc per a l'ecosistema en català.

## Font de dades

Taula Supabase `llista_tendencies`, poblada diàriament per `agent-tendencies.py` a les 7:00h.  
L'agent usa **Perplexity API** (model `sonar`) per fer cerques web en temps real.

## Categories

| ID | Nom |
|----|-----|
| `algoritmes` | Algoritmes |
| `metriques` | Mètriques i Analytics |
| `plataformes` | Tendències de Plataformes |
| `economia` | Economia de Creadors |
| `ia-contingut` | IA i Contingut |
| `mercat-hispanic` | Mercat Hispanòfon |

## Taula Supabase: `llista_tendencies`

| Camp | Tipus | Valors | Notes |
|------|-------|--------|-------|
| `id` | UUID | auto | |
| `categoria_id` | TEXT | vegeu llista | |
| `categoria_nom` | TEXT | lliure | |
| `titol` | TEXT | lliure | Màx 200 car. |
| `resum` | TEXT | lliure | Anàlisi 3-4 frases |
| `font` | TEXT | lliure | Nom publicació |
| `url` | TEXT | lliure | URL font |
| `valoracio` | TEXT | `oportunitat` / `risc` / `neutre` | |
| `data_cerca` | DATE | ISO date | Data de l'execució de l'agent |
| `estat` | TEXT | `pendent` / `guardat` / `eliminat` | Controlat per l'usuari |
| `created_at` | TIMESTAMPTZ | auto | |

## Interacció de l'usuari

- **★ Guardar**: canvia `estat` a `guardat` (la card queda destacada en índigo)
- **Eliminar**: canvia `estat` a `eliminat` (s'oculta de la vista)
- **Filtres**: Tots · Oportunitats · Riscos · Guardats
- **↻ Recarregar**: recarrega des de Supabase
- **⊞ SQL taula**: mostra el SQL per crear la taula si no existeix

## Codi de colors

| Valoració | Color |
|-----------|-------|
| Oportunitat | Verd (#10B981) |
| Risc | Vermell (#DC2626) |
| Neutre | Gris |
| Guardat | Índigo (accent) |

## Agent associat

Documentació completa a [agent-tendencies.md](agent-tendencies.md).
