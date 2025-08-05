EKalk – Kalkulationstool für Elektroumfänge an Förder- und Sortieranlagen

**Ziel:**
Ein browserbasiertes Kalkulationstool entwickeln, das die vorhandene Excelbasis ablöst. Das Tool führt den Benutzer schrittweise durch die Anlagenzusammenstellung und liefert am Ende ein Mengengerüst für Materialkosten und personelle Aufwendungen.

---

## 1. System­architektur & Module

1. **Prozessmodule**

   * Beschreiben je Aggregat (z. B. Förderband, Sieb, Ventilator)
   * Können mehrere Antriebe enthalten und deren Parameter (Leistung, Starter) definieren
   * Ermitteln das notwendige Material pro Modul (Schaltschrank- und Baustellenbedarf)
2. **Schalt­schrank­module**

   * Sammeln Elemente aller ausgewählten Prozessmodule
   * Berechnen benötigte Schrankgröße
   * Überwachen Kapazität (inkl. Reserve)
3. **Schalt­raum­module**

   * Fassen mehrere Schaltschränke zusammen

*Definition der Module:*

* In JSON-Dateien (beliebig viele, anpassbar)
* Module können nachgeladen oder neu erstellt werden

*Workflow in der Applikation:*

1. Globale Parameter befüllen
2. Prozessmodule einzeln hinzufügen und konfigurieren
3. Schaltschränke automatisch zusammenführen
4. Ergebnis: Mengengerüst, Materialliste, Zeitaufwand

---

## 2. Globale Parameter

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
| Reparaturschalter                    | Bool                        |
| SPS                                  | S7‑1200, S7‑1500            |
| Touch Panel                          | 7″, 12″, 15″                |
| Funkfernbedienung                    | Bool                        |
| # Anlaufwarnung                      | Integer                     |
| Einzeladerbeschriftung               | Bool                        |
| Klimagerät                           | Bool                        |
| Umgebungstemperatur                  | Auswahl (z. B. 25 °C–35 °C) |
| Durchschnittliche Kabellänge         | Decimal (Meter)             |
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

## 4. Antriebe & Kabel

* **Definition:** Leistungsklasse + Starter­Art (FU, DOL, DOL-reversierend)
* **Erweiterung:** Kabellänge pro Prozessmodul angeben; falls nicht definiert → globaler Durchschnitt

---

## 5. Berechnungs­logik

**Hinweis:** Parameter sind fest vordefiniert und nicht im Frontend editierbar. Änderungen erfolgen nur in der Konfigurationsdatei/DB.

### 5.1 Arbeitszeiten

1. **E‑Konstruktion**

   ```
   1,5 h × Anzahl Antriebe + 4 h + (1 h bei potentialfreien Kontakten)
   ```
2. **Schaltschrankbau**

   ```
   1,5 h × Anzahl Antriebe + 25 h
   +10 h (extra Bedienschrank)
   +5 h (Einzeladerbeschriftung)
   +0,5 h × Anzahl Antriebe
   +1 h (potentialfreie Kontakte)
   ```
3. **Werkmontage Elektro**

   ```
   2,75 h × Anzahl Antriebe + 3 h
   +10 h (extra Bedienschrank)
   +0,6 h × Kabellänge × Anzahl Antriebe (bei Kabel > 10 m)
   +10 h (Container)
   ```
4. **Programmierung**

   ```
   1,5 h × Anzahl Antriebe + 4 h
   +2 h (Profibus/Profinet)
   ```
5. **Probelauf/Prüfung**

   ```
   0,75 h × Anzahl Antriebe + 5 h
   ```
6. **Montagevorbereitung**

   ```
   wenn Σ Antriebe ≤ 6 → 15 h
   wenn Σ Antriebe ≤ 30 → 30 h
   sonst → 50 h
   ```
7. **Inbetriebnahme**

   ```
   2 h × Σ Antriebe + 3 h
   ```
8. **Baustellenmontage**

   ```
   43 h + 4 h × Σ Antriebe
   ```

### 5.2 Material (Mengengerüste)

* Montage-Mengengerüst
* Schaltschrank-Mengengerüst

---

## 6. Anforderungen an die Applikation

* Containerisiert (Docker)
* Python-basiert (z. B. Flask)
* Modularer Aufbau (JSON-Definitionen)
* Browser-Frontend (responsive)
* Konfigurierbare Faktortabellen (extern, z. B. JSON/DB)

---

## 7. Future Feature Map

Die folgenden Punkte sind für spätere Entwicklungsphasen geplant und werden gemäß Entwicklungsstand eingetaktet:

1. **Benutzerrechte & Rollenkonzept (low)**

   * Unterscheidung zwischen Admin, Engineer, Viewer
2. **Versionierung der Module (mid)**

   * Change-Log und Versionsverwaltung für JSON-Module
3. **Validation & Plausibilitätschecks (high)**

   * Automatische Prüfregeln für Eingabewerte und Warnmeldungen
4. **Internationalisierung (low)**

   * Mehrsprachige Oberfläche (Deutsch/Englisch)
5. **Reporting & Export**

   * Export für PDF, Excel, CSV mit konfigurierbaren Vorlagen (mid)
   * Schnittstelle zur vorhandenen Kalkulation Vertrieb (mid)
6. **API & Integrationen**

   * REST-API für Artikelstammdaten, ERP-/PIM-Systeme
7. **Performance & Skalierung (low)**

   * Caching, Hintergrundspeicherung, Optimierung für große Anlagen
8. **UI/UX-Verbesserungen (mid)**

   * Fortschrittsbalken, Übersichtskarte, Drag-&-Drop für Module
     on

* Containerisiert (Docker)
* Python-basiert (z. B. Flask)
* Modularer Aufbau (JSON-Definitionen)
* Browser-Frontend (responsive)
* Konfigurierbare Faktortabellen (extern, z. B. JSON/DB)
