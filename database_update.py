import os
import sqlite3
import pandas as pd

# ----- DATENBANKKONFIGURATION -----
db_dir = 'sqlite-dll-win-x64-3490100'
if not os.path.exists(db_dir):
    os.makedirs(db_dir)
    print(f"Ordner erstellt: {db_dir}")

db_path = os.path.join(db_dir, 'produktionsmanagement.db')

# Herstellung der Datenbankverbindung
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
print("Datenbankverbindung wurde hergestellt.")

# ----- AKTUALISIERUNG DER TABELLE 'teilelager' -----
excel_file_teile = 'teilelager.xlsx'
try:
    df_teile = pd.read_excel(excel_file_teile, dtype={'Artikel-Nr.': str})
    df_teile['Artikel-Nr.'] = df_teile['Artikel-Nr.'].str.strip()
    print(f"Daten aus der Datei '{excel_file_teile}' wurden geladen:")
    print(df_teile.head())
except FileNotFoundError:
    print(f"Fehler: Datei '{excel_file_teile}' wurde nicht gefunden")
    conn.close()
    exit()

df_teile.to_sql(
    'teilelager',
    conn,
    if_exists='replace',
    index=False,
    dtype={
        "Artikel-Nr.": "TEXT",
        # Ergänzen Sie bei Bedarf die Datentypen weiterer Spalten, z. B.:
        # "HESS-LP": "TEXT",
        # "Zeichnungs-Nr. Index": "TEXT",
        # "Artikelname": "TEXT",
        # "Einheit": "TEXT",
        # "Menge": "INTEGER"
    }
)
print("Tabelle 'teilelager' wurde erstellt und die Daten wurden eingefügt.")

# ----- AKTUALISIERUNG DER TABELLE 'production_plan' -----
excel_file_plan = 'production_plan.xlsx'
try:
    df_plan = pd.read_excel(excel_file_plan)
    print(f"Daten aus der Datei '{excel_file_plan}' wurden geladen:")
    print(df_plan.head())
except FileNotFoundError:
    print(f"Fehler: Datei '{excel_file_plan}' wurde nicht gefunden")
    conn.close()
    exit()

df_plan.to_sql(
    'production_plan',
    conn,
    if_exists='replace',
    index=False
    # Typdefinitionen für Spalten können bei Bedarf ergänzt werden.
)
print("Tabelle 'production_plan' wurde erstellt und die Daten wurden eingefügt.")

# ----- AUTOMATISCHES EINLESEN VON PRODUKTIONSDATEIEN AUS DEM VERZEICHNIS 'produktion_model' -----
production_folder = "produktion_model"
if not os.path.exists(production_folder):
    print(f"Verzeichnis '{production_folder}' existiert nicht.")
    conn.close()
    exit()

# Sammle alle Excel-Dateien im Verzeichnis, die mit 'produktion_' beginnen und mit '.xlsx' enden
production_files = [f for f in os.listdir(production_folder)
                    if f.startswith("produktion_") and f.endswith(".xlsx")]

if not production_files:
    print("Im Verzeichnis 'produktion_model' wurden keine Dateien gefunden, die den Kriterien entsprechen.")
else:
    for file in production_files:
        file_path = os.path.join(production_folder, file)
        # Tabellenname entspricht Dateiname ohne Erweiterung, z. B. 'produktion_70058'
        table_name = os.path.splitext(file)[0]
        try:
            df_prod = pd.read_excel(file_path, dtype={'Artikel-Nr.': str})
            df_prod['Artikel-Nr.'] = df_prod['Artikel-Nr.'].str.strip()
            print(f"Daten aus der Datei '{file_path}' wurden geladen:")
            print(df_prod.head())
        except Exception as e:
            print(f"Fehler beim Laden der Datei '{file_path}': {e}")
            continue

        # Einfügen in Tabelle – vorhandene Daten werden ersetzt (if_exists='replace')
        df_prod.to_sql(
            table_name,
            conn,
            if_exists='replace',
            index=False,
            dtype={
                "Artikel-Nr.": "TEXT",
                # Ergänzen Sie bei Bedarf die Datentypen weiterer Spalten, z. B.:
                # "HESS-LP": "TEXT",
                # "Zeichnungs-Nr. Index": "TEXT",
                # "Artikelname": "TEXT",
                # "Einheit": "TEXT",
                # "Rusten": "INTEGER",
                # "Mindestmenge": "INTEGER"
            }
        )
        print(f"Tabelle '{table_name}' wurde erstellt und die Daten wurden eingefügt.")

# ----- ANZEIGE UND ZUSAMMENFASSUNG DER DATENSÄTZE -----
cursor.execute('SELECT COUNT(*) FROM teilelager')
count_teile = cursor.fetchone()[0]
print(f"Tabelle 'teilelager' enthält {count_teile} Datensätze.")

cursor.execute('SELECT COUNT(*) FROM production_plan')
count_plan = cursor.fetchone()[0]
print(f"Tabelle 'production_plan' enthält {count_plan} Datensätze.")

for file in production_files:
    table_name = os.path.splitext(file)[0]
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    count_prod = cursor.fetchone()[0]
    print(f"Tabelle '{table_name}' enthält {count_prod} Datensätze.")

conn.close()
print("Updateprozess abgeschlossen.")
