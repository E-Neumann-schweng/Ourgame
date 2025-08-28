import customtkinter as ctk
from tkinter import messagebox
import json
import os
import subprocess # Importiert das Subprocess-Modul, um ein externes Programm zu starten
from global_config import THEME_COLORS, STAT_COLORS, MAX_SIDES_ON_DIE, FILLABLE_SIDES, STAT_TYPES, get_paths

class KampfseiteFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=THEME_COLORS["background"])
        self.controller = controller

        self.dice_container = []
        self.dice_frames = []
        self.selected_stat = None
        self.stat_buttons = {}

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.selection_frame = ctk.CTkFrame(self, width=200, fg_color=THEME_COLORS["frame_bg"], corner_radius=20, border_color=THEME_COLORS["border"], border_width=2)
        self.selection_frame.grid(row=0, column=0, padx=15, pady=20, sticky="nsw")
        self.selection_frame.grid_propagate(False)
        self.selection_frame.grid_rowconfigure(1, weight=1)

        top_frame = ctk.CTkFrame(self.selection_frame, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="new")

        selection_label = ctk.CTkLabel(top_frame, text="Wert wählen", font=ctk.CTkFont(size=18, weight="bold"), text_color=THEME_COLORS["text_accent"])
        selection_label.pack(pady=15, padx=10, fill="x")

        for stat in STAT_TYPES:
            button = ctk.CTkButton(
                top_frame,
                text=stat,
                font=ctk.CTkFont(size=16),
                fg_color=STAT_COLORS[stat][0],
                hover_color=STAT_COLORS[stat][1],
                text_color=THEME_COLORS["text_light"],
                corner_radius=12,
                command=lambda s=stat: self.select_stat(s)
            )
            button.pack(pady=10, padx=10, fill="x")
            self.stat_buttons[stat] = button

        bottom_frame = ctk.CTkFrame(self.selection_frame, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="sew", pady=10)

        nav_frame = ctk.CTkFrame(self.selection_frame, fg_color="transparent")
        nav_frame.grid(row=3, column=0, sticky="sew", pady=10)

        back_to_char_button = ctk.CTkButton(nav_frame, text="Zurück zur Charakterseite", command=self.go_back_to_character, font=("Cinzel", 12, "bold"), fg_color=THEME_COLORS["button_main"], hover_color=THEME_COLORS["button_hover"], text_color=THEME_COLORS["text_dark"])
        back_to_char_button.pack(pady=5, padx=10, fill="x")

        back_to_talents_button = ctk.CTkButton(nav_frame, text="Zurück zur Talentseite", command=self.go_back_to_talents, font=("Cinzel", 12, "bold"), fg_color=THEME_COLORS["button_main"], hover_color=THEME_COLORS["button_hover"], text_color=THEME_COLORS["text_dark"])
        back_to_talents_button.pack(pady=5, padx=10, fill="x")

        # Geänderter Button, um das externe Skript zu starten
        to_magic_button = ctk.CTkButton(nav_frame, text="Zauber-Baukasten", command=self.go_to_magic, font=("Cinzel", 12, "bold"), fg_color=THEME_COLORS["button_main"], hover_color=THEME_COLORS["button_hover"], text_color=THEME_COLORS["text_dark"])
        to_magic_button.pack(pady=5, padx=10, fill="x")

        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Deine Würfel", fg_color=THEME_COLORS["frame_bg"], corner_radius=20, border_color=THEME_COLORS["border"], border_width=2, label_font=ctk.CTkFont(size=18, weight="bold"), label_text_color=THEME_COLORS["text_accent"])
        self.scrollable_frame.grid(row=0, column=1, pady=20, padx=15, sticky="nsew")

    def load_character_data(self, data):
        """Lädt die Würfeldaten aus den Charakterdaten oder erstellt einen neuen Würfel, wenn keine vorhanden sind."""
        for die_frame in self.dice_frames:
            die_frame.destroy()
        self.dice_container = []
        self.dice_frames = []

        dice_data = data.get("dice_data", [])
        if dice_data:
            self.dice_container = dice_data
            for die_data in self.dice_container:
                self.create_die_widget(die_data)
        else:
            self.add_new_die()

        if self.dice_container:
             for die_data in self.dice_container:
                 self.update_die_display(die_data["id"])

    def save_data(self):
        """Speichert die aktuellen Würfeldaten im Charakter-JSON."""
        self.controller.current_character_data["dice_data"] = self.dice_container
        self.controller.save_character_data()

    def go_back_to_character(self):
        """Speichert die Daten und wechselt zurück zur Charakterseite."""
        self.save_data()
        self.controller.show_frame("CharakterseiteFrame", self.controller.current_character_data)

    def go_back_to_talents(self):
        """Speichert die Daten und wechselt zurück zur Talentseite."""
        self.save_data()
        self.controller.show_frame("TalentseiteFrame", self.controller.current_character_data)
        
    def go_to_magic(self):
        """Startet die externe Zauber-Anwendung."""
        # Holen Sie sich die Pfade aus der globalen Konfiguration
        _, _, _ = get_paths()
        
        # Pfad zum zauber.py Skript
        zauber_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zauber.py")
        
        try:
            # Startet zauber.py in einem neuen Prozess, ohne das Hauptprogramm zu blockieren
            subprocess.Popen(["python", zauber_script_path])
        except FileNotFoundError:
            messagebox.showerror("Fehler", f"Das Skript '{zauber_script_path}' konnte nicht gefunden werden.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Ein Fehler ist beim Starten des Zauber-Baukastens aufgetreten: {e}")

    def select_stat(self, stat):
        """Wählt einen Wert aus und markiert den entsprechenden Button."""
        self.selected_stat = stat
        for s, btn in self.stat_buttons.items():
            btn.configure(border_width=3 if s == stat else 0, border_color=STAT_COLORS["Selected"])

    def add_new_die(self):
        """Erstellt ein neues Würfel-Datenobjekt und das zugehörige Widget."""
        die_data = {"id": len(self.dice_container), "sides": [{"stat": "Leer", "level": 0} for _ in range(MAX_SIDES_ON_DIE)]}
        self.dice_container.append(die_data)
        self.create_die_widget(die_data)
        self.save_data()

    def create_die_widget(self, die_data):
        """Erstellt das visuelle Widget für einen Würfel."""
        die_id = die_data["id"]
        die_frame = ctk.CTkFrame(self.scrollable_frame, border_width=2, border_color=THEME_COLORS["border_dark"], fg_color=THEME_COLORS["card_bg"], corner_radius=15)
        die_frame.pack(pady=10, padx=10, fill="x")
        title_label = ctk.CTkLabel(die_frame, text=f"Würfel {die_id + 1} (d10)", font=ctk.CTkFont(size=16, weight="bold"), text_color=THEME_COLORS["text_accent"])
        title_label.pack(pady=(5, 10))
        sides_frame = ctk.CTkFrame(die_frame, fg_color="transparent")
        sides_frame.pack(pady=5, padx=5, fill="x")
        die_frame.sides_widgets = []
        for i in range(MAX_SIDES_ON_DIE):
            side_button = ctk.CTkButton(sides_frame, text="-", fg_color=STAT_COLORS["Leer"][0], hover_color=STAT_COLORS["Leer"][1], text_color=THEME_COLORS["text_light"], corner_radius=8,
                                        command=lambda d_id=die_id, s_idx=i: self.on_side_click(d_id, s_idx))
            side_button.grid(row=0, column=i, padx=4, pady=5, sticky="ew")
            die_frame.sides_widgets.append(side_button)
        sides_frame.grid_columnconfigure(list(range(MAX_SIDES_ON_DIE)), weight=1)
        self.dice_frames.append(die_frame)
        self.update_die_display(die_id)

    def on_side_click(self, die_id, side_index):
        """Behandelt den Klick auf eine Würfelseite."""
        if self.selected_stat is None:
            messagebox.showwarning("Keine Auswahl", "Bitte wähle zuerst einen Wert (Angriff, Verteidigung, Mana) aus der linken Leiste aus.")
            return
        if self.dice_container[die_id]["sides"][side_index]["stat"] != "Leer":
            messagebox.showinfo("Belegt", "Dieser Slot ist bereits belegt.")
            return
        self.assign_stat(die_id, side_index, self.selected_stat)

    def assign_stat(self, die_id, side_index, stat):
        """Weist einer Würfelseite einen Wert zu und speichert die Daten."""
        die = self.dice_container[die_id]
        die["sides"][side_index] = {"stat": stat, "level": 1}
        filled_sides = sum(1 for side in die["sides"] if side["stat"] != "Leer")
        self.update_die_display(die_id)
        self.save_data()

        if filled_sides == FILLABLE_SIDES:
            self.trigger_end_of_fill_action()

    def update_die_display(self, die_id):
        """Aktualisiert die Anzeige eines Würfel-Widgets."""
        die_data = self.dice_container[die_id]
        die_frame = self.dice_frames[die_id]
        filled_sides = sum(1 for side in die_data["sides"] if side["stat"] != "Leer")
        for i, side_data in enumerate(die_data["sides"]):
            button = die_frame.sides_widgets[i]
            stat, level = side_data["stat"], side_data["level"]
            if stat == "Leer":
                button.configure(text="-", fg_color=STAT_COLORS["Leer"][0], hover_color=STAT_COLORS["Leer"][1], text_color=THEME_COLORS["text_light"])
            else:
                button.configure(text=f"{stat} Lvl {level}", fg_color=STAT_COLORS[stat][0], hover_color=STAT_COLORS[stat][1], text_color=THEME_COLORS["text_light"])
            button.configure(state="normal" if not (filled_sides >= FILLABLE_SIDES and stat == "Leer") else "disabled")

    def can_level_up(self, die_id):
        """Prüft, ob ein Würfel aufgelevelt werden kann."""
        die = self.dice_container[die_id]
        counts = {}
        for side in die["sides"]:
            if side["stat"] != "Leer":
                key = (side["stat"], side["level"])
                counts[key] = counts.get(key, 0) + 1
        return any(count >= 2 for count in counts.values())

    def get_levellable_dice_ids(self):
        """Sammelt die IDs der Würfel, die aufgelevelt werden können."""
        return [die["id"] for die in self.dice_container if self.can_level_up(die["id"])]

    def trigger_end_of_fill_action(self):
        """Löst eine Aktion aus, wenn ein Würfel voll ist."""
        levellable_ids = self.get_levellable_dice_ids()
        if not levellable_ids:
            messagebox.showinfo("Kein Level-Up möglich", "Keiner deiner Würfel hat Seiten zum Kombinieren.\nEin neuer Würfel wird hinzugefügt.")
            self.add_new_die()
        else:
            self.offer_choice_dialog(levellable_ids)

    def offer_choice_dialog(self, levellable_ids):
        """Zeigt ein Dialogfenster für die Wahl zwischen Aufleveln und neuem Würfel."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Aktion wählen")
        dialog.transient(self)
        dialog.grab_set()
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        dialog.configure(fg_color=THEME_COLORS["frame_bg"])

        label = ctk.CTkLabel(dialog, text="Ein Würfel ist voll. Was möchtest du tun?", font=ctk.CTkFont(size=16, weight="bold"), text_color=THEME_COLORS["text_main"])
        label.pack(pady=(15, 10), padx=20)

        def level_up_action(die_id_to_level):
            self.level_up_die(die_id_to_level)
            dialog.destroy()

        def new_die_action():
            self.add_new_die()
            dialog.destroy()

        for die_id in levellable_ids:
            btn = ctk.CTkButton(dialog, text=f"Würfel {die_id + 1} aufleveln",
                                font=ctk.CTkFont(size=14, weight="bold"),
                                fg_color=THEME_COLORS["button_success"],
                                hover_color=THEME_COLORS["button_success_hover"],
                                text_color=THEME_COLORS["text_dark"],
                                command=lambda d_id=die_id: level_up_action(d_id))
            btn.pack(pady=5, padx=20, fill="x")

        separator = ctk.CTkFrame(dialog, height=2, fg_color=THEME_COLORS["border"])
        separator.pack(pady=10, padx=20, fill="x")

        new_die_btn = ctk.CTkButton(dialog, text="Neuen Würfel hinzufügen",
                                    font=ctk.CTkFont(size=14, weight="bold"),
                                    fg_color=THEME_COLORS["button_main"],
                                    hover_color=THEME_COLORS["button_hover"],
                                    text_color=THEME_COLORS["text_dark"],
                                    command=new_die_action)
        new_die_btn.pack(pady=5, padx=20, fill="x")

        dialog.update_idletasks()
        height = label.winfo_reqheight() + (len(levellable_ids) * 40) + 120
        dialog.geometry(f"400x{height}")

    def level_up_die(self, die_id):
        """Führt das Aufleveln eines Würfels durch und speichert die Daten."""
        die = self.dice_container[die_id]
        counts = {}
        for side in die["sides"]:
            if side["stat"] != "Leer":
                key = (side["stat"], side["level"])
                counts[key] = counts.get(key, 0) + 1
        new_sides = []
        for (stat, level), count in counts.items():
            for _ in range(count // 2):
                new_sides.append({"stat": stat, "level": level + 1})
            if count % 2 == 1:
                new_sides.append({"stat": stat, "level": level})
        num_new_sides = len(new_sides)
        for _ in range(MAX_SIDES_ON_DIE - num_new_sides):
            new_sides.append({"stat": "Leer", "level": 0})
        self.dice_container[die_id]["sides"] = new_sides
        self.update_die_display(die_id)
        self.save_data()
