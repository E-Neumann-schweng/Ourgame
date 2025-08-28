import customtkinter as ctk
import os
import json
from tkinter import messagebox
from global_config import get_paths

class CharakterauswahlFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#2c1e1e")
        self.controller = controller
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Wähle deinen bestehenden Charakter", font=("Cinzel", 24, "bold"), text_color="#f0e6d2").grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="#3e2b2b", label_text="Verfügbare Charaktere", label_font=("Cinzel", 20, "bold"))
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

    def load_character_list(self):
        """Lädt die Liste der JSON-Dateien aus dem Charakter-Ordner."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        _, character_dir, _ = get_paths()
        if not os.path.exists(character_dir):
            os.makedirs(character_dir)
            
        character_files = sorted([f for f in os.listdir(character_dir) if f.endswith(".json")])
        
        if not character_files:
            ctk.CTkLabel(self.scrollable_frame, text="Keine Charaktere gefunden.", font=("Roboto", 14), text_color="#d4c59a").pack(pady=20)
        else:
            for file_name in character_files:
                char_name = os.path.splitext(file_name)[0]
                char_button = ctk.CTkButton(self.scrollable_frame, text=char_name.capitalize(), font=("Roboto", 16, "bold"),
                                            command=lambda name=char_name: self.load_character(name),
                                            fg_color="#a67c52", hover_color="#c49a6c", text_color="black")
                char_button.pack(fill="x", padx=10, pady=5)
                
    def load_character(self, name):
        """Lädt die Daten des ausgewählten Charakters und wechselt die Seite."""
        _, character_dir, _ = get_paths()
        file_path = os.path.join(character_dir, f"{name}.json")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                character_data = json.load(f)
            self.controller.show_frame("CharakterseiteFrame", character_data)
        except FileNotFoundError:
            messagebox.showerror("Fehler", f"Charakterdatei '{name}.json' nicht gefunden.")
        except json.JSONDecodeError:
            messagebox.showerror("Fehler", f"Fehler beim Laden von '{name}.json'. Datei ist beschädigt.")
