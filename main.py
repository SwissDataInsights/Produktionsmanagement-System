import os
import sqlite3
import pandas as pd

# ----- DATENBANKKONFIGURATION -----
db_dir = 'sqlite-dll-win-x64-3490100'
if not os.path.exists(db_dir):
    os.makedirs(db_dir)
    print(f"Ordner erstellt: {db_dir}")

db_path = os.path.join(db_dir, 'produktionsmanagement.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
print("Datenbankverbindung wurde hergestellt.")

# ----- Tabelle 'teilelager' -----
excel_file_teile = 'teilelager.xlsx'
table_name_teile = 'teilelager'

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
    table_name_teile,
    conn,
    if_exists='replace',
    index=False,
    dtype={
        "Artikel-Nr.": "TEXT",
        # Bei Bedarf ergänzen Sie die Datentypen der übrigen Spalten, z.B.
        # "HESS-LP": "TEXT",
        # "Zeichnungs-Nr. Index": "TEXT",
        # "Artikelname": "TEXT",
        # "Einheit": "TEXT",
        # "Menge": "INTEGER"
    }
)
print(f"Tabelle '{table_name_teile}' wurde erstellt und die Daten wurden eingefügt.")

# ----- Tabelle 'production_plan' -----
excel_file_plan = 'production_plan.xlsx'
table_name_plan = 'production_plan'
try:
    df_plan = pd.read_excel(excel_file_plan)
    print(f"Daten aus der Datei '{excel_file_plan}' wurden geladen:")
    print(df_plan.head())
except FileNotFoundError:
    print(f"Fehler: Datei '{excel_file_plan}' wurde nicht gefunden")
    conn.close()
    exit()

df_plan.to_sql(
    table_name_plan,
    conn,
    if_exists='replace',
    index=False
    # Typdefinitionen für Spalten können bei Bedarf präzisiert werden.
)
print(f"Tabelle '{table_name_plan}' wurde erstellt und die Daten wurden eingefügt.")

# ----- Automatisches Einlesen von Produktionsdateien -----
# Es wird angenommen, dass alle Produktionsspezifikationen im Verzeichnis "produktion_model" liegen.
production_folder = "produktion_model"
if not os.path.exists(production_folder):
    print(f"Verzeichnis '{production_folder}' existiert nicht.")
    conn.close()
    exit()

# Wir sammeln alle Excel-Dateien im Verzeichnis, die mit "produktion_" beginnen und die Endung .xlsx haben
production_files = [f for f in os.listdir(production_folder) if f.startswith("produktion_") and f.endswith(".xlsx")]

if not production_files:
    print("Im Verzeichnis 'produktion_model' wurden keine Dateien gefunden, die den Kriterien entsprechen.")
else:
    for file in production_files:
        file_path = os.path.join(production_folder, file)
        table_name = os.path.splitext(file)[0]  # z.B. 'produktion_70058'
        try:
            df_prod = pd.read_excel(file_path, dtype={'Artikel-Nr.': str})
            df_prod['Artikel-Nr.'] = df_prod['Artikel-Nr.'].str.strip()
            print(f"Daten aus der Datei '{file_path}' wurden geladen:")
            print(df_prod.head())
        except Exception as e:
            print(f"Fehler beim Laden der Datei '{file_path}': {e}")
            continue

        # Schreiben in die Tabelle – vorhandene Daten werden ersetzt (if_exists='replace')
        df_prod.to_sql(
            table_name,
            conn,
            if_exists='replace',
            index=False,
            dtype={
                "Artikel-Nr.": "TEXT",
                # Ergänzen Sie bei Bedarf die Typen weiterer Spalten, z.B.
                # "HESS-LP": "TEXT",
                # "Zeichnungs-Nr. Index": "TEXT",
                # "Artikelname": "TEXT",
                # "Einheit": "TEXT",
                # "Rusten": "INTEGER",
                # "Mindestmenge": "INTEGER"
            }
        )
        print(f"Tabelle '{table_name}' wurde erstellt und die Daten wurden eingefügt.")

# ----- Optional: Anzeige der Datensatzanzahl in den Tabellen -----
cursor.execute(f"SELECT COUNT(*) FROM {table_name_teile}")
count_teile = cursor.fetchone()[0]
print(f"Tabelle '{table_name_teile}' enthält {count_teile} Datensätze.")

cursor.execute(f"SELECT COUNT(*) FROM {table_name_plan}")
count_plan = cursor.fetchone()[0]
print(f"Tabelle '{table_name_plan}' enthält {count_plan} Datensätze.")

for file in production_files:
    table_name = os.path.splitext(file)[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count_prod = cursor.fetchone()[0]
    print(f"Tabelle '{table_name}' enthält {count_prod} Datensätze.")

# ----- Schließen der Datenbankverbindung -----
conn.close()
print("Prozess abgeschlossen.")
