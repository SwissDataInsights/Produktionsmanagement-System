import pandas as pd
from sqlalchemy import create_engine, inspect

# ----- DATENBANKVERBINDUNG -----
# Verbindungszeichenfolge für SQLite-Datenbank – Datei 'produktionsmanagement.db' im Ordner 'sqlite-dll-win-x64-3490100'
connection_string = 'sqlite:///sqlite-dll-win-x64-3490100/produktionsmanagement.db'
engine = create_engine(connection_string)
inspector = inspect(engine)

# ----- Tabellenliste abrufen -----
table_names = inspector.get_table_names()

# ----- Listen zur Speicherung von Spalten- und Fremdschlüsselinformationen -----
columns_data = []
fk_data = []

for table in table_names:
    # Spalteninformationen für jede Tabelle abrufen
    cols = inspector.get_columns(table)
    for col in cols:
        columns_data.append({
            'Table': table,
            'Column Name': col.get('name'),
            'Data Type': str(col.get('type')),
            'Nullable': col.get('nullable'),
            'Default': col.get('default')
        })

    # Fremdschlüsselinformationen für jede Tabelle abrufen
    fks = inspector.get_foreign_keys(table)
    for fk in fks:
        fk_data.append({
            'Table': table,
            'Constraint Name': fk.get('name', 'keiner'),
            'Constrained Columns': ", ".join(fk.get('constrained_columns', [])),
            'Referred Table': fk.get('referred_table', ''),
            'Referred Columns': ", ".join(fk.get('referred_columns', []))
        })

# ----- Umwandeln der Listen in DataFrames -----
df_columns = pd.DataFrame(columns_data)
df_fks = pd.DataFrame(fk_data)

# ----- Speichern in eine Excel-Datei mit zwei Tabellenblättern -----
output_file = 'database_structure.xlsx'
with pd.ExcelWriter(output_file) as writer:
    df_columns.to_excel(writer, sheet_name='Columns', index=False)
    df_fks.to_excel(writer, sheet_name='ForeignKeys', index=False)

print("Daten der Datenbankstruktur wurden in der Datei gespeichert:", output_file)
