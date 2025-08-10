EKalk – Kalkulationstool für Elektroumfänge an Förder- und Sortieranlagen

\*\*Ziel:\*\*

Ein browserbasiertes Kalkulationstool entwickeln, das die vorhandene Excelbasis ablöst. Das Tool führt den Benutzer schrittweise durch die Anlagenzusammenstellung und liefert am Ende ein Mengengerüst für Materialkosten und personelle Aufwendungen.

\---

\## 1. System­architektur & Module

1\. \*\*Prozessmodule\*\*

&#x20;  \* Beschreiben je Aggregat (z. B. Förderband, Sieb, Ventilator)

&#x20;  \* Können mehrere Antriebe enthalten und deren Parameter (Leistung, Starter) definieren

&#x20;  \* Ermitteln das notwendige Material pro Modul (Schaltschrank- und Baustellenbedarf)

&#x20;  \* Besitzen den Eingabeparameter `operating_load_factor` (Standard 0,8) und liefern daraus den Ausgabeparameter `motor_operating_load`

2\. \*\*Schalt­schrank­module\*\*

&#x20;  \* Sammeln Elemente aller ausgewählten Prozessmodule gruppiert nach Herkunfts-ID

&#x20;  \* Schlagen Hauptschaltergrößen vor und berechnen Kapazitätsreserven

&#x20;  \* Summieren `motor_rated_load` und `motor_operating_load` aller Module

&#x20;  \* Überwachen Schrankgröße (Konzept für spätere Füllgradkontrolle)

3\. \*\*Schalt­raum­module\*\*

&#x20;  \* Fassen mehrere Schaltschränke zusammen

\*Definition der Module:\*

* In JSON-Dateien, je Maschinenbaugruppe eine Datei (z. B. `sieb_typ_a_mod.json`, `foerderband_mod.json`).
* Jede Modul-Definition enthält:

  1. **Parameter-Definitionen (Key–Value-Paare)**:

  ```json
  {
    "parameterName": {
      "datatype": "Integer|Decimal|Bool|Auswahl|Text|...",
      "defaultValue": null,
      "hardLimits": { "min": 0, "max": 100 },          
      "softLimits": {
        "min": 10,
        "max": 80,
        "warningMessage": "Außerhalb üblicher Werte!"
      },
      "options": ["OptionA", "OptionB", ...],
      "source": ["global", "user", "reference"],
      "editableInFrontend": true,
        "reference": "input_voltage"
    }
  }
  ```

  * **datatype**: Datentyp des Parameters.
  * **defaultValue**: Vorgabewert aus Global- oder Referenzdaten.
  * **hardLimits**: Absolute Grenzen, nicht überschreitbar.
  * **softLimits**: Wertebereich, außerhalb wird gewarnt, aber akzeptiert.
  * **options**: Auswahlliste für Auswahlparameter.
  * **source**: Gibt an, woher der Parameter stammen kann.
  * **editableInFrontend**: Steuert, ob der Nutzer den Wert ändern darf.
  * **reference**: Bei `source: ["reference"]` verweist auf globalen oder anderen Modul-Parameter.

2. **Globale Referenzen**:

   * Liste globaler Parameter-Codes (z. B. `EING_TEMP`, `EING_SPS`), die automatisch eingebunden werden.
   * Ggf. mit `editableInFrontend=false`, um Überschreibung zu verhindern.

3. **Benutzereingabe-Parameter**:

   * Parameter, die der Anwender beim Hinzufügen des Moduls ausfüllt.

4. **Ausgabeparameter**:

   * Parameter, die nach Berechnung verfügbar sind und von anderen Modulen referenziert werden.

5. **Berechnungsreihenfolge**:

   * Sequenz von Python-Funktionen in `<gruppe>_logic.py`, z. B.:

     ```python
     def foerderband_schritt1(params):
         # Berechnung A
         return updated_params
     def foerderband_schritt2(params):
         # Berechnung B
         return updated_params
     ```

*Dateinamenskonvention & Organisation:* & Organisation:\*

* Hauptordner `/modules`
* Dateien benannt nach Maschinenbaugruppe in lowercase mit Unterstrich: `<gruppe>_mod.json` (z. B. `foerderband_mod.json`)
* Zu jeder JSON-Definition ein Python-Skript mit gleicher Basis: `<gruppe>_logic.py`, das die Berechnungsfunktionen enthält

### Definition des Globalmoduls

* Das Globalmodul wird analog zu Anlagenmodulen in einer JSON-Datei (`global_mod.json`) definiert.
* Es darf pro Projekt nur ein Globalmodul geben und muss vor anderen Modulen "eingebaut" werden.
* Struktur der `global_mod.json`:

  ```json
  {
    "moduleName": "Global",
    "moduleId": "GLOBAL",
    "logic": "global",
    "parameters": {
      "input_voltage": {
        "datatype": "Auswahl",
        "options": ["400V", "600V"],
        "defaultValue": "400V",
        "editableInFrontend": true
      },
      // ... weitere globale Parameter
    }
  }
  ```
* Globalmodul ist Quelle für `source: ["global"]` und wird in anderen Modulen einmalig referenziert.

### Definition des Schaltschrankmoduls

* Das Schaltschrankmodul (`schaltschrank_mod.json`) sammelt zunächst alle schaltschrankrelevanten Positionen in einem virtuellen Schrank und gruppiert sie nach Herkunfts-ID.
* Es schlägt auf Basis der Summe aller Motornennströme (× 0,75) automatisch eine Hauptschalterbaugröße aus 63A, 125A, 250A, 400A oder 630A vor und berechnet die Kapazitätsreserve in %.
* Zusätzlich summiert es `motor_rated_load` und `motor_operating_load` aller Module und stellt diese Gesamtwerte bereit.
* Ab 400A wird automatisch ein separates Einspeisefeld markiert, das den Hauptschalter enthält.
* Komponenten können anschließend einem realen Gehäuse zugeordnet werden; ein Konzept zur Überwachung der Füllgrade folgt.

Beispiel für einen virtuellen Schaltschrank:

```python
from pathlib import Path
from module_system import ModuleDefinition, ModuleRuntime

sc_def = ModuleDefinition.from_json(Path("modules/schaltschrank_mod.json"))
runtime = ModuleRuntime(
    sc_def,
    {
        "id": "SC1",
        "label": "Virtueller Schrank",
        "virtual_cabinet": True,
        "elements": {
            "H101": [{"type": "contactor", "rated_current": 10}],
            "F102": [{"type": "frequency_inverter", "rated_current": 12}]
        },
        "motor_currents": [10, 12],
        "motor_rated_loads": [5.5, 5.5],
        "motor_operating_loads": [4.4, 4.4],
    },
)
print(runtime.run())
```

### Cross-Modul Referenzen

* **Modul-Metadaten:**

  * Jedes Modul definiert in seiner JSON-Datei zusätzlich:

    ```json
    {
      "moduleName": "Förderband",        // lesbarer Name
      "moduleId": "FB001",               // eindeutige alphanumerische ID (max. 6 Zeichen)
      // ... weitere Definitionen
    }
    ```
* **Referenzierung von Parametern:**

  * Module untereinander: über `<moduleId>.<parameterName>`, z. B.:

    ```json
    "reference": "FB001.motor_rated_power"
    ```
  * Globalmodul: über `global.<parameterName>`, z. B.:

    ```json
    "reference": "global.input_voltage"
    ```
* **Lookup-Tabelle:**

  * Das System lädt alle Modul-Definitionen und das Globalmodul und erzeugt eine zentrale Lookup-Tabelle:

    * Schlüssel: `<moduleId>.<parameterName>` bzw. `global.<parameterName>`
    * Wert: aktueller Parameterwert
* Referenzierte Werte können als Default in Zielmodulen übernommen oder in Berechnungen verarbeitet werden.

*Workflow in der Applikation:*\*\*\*

1\. Globale Parameter befüllen

2\. Prozessmodule einzeln hinzufügen und konfigurieren (a)

3\. Schaltschränke automatisch zusammenführen

4\. Ergebnis: Mengengerüst, Materialliste, Zeitaufwand

a = Module können sich den Parametern aus den Globaldaten bedienen oder diese ggf. überschreiben
Beispiel *repair_switch*: Global gesetzt auf "intern" kann im Modul per Benutzerauswahl trotzdem auf Nein oder extern gestellt werden.
Ebenso verhält es sich bei der *avg_cable_length*: Wird vom Benutzer keine definiert, gilt der Durchschnittswert aus den Globaldaten.
Einige Globalparameter sollten jedoch vor "Modulübersteuerung" geschützt werden, wie z.B. die *input_voltage* und *frequency* – hier ist kein Überschreiben möglich.


**Eingabeparameter**

| Parameter              | Typ     | Beschreibung                          |
| ---------------------- | ------- | ------------------------------------- |
| Nennleistung Motor     | kW      | Leistungsklasse des Motors            |
| Start Typ              | Auswahl | DOL, FU, Softstart                    |
| Reversierbar           | Bool    | Motor reversierbar (ja/nein)          |
| Bremse                 | Bool    | Bremse vorhanden (ja/nein)            |
| 87 Hz Betrieb bei FU   | Bool    | Betrieb mit 87 Hz Kennlinie (ja/nein) |
| Länge Förderaggregat   | Integer | Länge des Förderaggregats in Metern   |
| Anzahl Reißleine       | Integer | Anzahl Seilzugschalter pro Band       |
| Anzahl Not-Halt Taster | Integer | Anzahl Not-Halt Taster im Modul       |

**Ausgabeparameter**

| Parameter                    | Berechnungslogik                                               |
| ---------------------------- | -------------------------------------------------------------- |
| Nennspannung Motor           | Globale Nennspannung (400 V) oder bei FU + 87 Hz Betrieb 230 V |
| Nennstrom Motor              | Überschlägig aus Nennleistung und Nennspannung ermittelt       |
| Leitungsquerschnitt Leistung | Bestimmung aus Kabellänge und Nennstrom                        |

*Module-spezifische Mengengerüste folgen im Anschluss als Mengengerüst Montage und Schaltschrank*

\---

\## 2. Globale Parameter

Aktuell definierte globale Parameter des Systems:

| Parameter          | Typ/Auswahl           | Beschreibung                         |
| ------------------ | --------------------- | ------------------------------------ |
| calculation_name   | Text                  | Name der Kalkulation                  |
| customer           | Text                  | Kunde                                 |
| customer_id        | Text                  | Kunden-ID                             |
| input_voltage      | Auswahl (400V, 600V)  | Anschlussspannung                     |
| frequency          | Decimal (Hz)          | Netzfrequenz                          |
| avg_cable_length   | Decimal (m)           | Durchschnittliche Kabellänge          |
| max_voltage_drop   | Decimal (%)           | Maximaler zulässiger Spannungsabfall  |

---

## 3. Persistenz & Datenhaltung

* **Kalkulationsspeicherung:**

  * Benutzer kann Kalkulationen speichern und später wieder laden.

  * Flexible Speicheroptionen:

    * Dateibasiert (z. B. JSON/XML-Dateien)

    * SQLite-Datenbank

    * MS SQL Server (MSSQL)

* **Artikeldaten:**

  * Primär: Anbindung an MS SQL Server per interne Artikelnummern (zukünftige Integration)

  * Fallback: Lokale SQLite-Tabelle mit Alternativ- bzw. Standardartikeln

---

## 4. Antriebe & Kabel Anforderungen an die Applikation

\* Containerisiert (Docker)

\* Python-basiert (z. B. Flask)

\* Modularer Aufbau (JSON-Definitionen)

\* Browser-Frontend (responsive)

\* Konfigurierbare Faktortabellen (extern, z. B. JSON/DB)

## Abweichungen zwischen Dokumentation und Code

- Es existieren Prozessmodule (Förderband, Splitter) und ein grundlegendes Schaltschrankmodul; Module für Schalträume sowie eine Füllgradüberwachung der Schaltschränke fehlen noch.
- Ein Browser-Frontend und Docker-Containerisierung sind aktuell nicht implementiert, obwohl sie als Ziel genannt werden.
- Die in der Beschreibung erwähnte Wahl der gemeinsamen oder getrennten Aufstellung von Schaltschränken ist derzeit nicht im Code umgesetzt.

## Roadmap

- [x] Moduldefinitionssystem auf Basis von JSON und Python-Logik
- [x] Globalmodul und Beispiel-Module (Förderband, Splitter) mit Berechnungen
- [x] Grundlegendes Schaltschrankmodul
- [ ] Schaltraummodule
- [ ] Persistenz der Kalkulationen (Datei/DB)
- [ ] Artikeldaten-Anbindung (SQLite/MSSQL)
- [ ] Browser-Frontend (z. B. Flask)
- [ ] Containerisierung (Docker)
- [ ] Validierung & Plausibilitätschecks
- [ ] Benutzerrechte & Rollenkonzept
- [ ] Versionierung der Module
- [ ] Reporting & Export (PDF/Excel/CSV)
- [ ] Internationalisierung
- [ ] API & Integrationen
- [ ] Performance & Skalierung
- [ ] UI/UX-Verbesserungen

\---

\## 7. Future Feature Map

Die folgenden Punkte sind für spätere Entwicklungsphasen geplant und werden gemäß Entwicklungsstand eingetaktet:

1\. \*\*Benutzerrechte & Rollenkonzept (low)\*\*

&#x20;  \* Unterscheidung zwischen Admin, Engineer, Viewer

2\. \*\*Versionierung der Module (mid)\*\*

&#x20;  \* Change-Log und Versionsverwaltung für JSON-Module

3\. \*\*Validation & Plausibilitätschecks (high)\*\*

&#x20;  \* Automatische Prüfregeln für Eingabewerte und Warnmeldungen

4\. \*\*Internationalisierung (low)\*\*

&#x20;  \* Mehrsprachige Oberfläche (Deutsch/Englisch)

5\. \*\*Reporting & Export\*\*

&#x20;  \* Export für PDF, Excel, CSV mit konfigurierbaren Vorlagen (mid)

&#x20;  \* Schnittstelle zur vorhandenen Kalkulation Vertrieb (mid)

6\. \*\*API & Integrationen\*\*

&#x20;  \* REST-API für Artikelstammdaten, ERP-/PIM-Systeme

7\. \*\*Performance & Skalierung (low)\*\*

&#x20;  \* Caching, Hintergrundspeicherung, Optimierung für große Anlagen

 8\. \*\*UI/UX-Verbesserungen (mid)\*\*

&#x20;  \* Fortschrittsbalken, Übersichtskarte, Drag-&-Drop für Module

&#x20;    on

\* Containerisiert (Docker)

\* Python-basiert (z. B. Flask)

\* Modularer Aufbau (JSON-Definitionen)

\* Browser-Frontend (responsive)

\* Konfigurierbare Faktortabellen (extern, z. B. JSON/DB)


---
Weitere ideen:

**Teilungseinheiten-System** 

$\gcd(45\,\text{mm}, 54\,\text{mm}) = \mathbf{9\,mm}$.

Damit ist alles schön ganzzahlig:

* Basis-Einheit (BU): **9 mm**
* 1 TE (DIN): **18 mm = 2 BU**
* Motorschutzschalter 45 mm: **5 BU = 2,5 TE**
* Leitungsschutzschalter 54 mm: **6 BU = 3 TE**

# So rechnest du den Platz auf der Hutschiene

1. **Nutzbreite** bestimmen: $W_\text{nutz} = W_\text{Schiene} - \text{Reserven (Endklemmen, Randleerraum, Trenner, Verdrahtung)}$.
2. **In BU umrechnen:** $N_\text{BU} = \left\lfloor \dfrac{W_\text{nutz}}{9} \right\rfloor$.
3. **Verbrauch in BU addieren:**
   $ \text{BU}_\text{gesamt} = 5\cdot n_\text{MSS} + 6\cdot n_\text{LS} + 2\cdot n_{18\text{mm-Module}} + \text{Abstände\_in\_BU}$.
4. **Restplatz:** $ \text{BU}_\text{frei} = N_\text{BU} - \text{BU}_\text{gesamt}$.
   Zurück in mm: $ \text{mm}_\text{frei} = 9 \cdot \text{BU}_\text{frei}$.
   In TE: $ \text{TE}_\text{frei} = \text{BU}_\text{frei}/2$.

# Mini-Tabelle (BU/TE)

| Gerät / Maß            | mm | BU |  TE |
| ---------------------- | -: | -: | --: |
| Standard-Modul         | 18 |  2 | 1.0 |
| Motorschutzschalter    | 45 |  5 | 2.5 |
| Leitungsschutzschalter | 54 |  6 | 3.0 |
| Trenner 9 mm           |  9 |  1 | 0.5 |

# Schneller Python-Helper (optional)

```python
import math

BU_MM = 9  # Basis-Einheit in mm (gcd von 45 und 54)
TE_MM = 18

def rail_capacity_mm_to_bu(rail_mm, reserve_mm=0):
    return (rail_mm - reserve_mm) // BU_MM

def bu_needed(n_mss=0, n_ls=0, n_18mm=0, extra_bu=0):
    return 5*n_mss + 6*n_ls + 2*n_18mm + extra_bu

def leftover(rail_mm, reserve_mm, n_mss, n_ls, n_18mm=0, extra_bu=0):
    cap_bu = rail_capacity_mm_to_bu(rail_mm, reserve_mm)
    need_bu = bu_needed(n_mss, n_ls, n_18mm, extra_bu)
    free_bu = int(cap_bu - need_bu)
    return {
        "free_bu": free_bu,
        "free_mm": free_bu * BU_MM,
        "free_te": free_bu / 2
    }
```


