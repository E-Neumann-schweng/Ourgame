import customtkinter
import tkinter as tk
from tkinter import ttk
import json
import os
import math

# ======================================================================
# Globale Variablen und Datenstrukturen
# ======================================================================

# AP (Abenteuerpunkte) - Startwert
ap = 1100

# Maximale Werte
MAX_KOPFWERT = 65
MAX_TALENTWERT = 70

# Kosten für das Steigern von Werten
# Die Kosten für einen Kopfwert sind jetzt die Anzahl der Talente * Schrittgröße
AP_KOSTEN_TALENT = 1

# Die erforderliche Anzahl an Kopfwert-Steigerungen für 1 Punkt im Talent
TALENT_PROGRESS_THRESHOLD = 2

# Aktuelle Schrittgröße
step_size = 1

# Kopfwerte mit ihren Startwerten
kopfwerte = {
    "Intelligenz": 0, "Kraft": 0, "Konstitution": 0,
    "Charisma": 0, "Intuition": 0, "Fingerfertigkeit": 0
}

# Talentwerte, initialisiert auf 0
talentwerte = {
    "Pflanzenkunde": 0, "Sammeln": 0, "Überreden": 0, "Menschenkenntnis": 0,
    "Ablenkung": 0, "Selbstbeherrschung": 0, "Wahrnehmung": 0,
    "Gassenwissen": 0, "Orientierung": 0, "Tierkunde": 0, "Wildniskunde": 0,
    "Kriegskunst": 0, "Magiekunde": 0, "Sagen und legenden": 0, "Alchemie": 0,
    "Heilkunde": 0, "Götter und Kulte": 0, "Jagen": 0,
    "Körperbeherrschung": 0, "Kraftakt": 0, "Schwimmen": 0, "Einschüchtern": 0,
    "Fesseln": 0, "Handwerk": 0, "Lebensmittelbearbeitung": 0, "Zechen": 0,
    "Schlösserknacken": 0, "Betören": 0, "Handel": 0, "Geistesblitz": 0,
    "Taschendiebstahl": 0, "Verbergen": 0, "Klettern": 0
}

# Ein neues Dictionary, um den Fortschritt der Talent-Steigerungen zu verfolgen.
# Jedes Talent beginnt bei 0.
talent_increase_progress = {name: 0 for name in talentwerte.keys()}

# Zuordnung von Kopfwerten zu Talentwerten
wert_zu_talente_mapping = {
    "Intelligenz": ["Pflanzenkunde", "Sammeln", "Überreden", "Menschenkenntnis", "Ablenkung",
                    "Selbstbeherrschung", "Wahrnehmung", "Gassenwissen", "Orientierung",
                    "Tierkunde", "Wildniskunde", "Kriegskunst", "Magiekunde",
                    "Sagen und legenden", "Alchemie", "Heilkunde", "Götter und Kulte"],
    "Kraft": ["Jagen", "Körperbeherrschung", "Kraftakt", "Schwimmen",
              "Einschüchtern", "Fesseln", "Kriegskunst", "Handwerk", "Lebensmittelbearbeitung"],
    "Konstitution": ["Sammeln", "Ablenkung", "Klettern", "Körperbeherrschung", "Kraftakt",
                     "Schwimmen", "Zechen", "Götter und Kulte", "Handwerk",
                     "Lebensmittelbearbeitung", "Schlösserknacken"],
    "Charisma": ["Betören", "Überreden", "Ablenkung", "Einschüchtern", "Handel"],
    "Intuition": ["Geistesblitz", "Klettern", "Selbstbeherrschung", "Wahrnehmung",
                  "Taschendiebstahl", "Verbergen", "Gassenwissen", "Orientierung",
                  "Magiekunde", "Sagen und legenden", "Alchemie", "Heilkunde",
                  "Lebensmittelbearbeitung", "Schlösserknacken"],
    "Fingerfertigkeit": ["Betören", "Körperbeherrschung", "Taschendiebstahl", "Verbergen",
                         "Fesseln", "Heilkunde", "Handwerk", "Lebensmittelbearbeitung",
                         "Schlösserknacken"]
}

# Logische Gruppierung von Talenten
talent_gruppen = {
    "Körperliche Talente": ["Jagen", "Körperbeherrschung", "Kraftakt", "Schwimmen", "Fesseln", "Klettern", "Verbergen", "Taschendiebstahl", "Schlösserknacken"],
    "Gesellschaftstalente": ["Überreden", "Menschenkenntnis", "Ablenkung", "Einschüchtern", "Betören", "Handel"],
    "Wissens-/Handwerkstalente": ["Pflanzenkunde", "Sammeln", "Tierkunde", "Wildniskunde", "Kriegskunst", "Handwerk", "Lebensmittelbearbeitung", "Alchemie"],
    "Geistige Talente": ["Selbstbeherrschung", "Wahrnehmung", "Gassenwissen", "Orientierung", "Magiekunde", "Sagen und legenden", "Heilkunde", "Götter und Kulte", "Geistesblitz", "Zechen"]
}

# Dictionaries zum Speichern der UI-Elemente
ap_label = None
kopfwerte_elements = {}
talentwerte_elements = {}
step_buttons = {}

def save_to_json():
    """
    Saves the current character data (AP, Kopfwerte, Talentwerte) to a JSON file.
    """
    global ap, kopfwerte, talentwerte

    character_data = {
        "available_ap": ap,
        "kopfwerte": kopfwerte,
        "talentwerte": talentwerte
    }

    filename = "character_data.json"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(character_data, f, indent=4)
        print(f"Charakterdaten erfolgreich in '{filename}' gespeichert.")
    except IOError as e:
        print(f"Fehler beim Speichern der Datei: {e}")

def set_step_size(new_size):
    """
    Aktualisiert die Schrittgröße und markiert den entsprechenden Button.
    """
    global step_size
    step_size = new_size
    
    # Update button states
    for size, btn in step_buttons.items():
        if size == step_size:
            btn.configure(fg_color="#454648")
        else:
            btn.configure(fg_color="#343638")
    
    print(f"Schrittgröße auf {step_size} geändert.")
    update_ui()

def update_ui():
    """Aktualisiert alle Labels und Button-Zustände der Benutzeroberfläche."""
    global ap
    
    # AP-Label aktualisieren
    if ap_label:
        ap_label.configure(text=f"Verfügbare AP: {ap}")

    # Kopfwerte aktualisieren
    for name, value in kopfwerte.items():
        label = kopfwerte_elements[name]["label"]
        plus_btn = kopfwerte_elements[name]["plus_btn"]
        minus_btn = kopfwerte_elements[name]["minus_btn"]

        label.configure(text=f"{value}")
        
        # Berechne die Kosten dynamisch
        num_talents = len(wert_zu_talente_mapping.get(name, []))
        ap_cost = num_talents * step_size
        
        # Plus-Button Zustand aktualisieren
        if ap >= ap_cost and value + step_size <= MAX_KOPFWERT:
            plus_btn.configure(state="normal")
        else:
            plus_btn.configure(state="disabled")

        # Minus-Button Zustand aktualisieren
        if value >= step_size:
            minus_btn.configure(state="normal")
        else:
            minus_btn.configure(state="disabled")

    # Talentwerte aktualisieren
    for name, value in talentwerte.items():
        label = talentwerte_elements[name]["label"]
        plus_btn = talentwerte_elements[name]["plus_btn"]
        minus_btn = talentwerte_elements[name]["minus_btn"]
        
        label.configure(text=f"{value}")
        
        # Plus-Button Zustand aktualisieren
        if ap >= AP_KOSTEN_TALENT * step_size and value + step_size <= MAX_TALENTWERT:
            plus_btn.configure(state="normal")
        else:
            plus_btn.configure(state="disabled")

        # Minus-Button Zustand aktualisieren
        if value >= step_size:
            minus_btn.configure(state="normal")
        else:
            minus_btn.configure(state="disabled")

def increase_wert(wert_name):
    """
    Erhöht den Wert eines Kopfwertes und der entsprechenden Talente
    um die aktuelle Schrittgröße. Die proportionalen Talentsteigerungen
    werden korrekt berechnet, auch bei großen Schritten.
    """
    global ap
    points_to_add = step_size
    
    num_talents = len(wert_zu_talente_mapping.get(wert_name, []))
    ap_cost = num_talents * step_size
    
    # Check if we can increase the Kopfwert
    if ap < ap_cost or kopfwerte[wert_name] + points_to_add > MAX_KOPFWERT:
        print("Nicht genug AP oder maximaler Kopfwert erreicht.")
        return

    # Wenn die Checks bestanden sind, die Erhöhung anwenden
    ap -= ap_cost
    kopfwerte[wert_name] += points_to_add
    
    # Überarbeitete Logik für die proportionale Steigerung
    if wert_name in wert_zu_talente_mapping:
        for talent in wert_zu_talente_mapping[wert_name]:
            if talent in talent_increase_progress:
                # Füge die Steigerung zum Fortschritt hinzu
                talent_increase_progress[talent] += points_to_add
                
                # Berechne, wie viele volle Talentpunkte gewonnen wurden
                points_gained = math.floor(talent_increase_progress[talent] / TALENT_PROGRESS_THRESHOLD)
                
                if points_gained > 0:
                    # Erhöhe den Talentwert, aber nicht über das Maximum hinaus
                    increase_amount = min(points_gained, MAX_TALENTWERT - talentwerte[talent])
                    if increase_amount > 0:
                        talentwerte[talent] += increase_amount
                        # Setze den Fortschritt entsprechend zurück
                        talent_increase_progress[talent] -= increase_amount * TALENT_PROGRESS_THRESHOLD
                    
                    if talentwerte[talent] == MAX_TALENTWERT:
                        print(f"Talent '{talent}' hat den Maximalwert erreicht.")
                        talent_increase_progress[talent] = 0 # Fortschritt zurücksetzen, wenn Maximum erreicht

    update_ui()


def decrease_wert(wert_name):
    """
    Verringert den Wert eines Kopfwertes und der entsprechenden Talente
    um die aktuelle Schrittgröße.
    """
    global ap
    points_to_remove = step_size
    
    if kopfwerte[wert_name] >= points_to_remove:
        num_talents = len(wert_zu_talente_mapping.get(wert_name, []))
        ap_cost = num_talents * points_to_remove

        ap += ap_cost
        kopfwerte[wert_name] -= points_to_remove
        
        # Hier ist die neue Logik für die Verringerung
        if wert_name in wert_zu_talente_mapping:
            for talent in wert_zu_talente_mapping[wert_name]:
                if talent in talent_increase_progress:
                    # Verringere den Fortschritt
                    talent_increase_progress[talent] -= points_to_remove
                    
                    # Wenn der Fortschritt unter den Schwellenwert fällt, muss die letzte Talentsteigerung rückgängig gemacht werden
                    if talent_increase_progress[talent] < 0 and talentwerte[talent] > 0:
                        talentwerte[talent] -= 1
                        talent_increase_progress[talent] += TALENT_PROGRESS_THRESHOLD

        update_ui()
    else:
        print("Wert kann nicht unter 0 fallen.")
        
def increase_talent(talent_name):
    """Erhöht den Wert eines Talents und zieht AP ab."""
    global ap
    points_to_add = step_size
    ap_cost = AP_KOSTEN_TALENT * step_size

    if ap >= ap_cost and talentwerte[talent_name] + points_to_add <= MAX_TALENTWERT:
        ap -= ap_cost
        talentwerte[talent_name] += points_to_add
        update_ui()
    else:
        print("Nicht genug AP oder maximaler Talentwert erreicht.")
        
def decrease_talent(talent_name):
    """Verringert den Wert eines Talents und fügt AP hinzu."""
    global ap
    points_to_remove = step_size

    if talentwerte[talent_name] >= points_to_remove:
        ap += AP_KOSTEN_TALENT * points_to_remove
        talentwerte[talent_name] -= points_to_remove
        update_ui()
    else:
        print("Wert kann nicht unter 0 fallen.")

# ======================================================================
# Benutzeroberfläche erstellen
# ======================================================================

app = customtkinter.CTk()
app.title("Charakter-Wertevergabe")
app.geometry("1200x800")
app.grid_rowconfigure(2, weight=1)
app.grid_columnconfigure(0, weight=1)

# Frame für AP und Schrittgröße (oben)
top_frame = customtkinter.CTkFrame(master=app, fg_color="#2b2b2b")
top_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
top_frame.grid_columnconfigure((0, 1, 2), weight=1)

ap_label = customtkinter.CTkLabel(master=top_frame, text=f"Verfügbare AP: {ap}", font=("Roboto", 24, "bold"), text_color="green")
ap_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

step_frame = customtkinter.CTkFrame(master=top_frame, fg_color="transparent")
step_frame.grid(row=0, column=1, padx=20, pady=10, sticky="e")

step_label = customtkinter.CTkLabel(master=step_frame, text="Schritt:", font=("Roboto", 16))
step_label.pack(side="left", padx=(0, 10))

btn_step_1 = customtkinter.CTkButton(master=step_frame, text="1", width=50, command=lambda: set_step_size(1))
btn_step_1.pack(side="left", padx=5)
step_buttons[1] = btn_step_1

btn_step_10 = customtkinter.CTkButton(master=step_frame, text="10", width=50, command=lambda: set_step_size(10))
btn_step_10.pack(side="left", padx=5)
step_buttons[10] = btn_step_10

save_button = customtkinter.CTkButton(master=top_frame, text="Speichern (JSON)", command=save_to_json, font=("Roboto", 16, "bold"))
save_button.grid(row=0, column=2, padx=(20, 0), pady=10, sticky="e")

# Frame für Kopfwerte (Mitte)
kopfwerte_frame = customtkinter.CTkFrame(master=app, fg_color="#2b2b2b")
kopfwerte_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

# Konfiguriere alle Spalten als gleichwertig für die Verteilung
for i in range(len(kopfwerte)):
    kopfwerte_frame.grid_columnconfigure(i, weight=1)

kopfwerte_title = customtkinter.CTkLabel(master=kopfwerte_frame, text="Kopfwerte", font=("Roboto", 24, "bold"))
kopfwerte_title.grid(row=0, column=0, columnspan=len(kopfwerte), pady=(10, 20))

# Erstellt UI-Elemente für jeden Kopfwert in einer Reihe
for col, name in enumerate(kopfwerte.keys()):
    wert_frame = customtkinter.CTkFrame(master=kopfwerte_frame, fg_color="transparent")
    wert_frame.grid(row=1, column=col, padx=5, pady=5, sticky="ew")

    label_name = customtkinter.CTkLabel(master=wert_frame, text=name, font=("Roboto", 14, "bold"))
    label_name.pack(pady=(0, 5))

    button_container = customtkinter.CTkFrame(master=wert_frame, fg_color="transparent")
    button_container.pack()

    minus_button = customtkinter.CTkButton(master=button_container, text="-", width=25, height=25, command=lambda n=name: decrease_wert(n))
    minus_button.pack(side="left", padx=(0, 3))

    label_value = customtkinter.CTkLabel(master=button_container, text=f"{kopfwerte[name]}", font=("Roboto", 14), width=25)
    label_value.pack(side="left")

    plus_button = customtkinter.CTkButton(master=button_container, text="+", width=25, height=25, command=lambda n=name: increase_wert(n))
    plus_button.pack(side="left", padx=(3, 0))

    kopfwerte_elements[name] = {"label": label_value, "plus_btn": plus_button, "minus_btn": minus_button}

# Haupt-Frame für Talentwerte (unten, mit Scrollfunktion)
talente_main_frame = customtkinter.CTkScrollableFrame(master=app, label_text="Talente", fg_color="#2b2b2b", label_font=("Roboto", 20, "bold"))
talente_main_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
talente_main_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

col_index = 0
for group_name, talents in talent_gruppen.items():
    group_frame = customtkinter.CTkFrame(master=talente_main_frame, fg_color="#343638", corner_radius=10, border_width=2, border_color="#555555")
    group_frame.grid(row=0, column=col_index, padx=10, pady=10, sticky="n")

    group_label = customtkinter.CTkLabel(master=group_frame, text=group_name, font=("Roboto", 18, "bold"))
    group_label.pack(pady=(10, 5))

    for name in talents:
        if name not in talentwerte:
            continue

        talent_row_frame = customtkinter.CTkFrame(master=group_frame, fg_color="transparent")
        talent_row_frame.pack(fill="x", padx=10, pady=2)
        talent_row_frame.grid_columnconfigure(0, weight=1)

        label_name = customtkinter.CTkLabel(master=talent_row_frame, text=name, font=("Roboto", 14), anchor="w")
        label_name.grid(row=0, column=0, sticky="ew")

        button_frame = customtkinter.CTkFrame(master=talent_row_frame, fg_color="transparent")
        button_frame.grid(row=0, column=1, sticky="e")

        minus_button = customtkinter.CTkButton(master=button_frame, text="-", width=30, height=30, command=lambda n=name: decrease_talent(n))
        minus_button.pack(side="left", padx=2)

        label_value = customtkinter.CTkLabel(master=button_frame, text=f"{talentwerte[name]}", font=("Roboto", 14), width=25)
        label_value.pack(side="left", padx=2)

        plus_button = customtkinter.CTkButton(master=button_frame, text="+", width=30, height=30, command=lambda n=name: increase_talent(n))
        plus_button.pack(side="left", padx=2)

        talentwerte_elements[name] = {"label": label_value, "plus_btn": plus_button, "minus_btn": minus_button}

    col_index += 1

# Startet die Benutzeroberfläche und initialisiert die Schrittgröße
update_ui()
set_step_size(1)
app.mainloop()
