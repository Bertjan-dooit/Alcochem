---
description: Sync de centrale dooIT-richtlijnen en slash-commands vanuit dooIT-nl/dev-guidelines
---

Je synchroniseert de centrale dooIT-tooling vanuit de (publieke) repo
`github.com/dooIT-nl/dev-guidelines` naar de **huidige** repo. Doel: de gedeelde
richtlijnen én slash-commands actueel houden zonder handmatig kopiëren.

## Wat je ophaalt en waar het heen gaat
- `guidelines.md`        → `.dooit/guidelines.md`      (de centrale richtlijnen)
- `commands/*.md`        → `.claude/commands/`         (de gedeelde slash-commands)

**Niet aanraken:** de `CLAUDE.md` in de repo-root. Dat is de stub met
`@.dooit/guidelines.md` plus eventuele repo-specifieke aanvullingen — die moeten
bij een sync behouden blijven.

## Stappen

1. **Werk vanuit de repo-root** (`git rev-parse --show-toplevel`).

2. **Haal de centrale repo op** als tarball en pak alleen de benodigde paden uit
   naar een tijdelijke map. `-f` laat curl falen bij een HTTP-fout:
   ```bash
   TMP=$(mktemp -d)
   curl -fsSL https://api.github.com/repos/dooIT-nl/dev-guidelines/tarball \
     | tar -xz -C "$TMP" --strip-components=1 --wildcards '*/commands/*' '*/guidelines.md'
   ```
   Faalt curl (exit ≠ 0)? Meld dat de repo niet bereikbaar is (netwerk of naam)
   en stop.

3. **Plaats de bestanden:**
   ```bash
   mkdir -p .dooit .claude/commands
   cp "$TMP/guidelines.md" .dooit/guidelines.md
   cp "$TMP/commands/"*.md .claude/commands/
   rm -rf "$TMP"
   ```

4. **Toon wat er wijzigt.** Draai `git status --short` en
   `git --no-pager diff --stat`. Niets gewijzigd? Meld "richtlijnen zijn al
   up-to-date" en stop.

5. **Committen en pushen** (na akkoord van de gebruiker; nooit direct op `main` —
   branch eerst indien nodig, conform de guidelines §13):
   ```bash
   git add .dooit/guidelines.md .claude/commands
   git commit -m "chore: sync dooIT guidelines + commands"
   odoosh-push
   ```
   Gebruik **`odoosh-push`**, nooit `git push`.

6. **Meld het resultaat:** welke bestanden zijn bijgewerkt, en of er nieuwe of
   verwijderde commands waren. Wijs erop dat nieuwe slash-commands pas na een
   herstart van de Claude Code-sessie verschijnen.
