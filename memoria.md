# Memòria de disseny — Productes digitals Gerard Velez

Aquest fitxer recull les preferències de disseny, decisions estètiques i arquitectura tècnica de Gerard Velez per aplicar-les de manera consistent a qualsevol producte digital.

---

## Paleta de colors

Colors actuals del projecte **Llista.cat** (panell d'administració) — paleta índigo:

```css
--accent:        #6366F1;
--accent-hover:  #4F46E5;
--accent-dim:    rgba(99,102,241,0.08);
--accent-border: rgba(99,102,241,0.25);

--bg-base:       #F7F7FA;
--bg-sidebar:    #F0F0F5;
--bg-card:       #FFFFFF;
--bg-card-hover: #FAFAFD;
--bg-input:      #FFFFFF;

--border:        rgba(0,0,0,0.07);
--border-md:     rgba(0,0,0,0.13);

--text-primary:   #111118;
--text-secondary: #52525B;
--text-muted:     #A1A1AA;

--warn:    #D97706;
--danger:  #DC2626;
--info:    #0EA5E9;
--shadow-sm: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.04);
--shadow-md: 0 4px 14px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);
--shadow-lg: 0 12px 40px rgba(0,0,0,0.14), 0 4px 10px rgba(0,0,0,0.06);
--radius-xl: 16px;
```

---

## Tipografia

- **Font principal**: Montserrat (geomètrica, moderna, llegible)
- **Font monospace**: JetBrains Mono (dades, codis, números)
- Carregades des de Google Fonts

---

## Estil general

- Disseny **simple però molt professional** — estètica de producte SaaS de pagament
- Evitar decoració innecessària
- Jerarquia visual clara
- Micro-detalls cuidats (radis, ombres, transicions)

---

## Decisions per projecte

### Llista.cat — Panell de gestió
- Single-file HTML (tot en un fitxer: HTML + CSS + JS)
- Fitxer principal: `Projecte llista.html`
- 5 mòduls actius: Anàlisi de dades, Recerca creadors, Comunicació, Seguiment (Kanban), Finances
- Backend: Supabase (`dqwteqgdwmivepkdtehy.supabase.co`)
- API Claude: `claude-haiku-4-5-20251001` · clau a localStorage `llista_api_key`
- MCP: `https://llista.lacuinadel.cat/public/mcp` (JSON-RPC 2.0, POST, `Content-Type: text/plain` per evitar CORS preflight)
- Supabase publishable key: `sb_publishable_4kvhAuJQ5JsqBOkI0v_YbQ_lCS-lqy9`
- Finances: Supabase directe (taula `llista_finances`, mateixa connexió que Kanban)

---

## Agent de factures

Script diari (8:00h) que processa factures de `Factures/` amb Claude Vision i les insereix a `llista_finances`.  
Documentació i instruccions de configuració: **`agent-factures.md`**

---

## Mòduls del panell

| Mòdul | Fitxer de referència |
|-------|---------------------|
| Anàlisi de dades | [modul-analisi.md](modul-analisi.md) |
| Recerca de creadors | [modul-recerca.md](modul-recerca.md) |
| Comunicació | [modul-comunicacio.md](modul-comunicacio.md) |
| Seguiment (Kanban) | [modul-kanban.md](modul-kanban.md) |
| Finances | [modul-finances.md](modul-finances.md) |

---

## Skills del projecte

| Skill | Ubicació | Ús |
|-------|----------|-----|
| `saas-design` | `.claude/skills/saas-design/` | Disseny de panells i interfícies SaaS |
| `contingut-llista` | `.claude/skills/contingut-llista/` | Articles de bloc i posts Instagram per Llista.cat |
