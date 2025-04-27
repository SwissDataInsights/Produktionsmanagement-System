```markdown
# Produktionsmanagement-System

## Gesamtüberblick
Dieses System automatisiert den Import, die Verwaltung und die Analyse von Produktions- und Lagerdaten. Es umfasst vier Hauptmodule, die zusammenarbeiten, um Daten einzulesen, zu strukturieren, zu aktualisieren und Produktionssimulationen durchzuführen.

- **Automatischer Datenimport**  
  Liest Excel-Dateien für Lagerbestände (z. B. `teilelager.xlsx`) und Produktionspläne (`production_plan.xlsx`) ein und speichert sie in einer SQLite-Datenbank.

- **Dynamische Datenbankerstellung & -aktualisierung**  
  Erstellt bei Bedarf das Verzeichnis für den SQLite-Treiber, legt die Datenbank `produktionsmanagement.db` an und importiert alle Dateien aus dem Ordner `produktion_model` automatisch als eigene Tabellen.

- **Analyse & Dokumentation**  
  Extrahiert mit SQLAlchemy Metadaten (Spalten, Datentypen, NULL-Zulässigkeit, Fremdschlüssel) und exportiert die Struktur in `database_structure.xlsx`.

- **Simulation & Visualisierung**  
  Simuliert den Produktionsprozess basierend auf dem aktuellen Lagerbestand, identifiziert Engpässe und erstellt Berichte sowie Diagramme zu fehlenden Teilen.

---

## Voraussetzungen & Installation

1. **Python 3.8+**  
2. **Abhängigkeiten installieren**  
   ```bash
   pip install -r requirements.txt
   ```
3. **Projektstruktur**  
   ```
   project-root/
   ├── main.py
   ├── database_info.py
   ├── database_update.py
   ├── "teile to order.py"
   ├── production_plan.xlsx
   ├── teilelager.xlsx
   ├── produktion_model/
   │   └── produktion_*.xlsx
   └── sqlite-dll-win-x64-3490100/  (wird bei Bedarf erstellt)
   ```

---

## 1. `main.py`

**Zweck:** Initialisiert die Datenbank, importiert Lager- und Produktionsplandaten und lädt automatisch alle Produktionsspezifikationen.

1. **Verzeichnis & Datenbank**  
   - Prüft und erstellt ggf. den Ordner für den SQLite-Treiber.  
   - Verbindet sich mit `produktionsmanagement.db`.

2. **Import von Excel-Daten**  
   - **`teilelager.xlsx`**: Säubert Artikelnummern, legt Tabelle `teilelager` an.  
   - **`production_plan.xlsx`**: Legt Tabelle `production_plan` an; bricht kontrolliert ab, wenn Datei fehlt.

3. **Import von Produktionsspezifikationen**  
   - Liest alle Dateien `produktion_*.xlsx` aus `produktion_model/` ein und legt für jede eine eigene Tabelle an.

4. **Verifikation**  
   - Zählt Datensätze in jeder Tabelle via SQL-Abfrage und überprüft so den erfolgreichen Import.

---

## 2. `database_info.py`

**Zweck:** Dokumentiert die aktuelle Datenbankstruktur.

1. **Inspektion**  
   - Verbindet sich mit der SQLite-Datenbank.  
   - Ermittelt alle Tabellennamen.

2. **Metadaten & Fremdschlüssel**  
   - Liest für jede Tabelle Spalteninformationen (Name, Typ, NULL, Default).  
   - Extrahiert Fremdschlüsselbeziehungen (referenzierte Tabelle/Spalte).

3. **Strukturbericht**  
   - Erstellt zwei DataFrames (Spalteninfos & FK-Infos).  
   - Exportiert beide in `database_structure.xlsx` in separaten Arbeitsblättern.

---

## 3. `database_update.py`

**Zweck:** Aktualisiert bestehende Daten in der Datenbank.

1. **Daten ersetzen**  
   - Liest `teilelager.xlsx` und `production_plan.xlsx` neu ein.  
   - Verwendet `if_exists='replace'`, um alte Daten zu überschreiben.

2. **Produktionsspezifikationen**  
   - Aktualisiert alle `produktion_*.xlsx` aus `produktion_model/` analog zum Erstimport.

3. **Überprüfung & Abschluss**  
   - Zählt nach dem Update alle Datensätze und gibt die Anzahl aus.  
   - Schließt die DB-Verbindung ordentlich.

---

## 4. `teile to order.py`

**Zweck:** Simulation des Produktionsprozesses und Identifikation von Materialengpässen.

1. **Datenabruf**  
   - Liest `teilelager` und `production_plan` in DataFrames.  
   - Wandelt Lagerbestand in ein Dictionary (Artikelnummer → Menge) um.

2. **Spezifikations-Laden**  
   - Ermittelt alle Tabellen `produktion_*` in der DB.  
   - Speichert jede Spezifikation in einem Dictionary.

3. **Simulationslogik**  
   - `simulate_production_for_unit`: Subtrahiert benötigte Teile vom Lagerbestand, protokolliert Engpässe.  
   - Iteriert über den Produktionsplan (Datum, Modell, Auftrag, Kunde) und simuliert jede Einheit.

4. **Berichte & Visualisierung**  
   - Erstellt `missing_parts.xlsx` mit allen Engpässen.  
   - Zeichnet Balkendiagramme der Fehlmengen pro Modell.  
   - Aggregiert Gesamtbedarf in `zbiorcze_zamowienie.xlsx`.

---

## Erweiterungsmöglichkeiten

- **Web-Dashboard** (z. B. mit Flask/Django) zur Echtzeit-Überwachung.  
- **Interaktive Analysen** mit Plotly/Dash oder ML-Modelle zur Bedarfsvorhersage.  
- **Multi-Datenbank-Support** für MySQL/PostgreSQL.  
- **Erweiterte Datenvalidierung** (CSV/JSON-Import, Quality Checks).  
- **Automatisierte Benachrichtigungen** (E-Mail/SMS bei Engpässen).

---

## Zusammenfassung

| Modul                   | Kernfunktion                                                   |
|-------------------------|----------------------------------------------------------------|
| **main.py**             | DB-Initialisierung & Erstimport von Lager- und Plan-Daten     |
| **database_info.py**    | Dokumentation der Datenbankstruktur                           |
| **database_update.py**  | Systematische Aktualisierung bestehender Daten                |
| **„teile to order.py“** | Produktionssimulation, Engpass-Erkennung & Reporting           |

Dieses modulare System gewährleistet eine effiziente, automatisierte Datenverwaltung und Produktionsplanung – mit zahlreichen Optionen für zukünftige Erweiterungen. 