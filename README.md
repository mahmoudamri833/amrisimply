# amrisimply
Site amrisimply.com + surveillance automatique des liens affilies

## MCP — 21st.dev

Le serveur MCP 21st.dev est declare dans `.mcp.json` (scope projet, partage via git).
La cle API n'est **pas** dans le depot : elle est lue depuis la variable
d'environnement `TWENTYFIRST_API_KEY`.

Mise en place :

```bash
cp .env.example .env       # puis renseigner TWENTYFIRST_API_KEY
set -a; . ./.env; set +a
claude                     # approuver le serveur "21st" au demarrage
```

Pour l'ajouter en scope local (cle ecrite directement dans la config Claude Code,
hors depot) plutot que via `.mcp.json` :

```bash
claude mcp add --transport http 21st https://21st.dev/api/mcp \
  --header "x-api-key: $TWENTYFIRST_API_KEY"
```

Note : le header doit contenir `: ` entre le nom et la valeur
(`"x-api-key: 21st_sk_..."`), sinon `--header` produit un header vide.
