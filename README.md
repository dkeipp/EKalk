EKalk – Kalkulationstool für Elektroumfänge an Förder- und Sortieranlagen

\*\*Ziel:\*\*

Ein browserbasiertes Kalkulationstool entwickeln, das die vorhandene Excelbasis ablöst. Das Tool führt den Benutzer schrittweise durch die Anlagenzusammenstellung und liefert am Ende ein Mengengerüst für Materialkosten und personelle Aufwendungen.

\---

\## 1. System­architektur & Module

1\. \*\*Prozessmodule\*\*

&#x20;  \* Beschreiben je Aggregat (z. B. Förderband, Sieb, Ventilator)

&#x20;  \* Können mehrere Antriebe enthalten und deren Parameter (Leistung, Starter) definieren

&#x20;  \* Ermitteln das notwendige Material pro Modul (Schaltschrank- und Baustellenbedarf)

2\. \*\*Schalt­schrank­module\*\*

&#x20;  \* Sammeln Elemente aller ausgewählten Prozessmodule

&#x20;  \* Berechnen benötigte Schrankgröße

&#x20;  \* Überwachen Kapazität (inkl. Reserve)

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
      "globalParameters": {
        "input_voltage": {
          "datatype": "Auswahl",
          "options": ["400V", "600V"],
          "defaultValue": "400V",
          "hardLimits": null,
          "softLimits": null,
          "editableInFrontend": false
        },
      "EING_TEMP": {
        "datatype": "Auswahl",
        "options": ["25°C", "30°C", "35°C"],
        "defaultValue": "25°C",
        "hardLimits": null,
        "softLimits": null,
        "editableInFrontend": false
      }
      // ... weitere globale Parameter
    }
  }
  ```
* Globalmodul ist Quelle für `source: ["global"]` und wird in anderen Modulen einmalig referenziert.

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

| Parameter                            | Typ/Auswahl                 |
| ------------------------------------ | --------------------------- |
| Anlagentyp                           | Sternsieb, Splitter, …      |
| Ziel-Land                            | Deutschland, Nordamerika, … |
| Anschlussspannung & Frequenz         | 400 V/50 Hz, 600 V/60 Hz    |
| # Motoren mit FU & Kabellänge > 50 m | Integer                     |
| # Bänder mit Seilzugschalter         | Integer                     |
| # Not-Aus extern                     | Integer                     |
| Steuerungs‑verknüpfung               | Bool                        |
| Extra Gehäuse für Bedienpult         | Bool                        |
| Fernwartung                          | Bool                        |
| repair_switch                        | intern, extern, nein        |
| SPS                                  | S7‑1200, S7‑1500            |
| Touch Panel                          | 7″, 12″, 15″                |
| Funkfernbedienung                    | Bool                        |
| # Anlaufwarnung                      | Integer                     |
| Einzeladerbeschriftung               | Bool                        |
| Klimagerät                           | Bool                        |
| Umgebungstemperatur                  | Auswahl (z. B. 25 °C–35 °C) |
| avg_cable_length                     | Decimal (Meter)             |
| Montage kalkuliert                   | Bool                        |
| Verbissichere Kabel                  | Bool                        |

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
