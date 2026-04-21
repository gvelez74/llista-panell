# Mòdul Recerca de creadors

Revisió i presa de decisions sobre suggeriments de nous creadors per incorporar a Llista.cat.

## Font de dades

Fitxer CSV al repositori GitHub: `gvelez74/llista-recerca/dades/suggeriments.csv`

Lectura via GitHub API (GET → base64 decode → parse CSV).  
Escriptura via PUT amb token d'autenticació.

## Camps de la taula

| Camp CSV | Visualització | Notes |
|----------|--------------|-------|
| Creador | Nom + enllaç | |
| Plataforma | Badge de color | Instagram, TikTok, YouTube... |
| `%_Català` | Barra de progrés + % | Normalitza variants (`%_Catala`, `%_catala`) |
| Posts analitzats | Número | |
| Data detecció | Data | |
| Estat | Badge | `pendent` o valor de la columna |
| Decisió | Dropdown | `— Pendent —` / `Incorporar` / `Descartar` |

## Flux de decisions

1. L'usuari revisa cada fila i selecciona `Incorporar` o `Descartar`
2. S'emplena automàticament `Data decisió` (ISO date)
3. En guardar: les files modificades s'escriuen de tornada al CSV via GitHub API
4. Missatge de commit: `Decisions del panell — {ISO date}`

## Autenticació GitHub

- Token guardat a `localStorage('llista_gh_token')` (opcional)
- Sense token: mode lectura únicament
- Amb token (Bearer): lectura + escriptura de decisions

## Badge de pendents

La icona del mòdul mostra un comptador (`#badge-recerca`) amb el nombre de files amb decisió pendent.
