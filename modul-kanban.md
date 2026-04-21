# Mòdul Seguiment (Kanban)

Tauler Kanban per fer seguiment de tasques del projecte Llista.cat.

## Taula Supabase: `llista_tasks`

| Camp | Tipus | Valors | Notes |
|------|-------|--------|-------|
| `id` | UUID | auto | |
| `title` | TEXT | lliure | Obligatori |
| `description` | TEXT | lliure | Opcional |
| `status` | TEXT | `pendent` / `en_curs` / `fet` | Columna del tauler |
| `prioritat` | TEXT | `baixa` / `normal` / `alta` | |
| `assignat` | TEXT | UUID del membre | Referència a `llista_members.id` |
| `created_at` | TIMESTAMPTZ | auto | |
| `updated_at` | TIMESTAMPTZ | auto | |

## Taula Supabase: `llista_members`

| Camp | Tipus | Notes |
|------|-------|-------|
| `id` | UUID | auto |
| `name` | TEXT | Obligatori |
| `color` | TEXT | Color HEX de l'avatar |
| `created_at` | TIMESTAMPTZ | auto |

## Columnes del tauler

| Estat | Etiqueta |
|-------|----------|
| `pendent` | Pendent |
| `en_curs` | En curs |
| `fet` | Fet |

## Gestió de membres

- Accessibles des del botó **👥 Membres** a la topbar
- Operacions: crear, editar (nom + color), eliminar
- **Restricció**: no es pot eliminar un membre si té tasques assignades — el sistema mostra un avís amb el llistat de tasques bloquejants
- Colors disponibles: 10 colors predefinits (`MEMBER_COLORS`)
- L'avatar es mostra com a cercle de color amb la inicial del nom

## Lògica

- Les targetes es mouen entre columnes actualitzant el camp `status` i fent upsert a Supabase
- **Fallback local**: tasques a `localStorage('llista_tasks')`, membres a `localStorage('llista_members')`
- El client Supabase és `kanbanSupabase` (compartit amb el mòdul Finances)
- En iniciar la vista es carreguen primers els membres i després les tasques

## Formulari de targeta

Camps: Títol (obligatori), Descripció, Estat, Prioritat, Assignat (select de membres).
