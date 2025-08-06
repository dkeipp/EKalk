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

\* In JSON-Dateien (beliebig viele, anpassbar)

\* Module können nachgeladen oder neu erstellt werden

\*Workflow in der Applikation:\*

1\. Globale Parameter befüllen

2\. Prozessmodule einzeln hinzufügen und konfigurieren (a)

3\. Schaltschränke automatisch zusammenführen

4\. Ergebnis: Mengengerüst, Materialliste, Zeitaufwand

a = Module können sich den Parametern aus den Globaldaten bedienen oder diese ggf. überschreiben
Beispiel Reparaturschalter: Global gesetzt auf "intern" kann im Modul per Benutzerauswahl trotzdem auf Nein oder extern gestellt werden.
Ebenso verhält es sich bei der Kabellänge: Wird vom Benutzer keine definiert, gilt der durchschnittswert aus den Globaldaten.
Einige Globalparameter sollten aber vor "Modulübersteuerung" geschützt werden, wie z.B. die Nennspannung und Frequenz, hier ist kein Überschreiben möglich.


**Eingabeparameter**

| Parameter              | Typ     | Beschreibung                        |
| ---------------------- | ------- | ----------------------------------- |
| Nennleistung Motor     | kW      | Leistungsklasse des Motors          |
| Start Typ              | Auswahl | DOL, FU, Softstart                  |
| Reversierbar           | Bool    | Motor reversierbar (ja/nein)        |
| Bremse                 | Bool    | Bremse vorhanden (ja/nein)          |
| 87 Hz Betrieb bei FU   | Bool    | Betrieb mit 87 Hz möglich (ja/nein) |
| Länge Förderaggregat   | Integer | Länge des Förderaggregats in Metern |
| Anzahl Reißleine       | Integer | Anzahl Seilzugschalter pro Band     |
| Anzahl Not-Halt Taster | Integer | Anzahl Not-Halt Taster im Modul     |

**Ausgabeparameter**

| Parameter                    | Berechnungslogik                                               |
| ---------------------------- | -------------------------------------------------------------- |
| Nennspannung Motor           | Globale Nennspannung (400 V) oder bei FU + 87 Hz Betrieb 230 V |
| Nennstrom Motor              | Überschlägig aus Nennleistung und Nennspannung ermittelt       |
| Leitungsquerschnitt Leistung | Bestimmung aus Kabellänge und Nennstrom                        |

*Module-spezifische Mengengerüste folgen im Anschluss als Mengengerüst Montage und Schaltschrank*

\---

\## 6. Anforderungen an die Applikation

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
