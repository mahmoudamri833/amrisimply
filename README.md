# amrisimply
Site amrisimply.com + surveillance automatique des liens affilies

## MCP — 21st.dev

Endpoint : `https://21st.dev/api/mcp` (HTTP), header `x-api-key`, cle lue depuis
la variable d'environnement `API_KEY_21ST`. Ces valeurs sont celles du plugin
officiel : https://github.com/21st-dev/claude-code-plugin

### Option 1 — plugin officiel (recommande)

Dans une session `claude` interactive :

```
/plugin marketplace add 21st-dev/claude-code-plugin
/plugin install 21st@21st
```

Le plugin installe le serveur MCP **et** quatre skills (`21st-cli-use`,
`21st-ai`, `21st-registry`, `21st-design-sync`). Exporter la cle avant :

```bash
export API_KEY_21ST="21st_sk_..."      # Windows : variable utilisateur API_KEY_21ST
```

### Option 2 — `.mcp.json` du depot

Le fichier `.mcp.json` a la racine declare le meme serveur en portee projet.
Aucun secret dedans : il reference `${API_KEY_21ST}`.

```bash
cp .env.example .env       # puis renseigner API_KEY_21ST
set -a; . ./.env; set +a
claude                     # approuver le serveur "21st" au demarrage
```

> Les deux options declarent un serveur nomme `21st`. Utiliser l'une **ou**
> l'autre, pas les deux, pour eviter un doublon entre portee plugin et projet.

### Option 3 — enregistrement manuel

```bash
claude mcp add --transport http --scope user 21st https://21st.dev/api/mcp \
  --header "x-api-key: $API_KEY_21ST"
```

Le header doit contenir `: ` entre le nom et la valeur. Sans les deux-points,
`--header` ne separe jamais le nom de la valeur et la cle n'est pas transmise :

```
FAUX  --header "x-api-key21st_sk_..."
BON   --header "x-api-key: 21st_sk_..."
```

### Verification

```bash
claude mcp list    # attendu : 21st: https://21st.dev/api/mcp (HTTP) - Connected
```
