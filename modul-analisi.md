# Mòdul Anàlisi de dades

Visualització de dades de la base Llista.cat i assistent AI amb accés en temps real via MCP.

## Pestanyes

| Clau | Contingut |
|------|-----------|
| `tab-resum` | Estadístiques globals (creadors, posts, registres hist., transcripcions) + gràfic per plataforma |
| `tab-tendencies` | Anàlisi de tendències |
| `tab-assistent` | Xat amb Claude + eines MCP |

## Eines MCP disponibles

Servidor: `https://llista.lacuinadel.cat/public/mcp`  
Protocol: JSON-RPC 2.0 · POST · `Content-Type: text/plain` (evita CORS preflight)

| Eina | Retorna | Paràmetres principals |
|------|---------|----------------------|
| `get_counts` | `{projectes, posts, historica, transcripcions}` | — |
| `get_projectes` | Llista de creadors | `territori`, `categories`, `limit`, `offset` |
| `get_posts` | Publicacions | `id_creador`, `type`, `limit` |
| `get_transcripcions` | Transcripcions de vídeo | `search`, `limit` |

## Assistent AI

- Model: `claude-haiku-4-5-20251001`
- Clau API: `localStorage('llista_api_key')` — mai s'envia a tercers
- La clau es configura inline al xat (si no hi és, apareix camp d'entrada directament al bubble de benvinguda)
- Bucle tool-use: si Claude retorna `stop_reason: 'tool_use'`, el panell executa l'eina MCP i continua

### Consultes ràpides predefinides (`ASSISTENT_CHIPS`)

- Quants creadors hi ha a les Illes Balears?
- Quines categories tenen més creadors?
- Busca transcripcions sobre cuina catalana
- Creadors de videojocs al País Valencià
- Posts recents de tipus YouTube
- Resum general de la base de dades

## Estat del sistema (Dashboard)

El Resum mostra l'estat de: connexió MCP, auto-recerca, YouTube API Key, GitHub Action.
