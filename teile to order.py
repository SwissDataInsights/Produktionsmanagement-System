#!/usr/bin/env python
# coding: utf-8

# In[5]:


import sqlite3
import pandas as pd

# ----- KROK 1: Pobranie danych z bazy -----
db_path = 'sqlite-dll-win-x64-3490100/produktionsmanagement.db'
conn = sqlite3.connect(db_path)

# Wczytaj stan magazynowy z tabeli "teilelager"
teilelager_df = pd.read_sql("SELECT * FROM teilelager", conn)
# Zamiana stanu magazynowego na słownik: klucz = Artikel-Nr., wartość = dostępna ilość
inventory = teilelager_df.set_index('Artikel-Nr.')['Menge'].to_dict()

# Wczytaj plan produkcji z tabeli "production_plan"
# Tabela production_plan zawiera kolumny: Model, Nr, Kunde, Termin
production_plan_df = pd.read_sql("SELECT * FROM production_plan", conn)
# Konwersja kolumny Termin – data będzie rozpoznana automatycznie (np. ISO8601)
production_plan_df['Termin'] = pd.to_datetime(production_plan_df['Termin'])
# Sortujemy plan produkcji według terminu
production_plan_df.sort_values('Termin', inplace=True)

# ----- KROK 2: Automatyczne pobranie tabel produkcyjnych z bazy -----
# Pobieramy listę tabel w bazie, które zaczynają się od "produktion_"
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'produktion_%'")
prod_tables = [row[0] for row in cursor.fetchall()]

# Tworzymy słownik model_requirements: klucz = model (np. "70058"), wartość = DataFrame tabeli produkcyjnej
model_requirements = {}
for table in prod_tables:
    # Wyekstrahujemy kod modelu – np. z "produktion_70058" wyciągniemy "70058"
    model_code = table.replace("produktion_", "")
    try:
        df_prod = pd.read_sql(f"SELECT * FROM {table}", conn, dtype={'Artikel-Nr.': str})
        df_prod['Artikel-Nr.'] = df_prod['Artikel-Nr.'].str.strip()
        model_requirements[model_code] = df_prod
        print(f"Spezifikation für Modell {model_code} aus Tabelle {table} wurde geladen.")
    except Exception as e:
        print(f"Fehler beim Laden der Tabelle {table}: {e}")

conn.close()

# ----- KROK 3: Symulacja produkcji -----
def simulate_production_for_unit(current_inventory, requirements_df):
    """
    Symuluje produkcję jednej sztuki.
    Odejmuje ze stanu magazynowego ilość (Rusten) niezbędną dla każdej części.
    Zwraca zaktualizowany stan magazynowy (updated_inventory)
    oraz słownik (missing) z informacją o ewentualnych brakach.
    """
    updated_inventory = current_inventory.copy()
    missing = {}
    for _, row in requirements_df.iterrows():
        artikel = row['Artikel-Nr.']
        required_qty = row['Rusten']  # Używamy kolumny 'Rusten' jako ilość potrzebną dla jednej sztuki
        if artikel not in updated_inventory:
            updated_inventory[artikel] = 0
        updated_inventory[artikel] -= required_qty
        if updated_inventory[artikel] < 0:
            missing[artikel] = abs(updated_inventory[artikel])
    return updated_inventory, missing

# Lista do zbierania raportu – dla każdego dnia, modelu, konkretnej sztuki, gdzie wystąpił niedobór
order_schedule = []

# Iterujemy po wierszach planu produkcji (każdy rekord dotyczy wyprodukowania jednej sztuki)
for idx, order in production_plan_df.iterrows():
    day = order['Termin'].date()
    model = str(order['Model']).strip()
    unit_id = order['Nr']    # numer sztuki
    kunde = order['Kunde']

    if model not in model_requirements:
        print(f"Keine Produktionsspezifikation für Modell {model} (Einheit: {unit_id}) am {day}.")
        continue

    requirements_df = model_requirements[model]
    inventory, missing_parts = simulate_production_for_unit(inventory, requirements_df)

    if missing_parts:
        for artikel, missing_qty in missing_parts.items():
            order_schedule.append({
                "Termin": day,
                "Model": model,
                "Sztuka Nr": unit_id,
                "Kunde": kunde,
                "Artikel-Nr.": artikel,
                "Brak (szt.)": missing_qty
            })
        print(f"Tag {day}: Produktion des Modells {model} (Einheit {unit_id}) – es trat ein Mangel auf: {missing_parts}")
    else:
        print(f"Tag {day}: Produktion des Modells {model} (Einheit {unit_id}) verlief ohne Probleme.")

# ----- KROK 4: Raportowanie i zapis do pliku Excel -----
if order_schedule:
    order_schedule_df = pd.DataFrame(order_schedule)
    print("\nTage, an denen Nachbestellungen für fehlende Teile aufgegeben werden sollten:")
    print(order_schedule_df)
    order_schedule_df.to_excel("missing_parts.xlsx", index=False)
    print("Der Bericht über fehlende Teile wurde in die Datei 'missing_parts.xlsx' gespeichert.")
else:
    print("\nDer Produktionsplan ist mit dem aktuellen Lagerbestand umsetzbar – es gibt keine Teilefehlmengen.")


# In[6]:


import matplotlib.pyplot as plt

# Zakładamy, że order_schedule_df zawiera następujące kolumny:
# "Model", "Sztuka Nr", "Brak (szt.)" oraz "Termin" (jako daty produkcji)
# Najpierw grupujemy dane według Model i Sztuka Nr, obliczając:
# - sumę braków (Brak (szt.))
# - minimalny termin (jako datę produkcji) dla danej pary
grouped = order_schedule_df.groupby(["Model", "Sztuka Nr"]).agg({
    "Brak (szt.)": "sum",
    "Termin": "min"
}).reset_index()

# Sortujemy wynik według kolumny "Termin"
grouped = grouped.sort_values("Termin")

# Tworzymy kolumnę etykiet, która łączy Model oraz Sztuka Nr
grouped["Label"] = grouped["Model"].astype(str) + " - " + grouped["Sztuka Nr"].astype(str)

# Generujemy wykres słupkowy
plt.figure(figsize=(10, 6))
plt.bar(grouped["Label"], grouped["Brak (szt.)"], color='skyblue')
plt.title("Gesamte Anzahl fehlender Teile nach Modell und Seriennummer\n(sortiert nach Produktionsdatum)")
plt.xlabel("Modell - Seriennummer")
plt.ylabel("Gesamte Anzahl fehlender Teile")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()


# In[7]:


# Przykładowo zakładamy, że order_schedule_df zawiera kolumny:
# ["Termin", "Model", "Sztuka Nr", "Kunde", "Artikel-Nr.", "Brak (szt.)"]

# 1. Grupujemy wiersze po kolumnie "Artikel-Nr." i sumujemy wartość "Brak (szt.)".
zbiorcze_zamowienie = order_schedule_df.groupby("Artikel-Nr.")["Brak (szt.)"].sum().reset_index()

# 2. Zmieniamy nazwę kolumny z sumą braków, by była bardziej czytelna
zbiorcze_zamowienie.rename(columns={"Brak (szt.)": "Gesamtzahl der Mängel"}, inplace=True)

# 3. Wyświetlamy zbiorcze zamówienie w konsoli (opcjonalnie)
print(zbiorcze_zamowienie)

# 4. Możemy również zapisać zbiorcze zamówienie do pliku Excel, np.:
zbiorcze_zamowienie.to_excel("zbiorcze_zamowienie.xlsx", index=False)
print("Die Datei 'zbiorcze_zamowienie.xlsx' wurde erstellt.")


# In[ ]:




