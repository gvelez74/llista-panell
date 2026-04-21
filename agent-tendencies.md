# Agent de tendències — Llista.cat

Script diari (7:00h) que investiga les 5 principals novetats per categoria usant Perplexity (cerca web en temps real) i les desa a Supabase.

## Arxius

| Fitxer | Funció |
|--------|--------|
| `agent-tendencies.py` | Script principal |
| `agent-tendencies.log` | Log d'operacions (generat automàticament) |

## Configuració (primera vegada)

Necessites tres variables d'entorn. Afegeix-les al teu `~/.zshrc`:

```bash
export SUPABASE_KEY="eyJ..."           # service_role key de Supabase
export PERPLEXITY_API_KEY="pplx-..."   # clau de api.perplexity.ai
```

**Perplexity API key**: Registra't a [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api). El pla gratuït inclou crèdits inicials. El model `sonar` costa ~$1/milió tokens (cada execució diària ~$0.01-0.02).

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

1. Per cada categoria, crida Perplexity (`sonar`) amb un prompt especialitzat
2. Perplexity fa cerca web en temps real i retorna JSON estructurat
3. Cada troballa inclou: títol, resum, font, URL, valoració (oportunitat/risc/neutre)
4. S'insereix a `llista_tendencies` amb `estat='pendent'`
5. Des del panell l'usuari pot canviar estat a `guardat` o `eliminat`

## Errors comuns

- **"Falta PERPLEXITY_API_KEY"** → Exporta la variable (veure Configuració)
- **"Falta SUPABASE_KEY"** → Exporta la service_role key
- **JSON invàlid de Perplexity** → Reintenta; rarament el model retorna format incorrecte
- **Error de taula** → Crea la taula amb el SQL de dalt (botó "⊞ SQL taula" al panell)
