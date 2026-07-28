---
description: Scan alle addons en vul het Maatwerk register (docs/customizations.csv) + kopieer/download-pagina
argument-hint: <database_name> "<partner_id>"
---

Je gaat het **Maatwerk register** vullen voor deze repo, volgens de procedure in
`CLAUDE.md` §17 (schema in §17.2, kwaliteitsniveaus in §17.3).

## Parameters
- `database_name` = **$1**
- `partner_id` = **$2**

Als `$1` of `$2` leeg is: vraag de gebruiker eerst om de ontbrekende waarde(n)
voordat je verder gaat. Waarschuw kort dat `partner_id` exact als `res.partner`
in de database moet bestaan.

## Stappen

1. **Scan alle addons.** Zoek elk `__manifest__.py` in de repo. Lees per module
   het manifest én de belangrijkste code/bestanden (models, views, data, assets,
   controllers, hooks) om te bepalen wát de module doet.

2. **Leid per module een CSV-regel af** volgens het schema uit §17.2. Kolommen:
   `name, technical_name, database_name, partner_id, process_area_id/id,
   customization_type_id/id, quality_level, criticality, upgrade_risk,
   functional_goal, technical_location, dependencies, test_scenario, status, notes`.
   - Zet `database_name` = `$1` en `partner_id` = `$2` op elke regel.
   - Gebruik externe id's voor relaties: `d1_customization_register.d1_process_area_<key>`
     en `d1_customization_register.d1_ctype_<key>` (keys: zie §17.2).
   - Gebruik technische waarden voor keuzevelden (`quality_level` 1-5;
     `criticality` low/medium/high/business_critical; `upgrade_risk`
     low/medium/high/very_high; `status` active/needs_review/phase_out/
     replace_by_standard/deprecated).
   - Kies het **laagste** kwaliteitsniveau dat het maatwerk beschrijft (§17.3).
     Bij niveau 4/5 is een concreet `test_scenario` verplicht; bij 5 ook een
     motivatie in `notes`. Bij twijfel eerder te hoog inschatten en dit benoemen.
   - `technical_name` = modulenaam. Dedup is op `technical_name` (bestaande regel
     wordt bij import bijgewerkt, niet gedupliceerd).

3. **Schrijf naar `docs/customizations.csv`** (repo-root, UTF-8, komma-gescheiden,
   header op regel 1, alle waardevelden tussen dubbele aanhalingstekens, interne
   `"` verdubbelen). Maak het bestand aan als het nog niet bestaat.

4. **Lever een Artifact-pagina** met de titel `Download customizations.csv` en:
   - een knop **📋 Kopieer naar klembord** (`navigator.clipboard.writeText` met
     fallback naar een `<textarea>` + `document.execCommand('copy')`),
   - een knop **⬇ Download CSV** (Blob + download-link, bestandsnaam
     `customizations.csv`),
   - een leesbaar tekstvak/preview van de inhoud.
   Embed de CSV **verbatim in de pagina zelf** (geen externe fetch). Bouw de
   JS-string veilig op — voeg regels samen met `String.fromCharCode(10)`, nooit
   een echte newline in een quote. Redeploy zo mogelijk op dezelfde artifact-URL.

5. **Print de ruwe CSV in een code-blok** in de chat (kopregel + alle regels,
   zonder extra uitleg in het blok) zodat de consultant het direct kan
   knippen/plakken in de import-wizard (Configuratie → Import customizations →
   veld "Of plak CSV").

6. **Meld expliciet welke velden onzeker waren** en handmatige controle
   verdienen — met name `quality_level`, `upgrade_risk`, `test_scenario`, en
   modules die van conventies afwijken (naamgeving, license, status). Vraag daarna
   of het op een branch gecommit en gepusht moet worden (registratie-check §13).
