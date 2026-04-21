# Agent de tendències — Llista.cat

Script diari (7:00h) que investiga les 5 principals novetats per categoria usant Perplexity (cerca web en temps real) i les desa a Supabase.

## Arxius

| Fitxer | Funció |
|--------|--------|
| `agent-tendencies.py` | Script principal |
| `agent-tendencies.log` | Log d'operacions (generat automàticament) |

## Configuració (primera vegada)

Necessites dues variables d'entorn. Afegeix-les al teu `~/.zshrc`:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."  # mateixa clau que uses al panell
export SUPABASE_KEY="eyJ..."           # service_role key de Supabase
```

**No requereix cap API addicional.** Usa la clau d'Anthropic que ja tens i fonts RSS públiques gratuïtes.

Recàrrega: `source ~/.zshrc`

## Execució manual

```bash
cd "/Users/gvelez/Library/CloudStorage/OneDrive-FundaciópuntCAT/Gerard Velez/3. Projectes/1. llista/99. Agents llista"
python3 agent-tendencies.py
```

## Cron diari (7:00h)

Configurat via CronCreate. Executa cada dia a les 7:00h.

## Categories investigades

| ID | Nom | Focus |
|----|-----|-------|
| `algoritmes` | Algoritmes | Canvis d'algoritme a YouTube, TikTok, Instagram, X |
| `metriques` | Mètriques i Analytics | Noves mètriques, eines d'analítica, KPIs |
| `plataformes` | Tendències de Plataformes | Novetats de funcionalitats, monetització, polítiques |
| `economia` | Economia de Creadors | Brand deals, fons, patrocinis, models de negoci |
| `ia-contingut` | IA i Contingut | Eines IA, impacte en creadors, regulació |
| `mercat-hispanic` | Mercat Hispanòfon | Tendències a Espanya, LATAM i mercat català |

## Taula Supabase: `llista_tendencies`

```sql
CREATE TABLE llista_tendencies (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  categoria_id TEXT NOT NULL,
  categoria_nom TEXT NOT NULL,
  titol TEXT NOT NULL,
  resum TEXT NOT NULL,
  font TEXT DEFAULT '',
  url TEXT DEFAULT '',
  valoracio TEXT DEFAULT 'neutre',  -- 'oportunitat' | 'risc' | 'neutre'
  data_cerca DATE NOT NULL,
  estat TEXT DEFAULT 'pendent',     -- 'pendent' | 'guardat' | 'eliminat'
  created_at TIMESTAMPTZ DEFAULT now()
);
ALTER TABLE llista_tendencies ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all" ON llista_tendencies FOR ALL USING (true) WITH CHECK (true);
```

## Flux

1. Per cada categoria, llegeix els RSS feeds associats (últimes 72h)
2. Recull fins a 30 articles recents filtrant duplicats per URL
3. Envia els articles a Claude (`claude-sonnet-4-6`) amb un prompt especialitzat
4. Claude analitza, selecciona les 5 tendències més rellevants i les valora (oportunitat/risc/neutre)
5. Si no hi ha articles recents als feeds, Claude usa el seu coneixement del sector
6. S'insereix a `llista_tendencies` amb `estat='pendent'`
7. Des del panell l'usuari pot guardar o eliminar cada entrada

## Errors comuns

- **"Falta ANTHROPIC_API_KEY"** → Exporta la variable (veure Configuració)
- **"Falta SUPABASE_KEY"** → Exporta la service_role key
- **RSS no disponible** → Avís al log, continua amb els altres feeds; Claude usa coneixement propi
- **JSON invàlid de Claude** → Reintenta l'execució manual
- **Error de taula** → Crea la taula amb el SQL de dalt (botó "⊞ SQL taula" al panell)
