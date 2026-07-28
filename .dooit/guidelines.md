# CLAUDE.md — dooIT Odoo Development Richtlijnen

Deze file beschrijft hoe Claude (en elke andere AI-tool) code, views en
configuratie binnen een dooIT Odoo-project moet genereren. Plak deze file in
de root van elke nieuwe module-repo.

> **Projectgegevens:**
> - Project: `dooIT modules (Odoo.sh)`
> - Odoo versie: `19.0`
> - Module prefix: `d1_` (generiek) of `d1_<klantcode>_` (klantspecifiek)

---

## 0. Kernprincipes

* **Taal:** code, identifiers, manifests, log-messages en commit-messages in
  **Engels**. Docstrings, README en in-line uitleg mogen Nederlands.
* **Prefix `d1` op alles** wat dooIT toevoegt of overschrijft (models, velden,
  XML-id's, groepen, klassen) — zie sectie 1.
* **Views via XPath-extensies** in eigen view-records. Standaard Odoo-XML wordt
  in development **nooit** rechtstreeks gewijzigd. (De `#D1`-commentaar-werkwijze
  is uitsluitend voor handmatige aanpassingen door consultants, niet voor
  gegenereerde code.)
* **Geen klantspecifieke logica in generieke modules.** Maak een klant-module
  die `depends` op de generieke module.
* **Bij twijfel: vraag, raad niet.** Liever één extra vraag dan een verkeerde
  aanname die later om-gebouwd moet worden.

---

## 1. Naamgeving

### Prefix-tabel

| Wat | Prefix | Voorbeeld |
|-----|--------|-----------|
| Eigen module-map | `d1_` | `d1_copy_project_task/` |
| Model `_name` | `d1.` | `_name = "d1.copy.project.task.wizard"` |
| Extra velden op bestaand Odoo-model | `d1_` | `d1_is_template = fields.Boolean(...)` |
| Velden binnen eigen `d1.`-model | geen prefix | `is_template = fields.Boolean(...)` |
| XML view record id | `d1_` | `id="d1_res_partner_view_buttons"` |
| XML view `name`-veld | `.d1` | `name="d1.res.partner.form"` |
| XML action / menu-item id | `d1_` | `id="d1_action_voyage_list"` |
| Cron records (XML id) | `d1_` | `id="d1_cron_clean_logs"` |
| Demo-/data-records (XML id) | `d1_` | `id="d1_demo_partner_acme"` |
| Security group (XML id + label) | `d1_` | `id="d1_group_logistics_manager"` |
| `ir.model.access.csv` id | `access_` | `access_d1_voyage_user` |
| Automated Actions (label) | `d1 ` | `"d1 Factuur versturen bij bevestiging"` |
| Server Actions (label) | `d1 ` | `"d1 Herbereken marge"` |
| Python klassenamen | `D1` | `class D1VoyageLine(models.Model):` |
| Klantspecifieke module | `d1_<klantcode>_` | `d1_acme_invoice_layout` |

### Method-namen (Odoo-conventie)

| Methode-soort | Patroon | Voorbeeld |
|---------------|---------|-----------|
| Compute | `_compute_<veld>` | `_compute_total_amount` |
| Default | `_default_<veld>` | `_default_user_id` |
| Inverse | `_inverse_<veld>` | `_inverse_partner_name` |
| Search | `_search_<veld>` | `_search_is_overdue` |
| Onchange | `_onchange_<veld>` | `_onchange_partner_id` |
| Constrains | `_check_<beschrijving>` | `_check_quantity_positive` |
| Button-callback | `action_<verb>` | `action_confirm`, `action_send_mail` |
| Cron | `_cron_<beschrijving>` | `_cron_send_reminders` |
| Private helper | `_<naam>` | `_prepare_invoice_vals` |

---

## 2. Views — XPath-extensies (development)

> Voor AI-gegenereerde code: **altijd** XPath-extensies, **nooit** standaard
> Odoo-XML rechtstreeks wijzigen.

```xml
<record id="d1_res_partner_view_form" model="ir.ui.view">
    <field name="name">res.partner.form.d1</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='vat']" position="after">
            <field name="d1_is_template"/>
        </xpath>
    </field>
</record>
```

**Regels:**

* Record id: `d1_<model>_<view_type>[_<doel>]`
* `<field name="name">`: `<model>.<view_type>.d1[.<doel>]`
* Prefereer `position="after"` / `before` / `attributes` boven `replace`
  (minder fragiel bij Odoo-upgrades).
* Gebruik attribuut-matchers (`//field[@name='xxx']`), nooit positie-selectors
  zoals `//div[1]/div[3]`.
* Eén view-record per logische aanpassing — niet meerdere onsamenhangende
  wijzigingen samen.

---

## 3. Module-structuur

```
d1_mijn_module/
├── __init__.py                       # alleen imports, geen logica
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   └── <model>.py
├── views/
│   └── <model>_views.xml
├── wizards/
├── reports/
├── data/
├── demo/
├── security/
│   ├── ir.model.access.csv
│   └── <module>_security.xml         # groepen + record rules
├── controllers/                      # alleen indien nodig
├── i18n/                             # .pot + .po
├── static/
│   └── description/
│       ├── icon.png                  # dooIT logo (verplicht)
│       └── index.html                # optioneel
└── tests/
    ├── __init__.py
    └── test_<feature>.py
```

---

## 4. Manifest

* **Taal:** Engels.
* **Verplicht:** `name, summary, version, category, author, license, depends, data, installable`.
* **Vast:** `"author": "dooIT B.V."`, `"license": "LGPL-3"`.
* **`depends`:** zo minimaal mogelijk — alleen wat echt nodig is.
* **`application`:** `False`, tenzij het een volwaardige standalone app is.
* **`version`:** `<odoo-versie>.<major>.<minor>.<patch>` (bv. `19.0.1.5.0`).
* **`description`:** changelog — zie hieronder.

```python
{
    "name": "Copy Project Tasks from Template",
    "summary": "Copy tasks (including subtasks) from template projects",
    "version": "19.0.1.5.0",
    "category": "Project",
    "author": "dooIT B.V.",
    "website": "https://dooit.nl",
    "license": "LGPL-3",
    "depends": ["project"],
    "data": [
        "security/ir.model.access.csv",
        "security/d1_copy_project_task_security.xml",
        "wizards/copy_project_task_wizard_views.xml",
        "views/project_project_views.xml",
    ],
    "installable": True,
    "application": False,
    "description": """
        Copy Project Tasks 19.0.1.5.0
        =============================
        * v1.5: ondersteuning voor subtaak-deadlines
        * v1.4: optie om assignees mee te kopiëren
    """,
}
```

---

## 5. Python / Modellen

### Bestandsindeling (top of file)

```python
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)
```

### Volgorde binnen een model-klasse

1. `_name`, `_description`, `_inherit`, `_order`, `_rec_name`, `_sql_constraints`
2. Velden (logisch gegroepeerd of alfabetisch)
3. `_default_*` methoden
4. `@api.depends` compute-methoden
5. `@api.onchange`
6. `@api.constrains`
7. CRUD-overrides (`create`, `write`, `unlink`, `copy`)
8. `action_*` business-methoden
9. Private helpers

### Regels

* **Geen bare `except:`.** Minimaal `except Exception as e:` met
  `_logger.exception(...)` of `_logger.error(...)`.
* **Docstring per publieke methode** — wat doet het, welke context wordt
  verwacht, wat is de return.
* **Geen logica in `__init__.py` of `__manifest__.py`** (`__init__.py` doet
  alleen imports).
* **Validaties:** `_sql_constraints` voor database-niveau, aanvullend
  `@api.constrains` voor business-logica.
* **`_()` rond alle user-facing strings** (UserError, notificaties, labels).
* **Excepties:** `UserError` voor verwachte fouten, `ValidationError` voor
  constraint-violations, `AccessError` voor permissies.
* **Vermijd `.sudo()`** — alleen gebruiken als security-bypass bewust nodig
  is, met commentaar waarom.
* **Vermijd `self.env.cr.execute()`** — alleen als ORM ontoereikend is. Altijd
  parameterized queries, nooit string-interpolatie.
* **Recordset-vriendelijk:** methoden werken op `self` als recordset, niet als
  enkele record. Gebruik `for rec in self:` waar nodig.
* **Gebruik `mapped()`, `filtered()`, `sorted()`** boven Python-loops.
* **Datums:** `fields.Datetime` (UTC); conversie naar user-tz doet Odoo.
* **Bedragen:** `fields.Monetary(currency_field='currency_id')` — nooit
  `fields.Float` voor geld.

---

## 6. Security

### `security/ir.model.access.csv`

* Altijd aanmaken, ook bij tijdelijk open access — documenteer dan expliciet
  waarom.
* Eén regel per (model × groep).
* Id-naamgeving: `access_<model_snake>_<group_short>`.
* Alle vier perms expliciet (`perm_read,perm_write,perm_create,perm_unlink`).

### `security/<module>_security.xml` (groepen + record rules)

* Groep-id's: `d1_group_<module>_user`, `d1_group_<module>_manager`.
* Manager erft van user via `implied_ids`.
* Categorie via `category_id` (eigen of `base.module_category_*`).
* **Record rules voor row-level security** — niet via Python-filtering in
  methoden.
* **Multi-company:** rules altijd met
  `('company_id', 'in', company_ids)` of `('company_id', '=', False)`.

---

## 7. Studio vs Maatwerk

| Situatie | Aanpak |
|----------|--------|
| Eenvoudig extra veld, geen logica | Studio |
| Aanpassing lay-out bestaande view (handmatig) | Studio of `#D1`-werkwijze |
| Compute-veld, constraint, Python-logica | Maatwerk module |
| Integratie met extern systeem | Altijd maatwerk module |

Studio-wijzigingen zijn niet versioned. Documenteer in `README.md` van de
module (of in een notitieveld in Odoo) welke aanpassingen via Studio zijn
gedaan. Exporteer periodiek als module.

---

## 8. Automated Actions & Server Actions

* Naam-label begint met `d1 ` (spatie, geen underscore).
* `description`-veld vult **doel, aanmaakdatum, auteur**.
* Test eerst handmatig als Server Action vóór je de trigger activeert.

---

## 9. Logging

* `_logger.info(...)` — business-events.
* `_logger.warning(...)` — onverwachte maar herstelbare situaties.
* `_logger.error(...)` / `_logger.exception(...)` — echte fouten.
* **Geen `print()`** in productiecode.
* **Geen gevoelige data** in logs (klantgegevens, tokens, wachtwoorden, PII).

---

## 10. Vertalingen (i18n)

* Wrap user-facing strings in `_()` (geïmporteerd uit `odoo`).
* Exporteer `.pot` per module:
  `odoo-bin --i18n-export=i18n/d1_mijn_module.pot -d <db> --modules=d1_mijn_module`.
* Plaats taal-bestanden in `i18n/`: `nl_NL.po`, `en_US.po`.

---

## 11. Performance

* **Aggregaties:** `read_group()` in plaats van Python-sum loops.
* **Vermijd N+1:** `partners.mapped('country_id.name')` i.p.v. loop met
  attribute-access.
* **Indexes:** `fields.Char(index=True)` op velden gebruikt in
  search/domain/group_by.
* **Stored compute:** alleen als je erop zoekt of het in een
  tree/kanban-view toont. Anders non-stored.
* **`@api.depends(...)`:** vermeld alle dependencies expliciet — anders
  herberekent Odoo niet.
* **Batches:** vermijd `for record in big_recordset: record.write({...})` —
  doe `big_recordset.write({...})` of split per groep.

---

## 12. Testen

* `tests/__init__.py` importeert alle test-bestanden.
* Tests erven van `odoo.tests.common.TransactionCase` (of `HttpCase` voor
  controllers).
* **Minimaal één smoke-test per kritisch model:** create, default values, key
  compute, één business-action.
* Tag tests met `@tagged('d1_<module>')` zodat ze selectief draaibaar zijn:
  `--test-tags=d1_<module>`.

---

## 13. Git & Odoo.sh

* **Repo:** `https://github.com/dooIT-nl/modules` — module op juiste
  versie/branch.
* **Branching:** nooit direct op `main`. Branch per feature of
  klant-aanpassing.
* **Branch-naam:** `feature/d1_<module>` of `fix/d1_<module>_<short>`.
* **Conventional commits:**
  * `feat: d1_voyage — voeg lading-tracking toe aan voyage lines`
  * `fix: d1_powerpick — bare except vervangen door exception logging`
  * `docs: d1_voyage — manifest changelog bijgewerkt naar v19.13.5`
* **PR review verplicht** voor productie-merges.
* **`.gitignore` minimaal:** `*.pyc`, `__pycache__/`, `.idea/`, `.vscode/`,
  `*.swp`, `.DS_Store`, `.env`.
* **Geen credentials/API-keys/klantdata in code.**
  * Configureerbare waarden → `ir.config_parameter`.
  * Secrets → Odoo.sh environment variables.
* **Pushen op Odoo.sh:** gebruik `odoosh-push`, **nooit** `git push`.
* **Vóór elke push — registratie-check (verplicht):** vraag altijd expliciet of
  het gewijzigde/nieuwe maatwerk in het **Maatwerk register** moet worden
  opgenomen (zie §17). Is dat nog niet gebeurd, bied dan aan de registratie uit
  te voeren (regel toevoegen aan `docs/customizations.csv`) **vóór** de push.
  Sla dit alleen over als de gebruiker het expliciet aangeeft, of als er
  aantoonbaar geen maatwerk is gewijzigd.

---

## 14. Documentatie per module

Elke module bevat minimaal:

* `README.md` — doel, installatie-instructies, gebruikersinstructies, bekende
  beperkingen, contactpersoon.
* `__manifest__.py` `description` — changelog (zie sectie 4).
* `static/description/icon.png` — dooIT logo (verplicht voor herkenbaarheid in
  de Apps-lijst).
* `static/description/index.html` — optioneel, voor uitgebreidere weergave in
  Apps-overzicht.

---

## 15. Klantspecifieke modules

* **Geen** klantspecifieke logica in generieke modules.
* Klant-module `depends` op (of erft van) de generieke module.
* Naam: `d1_<klantcode>_<functie>` — bv. `d1_acme_invoice_layout`.

---

## 16. Werkwijze voor Claude

Wanneer je een module of feature genereert:

1. **Vraag eerst** wat onduidelijk is — Odoo-versie, klantcode, exacte scope.
2. **Lever een complete module-structuur** (alle `__init__.py`'s, manifest,
   security CSV, minimaal één test) — geen halve oplevering.
3. **Volg de prefix- en method-naamgeving exact** (sectie 1).
4. **Views: altijd XPath-extensies** (sectie 2). Geen directe wijziging van
   standaard Odoo-XML.
5. **`_()`** rond alle user-facing strings.
6. **Smoke-test** in `tests/` bij elk nieuw model.
7. **Manifest `description`** bijwerken met versie-bullet bij elke wijziging.
8. **Verklaar afwijkingen** — als een richtlijn niet past in een specifiek
   geval, geef expliciet aan waarom je afwijkt en wacht op bevestiging.
9. **Registreer het maatwerk** — leg elke customization vast in het Maatwerk
   register via `docs/customizations.csv`, in dezelfde commit/PR als de code
   (zie sectie 17).

---

## 17. Maatwerk register bijhouden (verplicht)

Alle customizations worden centraal vastgelegd in het **Maatwerk register**
(module `d1_customization_register`) voor consultancy, support en upgrades. Om
te voorkomen dat het register verwatert, gebeurt het vastleggen **op het moment
van bouwen**, als onderdeel van dezelfde wijziging — niet als losse klus
achteraf.

### 17.1 Standing rule

* **Na elke customization** — nieuwe `d1_`-module, technische override, view,
  server action, integratie, structurele afwijking, of een geëxporteerde
  Studio-aanpassing — voeg je een regel toe aan (of werk je bij in)
  `docs/customizations.csv` in de repo-root.
* Doe dit **in dezelfde commit/PR als de code**. PR-review controleert of de
  regel aanwezig en correct is.
* Vraag Claude om de registratie uit te voeren — bv. **"registreer dit
  maatwerk"** (of typ `register-customization`). Claude volgt dan de procedure
  in 17.4 en genereert de regel uit de git-diff. Er is **geen extra bestand,
  commando of installatie** nodig: deze CLAUDE.md is zelfvoorzienend — het enige
  wat je per development hoeft te doen is deze CLAUDE.md gebruiken.
* De CSV is de **staging-bron**; regels worden periodiek in het Odoo-register
  geïmporteerd (zie 17.5). Committen ≠ geïmporteerd.
* **Bij iedere push** vraagt Claude of het maatwerk geregistreerd moet worden
  (zie §13, "registratie-check"). Zo blijft het register vanzelf gevuld.

### 17.2 CSV — locatie en schema

* Locatie: `docs/customizations.csv` (repo-root), UTF-8, komma-gescheiden, mét
  header. Eén regel per customization.
* Kolommen (in deze volgorde), direct importeerbaar in Odoo:

  ```
  name,technical_name,database_name,partner_id,process_area_id/id,customization_type_id/id,quality_level,criticality,upgrade_risk,functional_goal,technical_location,dependencies,test_scenario,status,notes
  ```

* **Relaties** — gebruik externe id's (robuust), niet labels:
  * `process_area_id/id`: `d1_customization_register.d1_process_area_<key>`
    (keys: `sales, purchase, inventory, manufacturing, accounting, crm,
    website, pos, project, hr, documents, integrations, security, reporting,
    other`).
  * `customization_type_id/id`: `d1_customization_register.d1_ctype_<key>`
    (keys: `standard_configuration, studio, managed_module,
    technical_override, structural_deviation, view, report, server_action,
    integration, security_rule, other`).
  * `partner_id`: exacte contactnaam (`res.partner`), of leeg laten.
* **Keuzevelden** — gebruik de technische waarde, niet het label:
  * `quality_level`: `1`–`5`
  * `criticality`: `low, medium, high, business_critical`
  * `upgrade_risk`: `low, medium, high, very_high`
  * `status`: `active, needs_review, phase_out, replace_by_standard, deprecated`
* **Overslaan:** `code` (auto CUST-…), `risk_score`/`risk_category`
  (berekend). `technical_owner_id` wordt bij import bepaald of naderhand gezet.
* Waarden met komma's, aanhalingstekens of nieuwe regels: omhullen met dubbele
  aanhalingstekens (`"..."`), interne `"` verdubbelen.

Voorbeeldregel:

```csv
name,technical_name,database_name,partner_id,process_area_id/id,customization_type_id/id,quality_level,criticality,upgrade_risk,functional_goal,technical_location,dependencies,test_scenario,status,notes
"Kredietcheck bij SO-bevestiging","d1_beta_sale_credit","beta-odoosh","Beta N.V.","d1_customization_register.d1_process_area_sales","d1_customization_register.d1_ctype_technical_override","4","high","high","Blokkeer bevestiging boven kredietlimiet","sale.order.action_confirm() override","sale_management,account","Order boven limiet -> UserError; binnen limiet -> OK","needs_review","Bewust gekozen override"
```

### 17.3 Kwaliteitsniveau kiezen

Kies het **laagste** niveau dat de vraag oplost:

| Niveau | Betekenis | Wanneer |
|--------|-----------|---------|
| 1 | Standaard configuratie | Opgelost met instellingen; geen code/Studio |
| 2 | Studio / laag-risico | Eenvoudig veld/layout via Studio, geen logica |
| 3 | Uitbreiding (beheerde module) | Nette module die uitbreidt via `_inherit` |
| 4 | Technische override | Bewust standaardgedrag overschrijven (testscenario verplicht) |
| 5 | Structurele afwijking | Kernlogica herschreven (testscenario + motivatie in `notes` verplicht) |

`criticality` = impact voor de klant; `upgrade_risk` = kans dat het breekt bij
een versie-upgrade. Bij niveau 4/5 is `test_scenario` verplicht; bij niveau 5
ook een motivatie in `notes` (dit wordt in Odoo afgedwongen).

### 17.4 Maatwerk registreren — procedure

Trigger: de gebruiker vraagt het maatwerk te registreren, bv. **"registreer dit
maatwerk"**, "registreer deze customization" of "register-customization". Er is
hiervoor **geen slash-command of extra bestand** nodig; deze procedure staat in
CLAUDE.md en is dus in elke sessie beschikbaar.

Doel: uit de huidige wijzigingen automatisch een correcte CSV-regel opstellen,
zodat registreren vrijwel geen moeite kost.

Werkwijze wanneer dit wordt gevraagd:

1. **Bepaal de scope** — standaard de git-diff van de huidige branch t.o.v.
   `main`; of een opgegeven module/commit-range.
2. **Leid automatisch af uit de code:**
   * `name` — korte, herkenbare omschrijving;
   * `technical_name` — module-/model-/methodenaam of XML-id;
   * `dependencies` — uit `depends` in `__manifest__.py`;
   * `technical_location` — gewijzigde bestanden/models/methods/view-id's;
   * `process_area_id/id` en `customization_type_id/id` — beste inschatting;
   * `functional_goal` — afgeleid uit code/commit/README.
3. **Stel een onderbouwd voorstel op** voor `quality_level`, `criticality`,
   `upgrade_risk` en een **concreet** `test_scenario` — met korte motivatie
   per keuze (dit is waar de mens anders op vastloopt).
4. **Vraag alleen wat niet af te leiden is** — meestal `database_name`,
   `partner_id` en soms `business_owner`.
5. **Toon het voorstel ter bevestiging**, voeg daarna de regel toe aan
   `docs/customizations.csv` (juiste escaping; externe id's voor relaties;
   waarden voor keuzevelden; header aanmaken als het bestand nog niet bestaat).
6. **Toon de CSV in de chat — verplicht.** Print na het toevoegen de
   **kopregel + de zojuist toegevoegde regel(s)** in een gewoon code-blok, zodat
   de consultant het met de muis kan selecteren en **knippen/plakken** in de
   import-wizard (Configuratie → Import customizations → veld "Of plak CSV").
   Dit is de primaire overdracht: downloaden van bestanden werkt vaak niet in de
   omgeving, kopiëren uit de chat altijd. Zet in het code-blok géén extra uitleg
   of prefix — alleen de ruwe CSV-regels.
7. **Meld expliciet welke velden onzeker waren** en handmatige controle
   verdienen (met name niveau, risico en testscenario).

Uitgangspunten: nooit gokken op klant/database — vragen. Bij twijfel over het
niveau: eerder te hoog dan te laag inschatten en dit benoemen.

### 17.5 Importeren in Odoo

* **Aanbevolen — import-wizard:** in Odoo **Configuratie → Import
  customizations**. Plak de CSV of upload het bestand. De wizard matcht
  procesgebied/​type op externe id **of** naam (maakt ze desgewenst aan),
  keuzevelden op waarde, en **dedupliceert op `technical_name`** (bestaande
  regel wordt bijgewerkt i.p.v. gedupliceerd). Fouten worden **per regel**
  gemeld; goede regels gaan door.
* Alternatief: **Maatwerk register → lijst → Favorieten → Importeren** met
  `docs/customizations.csv` (standaard Odoo-import; kolomkoppen matchen 1-op-1).
* Controleer na import de automatisch toegekende `code` (CUST-…) en vul
  `technical_owner_id` waar nodig.

