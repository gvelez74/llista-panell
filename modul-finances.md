# Mòdul Finances

Gestió del pressupost i despeses reals de Llista.cat. Connexió directa a Supabase (no Vercel).

## Taula Supabase: `llista_finances`

| Camp | Tipus | Valors | Notes |
|------|-------|--------|-------|
| `id` | UUID | auto | `gen_random_uuid()` |
| `project_id` | TEXT | `'llista-cat'` | Sempre fix |
| `type` | TEXT | `'expense'` / `'income'` | Despesa o ingrés |
| `is_budget` | BOOLEAN | `true` / `false` | Previst o real |
| `categoria` | TEXT | vegeu llista | |
| `concept` | TEXT | lliure | Nom del proveïdor |
| `description` | TEXT | lliure | Concepte/descripció de la factura |
| `amount` | DECIMAL(10,2) | decimal € | **Import sense IVA** |
| `month` | INTEGER | 0–11 | 0 = Gener, 11 = Desembre |
| `created_at` | TIMESTAMPTZ | auto | Generat per Supabase |

SQL per crear la taula accessible des del botó **"⊞ SQL taula"** del panell.

## Categories

`COMUNICACIÓ` · `TECNOLOGIA` · `CONSULTORIA` · `PERSONAL` · `ESPAIS` · `SERVEIS` · `SUBVENCIONS` · `ALTRES`

Colors assignats per categoria (constants `FIN_CAT_COLORS` al codi).

## Lògica de doble dimensió

Cada registre té **dues dimensions independents**:

| Dimensió | Camp | Valors |
|----------|------|--------|
| Tipus | `type` | `expense` (despesa) / `income` (ingrés) |
| Estat | `is_budget` | `true` (previst) / `false` (real) |

Combinació habitual: `expense + is_budget=false` → despesa real (factura processada per l'agent).

## Seccions del mòdul

- **Dashboard** — resum global: total ingressos previstos/reals, total despeses, saldo
- **Pressupost** — taula filtrable (tipus, estat, categoria) amb 8 columnes
- **Detall** — agrupació per categoria amb totals
- **Evolució** — gràfic mensual/trimestral (Chart.js)

## Connexió Supabase

Reutilitza el client `kanbanSupabase` (funció `finGetSb()`). Si Kanban no s'ha connectat, crea una nova instància amb la mateixa URL i clau.

## Agent de factures

Les factures es poden processar automàticament via `agent-factures.py`.  
Sempre insereix amb `type='expense'`, `is_budget=false`.  
Documentació: [agent-factures.md](agent-factures.md)
