import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import requests
import time
import threading
import os
from typing import Dict, List, Set, Optional, Any
from global_config import THEME_COLORS, get_paths
import re

class MagicWorkshop:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🧙‍♂️ Erweiterter Magie-Baukasten")
        self.root.geometry("1400x900")
        
        # Data storage
        self.predefined_data = {}
        self.discovered_data = {
            "entdeckte_elemente": [],
            "entdeckte_zauber": {}
        }
        
        self.load_all_data()

        self.discovered_secondary_elements: Set[str] = set(self.discovered_data.get("entdeckte_elemente", []))
        self.discovered_spells: Dict[str, Dict] = self.discovered_data.get("entdeckte_zauber", {})
        self.experiment_components: List[Dict] = []
        self.current_spell: Optional[Dict] = None
        self.api_key: str = ""
        
        # Drag and Drop state
        self.dragged_item_data = None
        self.drag_window = None
        
        # Data from loaded JSON
        self.base_elements = self.predefined_data.get("basis_elemente", [])
        self.predefined_combinations = self.predefined_data.get("element_kombinationen", {})
        self.element_emojis = self.predefined_data.get("element_emojis", {})
        self.predefined_spells = self.predefined_data.get("vordefinierte_zauber", {})
        self.effect_types = self.predefined_data.get("wirkungsarten", [])
        self.ability_types = self.predefined_data.get("faehigkeitsarten", [])
        
        # Add predefined elements from combinations to discovered list at startup
        for combo in self.predefined_combinations.values():
            if combo["name"] not in self.discovered_secondary_elements:
                self.discovered_secondary_elements.add(combo["name"])
        
        self.setup_ui()
        self.update_displays()

    # --- Data Management Functions ---
    def load_all_data(self):
        _, character_dir, _ = get_paths()
        self.data_dir = os.path.join(character_dir, "..", "Daten")
        self.predefined_file = os.path.join(self.data_dir, "vordefinierte_magie.json")
        self.discovered_file = os.path.join(self.data_dir, "entdeckte_magie.json")

        self.create_data_directory()
        self.load_predefined_data()
        self.load_discovered_data()

    def create_data_directory(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
    def load_predefined_data(self):
        try:
            if not os.path.exists(self.predefined_file):
                print(f"Datei '{self.predefined_file}' nicht gefunden. Erstelle eine neue Standarddatei.")
                self.create_initial_predefined_file()
            
            with open(self.predefined_file, 'r', encoding='utf-8') as f:
                self.predefined_data = json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden von '{self.predefined_file}': {e}")
            self.predefined_data = {}

    def load_discovered_data(self):
        try:
            if not os.path.exists(self.discovered_file):
                self.save_discovered_data()
            
            with open(self.discovered_file, 'r', encoding='utf-8') as f:
                self.discovered_data = json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden von '{self.discovered_file}': {e}")
            self.discovered_data = {
                "entdeckte_elemente": [],
                "entdeckte_zauber": {}
            }
            self.save_discovered_data()

    def save_discovered_data(self):
        try:
            with open(self.discovered_file, 'w', encoding='utf-8') as f:
                json.dump(self.discovered_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern von '{self.discovered_file}': {e}")

    def create_initial_predefined_file(self):
        initial_data = {
            "basis_elemente": [
                "Wasser", "Feuer", "Erde", "Luft", "Äther", "Leere"
            ],
            "element_emojis": {
                'Wasser': '💧', 'Feuer': '🔥', 'Erde': '🏞️', 'Luft': '🌬️', 
                'Äther': '☀️', 'Leere': '🌑', 'Blut': '🩸', 'Schlamm': '🪨',
                'Tsunami': '🌊', 'Magma': '🌋', 'Dampf': '💨', 'Sand': '🏜️',
                'Heilung': '✨', 'Eis': '❄️', 'Vision': '👁️', 'Dämonie': '👿',
                'Pflanzen': '🌿', 'Stille': '🤫', 'Geist': '👻', 'Krankheit': '🤢',
                'Beschwörung': '🔮', 'Blitz': '⚡', 'Untot': '🧟', 'custom_input': '✍️'
            },
            "element_kombinationen": {
                "Feuer+Wasser": {"name": "Blut", "emoji": "🩸"}, "Erde+Wasser": {"name": "Schlamm", "emoji": "🪨"},
                "Luft+Wasser": {"name": "Tsunami", "emoji": "🌊"}, "Äther+Wasser": {"name": "Heilung", "emoji": "✨"},
                "Leere+Wasser": {"name": "Eis", "emoji": "❄️"}, "Erde+Feuer": {"name": "Magma", "emoji": "🌋"},
                "Feuer+Luft": {"name": "Dampf", "emoji": "💨"}, "Äther+Feuer": {"name": "Vision", "emoji": "👁️"},
                "Feuer+Leere": {"name": "Dämonie", "emoji": "👿"}, "Erde+Luft": {"name": "Sand", "emoji": "🏜️"},
                "Äther+Erde": {"name": "Pflanzen", "emoji": "🌿"}, "Erde+Leere": {"name": "Stille", "emoji": "🤫"},
                "Äther+Luft": {"name": "Geist", "emoji": "👻"}, "Leere+Luft": {"name": "Krankheit", "emoji": "🤢"},
                "Äther+Leere": {"name": "Beschwörung", "emoji": "🔮"}, "Eis+Feuer": {"name": "Blitz", "emoji": "⚡"},
                "Krankheit+Pflanzen": {"name": "Untot", "emoji": "🧟"}
            },
            "vordefinierte_zauber": {
                 "Heilende Berührung": {
                    "name": "Heilende Berührung", "type": "spell", "level": 1, "mana_kosten": 1,
                    "bausteine": ["Heilung"], "kurzbeschreibung": "Heilt Wunden bei Berührung.",
                    "beschreibung": "Ein sanfter Glanz umhüllt die Hand des Zaubernden, wenn er Verwundungen heilt.",
                    "effekt": "Bei Berührung eines Ziels werden 1W4 Trefferpunkte geheilt. Kann in einer Runde nur einmal pro Ziel angewendet werden.",
                    "schaden": "0", "rettungswurf_gegner": "Kein", "reaktiver_effekt": "Keiner"
                }
            },
            "wirkungsarten": [
                ["Projektil", "🏹"], ["Aura/Fläche", "🌟"], ["Verstärkung", "💪"],
                ["Erschaffung", "🗿"], ["Transformation", "🔄"], ["Kontrolle", "🎮"]
            ],
            "faehigkeitsarten": [
                ["Kampf-Manöver", "⚔️"], ["Defensiv-Haltung", "🛡️"], 
                ["Unterstützung", "🤝"], ["Taktik", "♟️"]
            ],
            "freischalt_codes": {
                "PFLANZE123": {"name": "Pflanzen", "type": "element"},
                "SCHATTEN888": {"name": "Schattenkugel", "type": "spell", "data": {
                        "name": "Schattenkugel", "type": "spell", "level": 2, "mana_kosten": 3,
                        "bausteine": ["Leere", "Projektil"], "kurzbeschreibung": "Eine Kugel aus purer Dunkelheit.",
                        "beschreibung": "Eine Kugel aus purer Dunkelheit, die auf ein Ziel zugeschleudert wird.",
                        "effekt": "Ein erfolgreicher Angriffswurf verursacht 2W6+3 Schaden.",
                        "schaden": "2W6+3", "rettungswurf_gegner": "Konstitution", "reaktiver_effekt": "Keiner"
                    }
                },
                "ENTLADUNG42": {"name": "Blitz", "type": "element"}
            }
        }
        with open(self.predefined_file, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=4, ensure_ascii=False)
            
    def add_discovered_element(self, element_name: str):
        if element_name not in self.discovered_data["entdeckte_elemente"]:
            self.discovered_data["entdeckte_elemente"].append(element_name)
            self.save_discovered_data()

    def add_discovered_spell(self, spell_data: Dict):
        spell_name = spell_data.get("name")
        if spell_name and spell_name not in self.discovered_data["entdeckte_zauber"]:
            self.discovered_data["entdeckte_zauber"][spell_name] = spell_data
            self.save_discovered_data()
            
    def unlock_with_key(self, key: str) -> List[str]:
        unlock_info = self.predefined_data.get("freischalt_codes", {}).get(key)
        if not unlock_info:
            return []

        unlocked_items = []
        item_name = unlock_info.get("name")
        item_type = unlock_info.get("type")
        item_data = unlock_info.get("data")
        
        if item_type == "element" and item_name not in self.discovered_secondary_elements:
            self.add_discovered_element(item_name)
            unlocked_items.append(item_name)
        elif item_type == "spell" and item_name not in self.discovered_spells:
            self.add_discovered_spell(item_data)
            unlocked_items.append(item_name)
        
        if unlocked_items:
            messagebox.showinfo("Erfolg", f"Folgende Elemente/Zauber wurden freigeschaltet:\n{', '.join(unlocked_items)}")
            self.unlock_entry.delete(0, tk.END)
            self.update_displays()
        else:
            messagebox.showinfo("Hinweis", "Dieser Code schaltet keine neuen Elemente/Zauber frei.")

    def reset_discovered_data(self):
        self.discovered_data = {
            "entdeckte_elemente": [],
            "entdeckte_zauber": {}
        }
        self.save_discovered_data()

    # --- UI Setup ---
    def setup_ui(self):
        self.root.configure(fg_color=THEME_COLORS['background'])
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🧙‍♂️ Erweiterter Magie-Baukasten",
            font=ctk.CTkFont(family="Cinzel", size=24, weight="bold"),
            text_color=THEME_COLORS['text_main']
        )
        title_label.pack(pady=10)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Entdecke unendliche Kombinationen durch KI-gestützte Magie-Forschung!",
            font=ctk.CTkFont(family="Roboto", size=14),
            text_color=THEME_COLORS['text_accent']
        )
        subtitle_label.pack()
        
        workshop_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        workshop_frame.pack(fill="both", expand=True)
        
        workshop_frame.grid_columnconfigure((0, 1, 2), weight=1)
        workshop_frame.grid_rowconfigure(0, weight=1)
        
        self.setup_left_panel(workshop_frame)
        self.setup_middle_panel(workshop_frame)
        self.setup_right_panel(workshop_frame)

    def setup_left_panel(self, parent):
        self.left_frame = ctk.CTkFrame(parent, fg_color=THEME_COLORS['card_bg'], corner_radius=15, border_color=THEME_COLORS['border_dark'], border_width=2)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        title = ctk.CTkLabel(self.left_frame, text="📚 Magie-Bibliothek", font=ctk.CTkFont(family="Cinzel", size=18, weight="bold"), text_color=THEME_COLORS['text_main'])
        title.pack(pady=(10, 20))
        
        api_frame = ctk.CTkFrame(self.left_frame, fg_color=THEME_COLORS['frame_bg'], corner_radius=12, border_color=THEME_COLORS['border'], border_width=1)
        api_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        api_title = ctk.CTkLabel(api_frame, text="🤖 KI-Assistent", font=ctk.CTkFont(family="Roboto", weight="bold"), text_color=THEME_COLORS['text_main'])
        api_title.pack(pady=(10, 5))
        
        self.api_entry = ctk.CTkEntry(api_frame, placeholder_text="Gemini API Key", show="*", width=300, fg_color=THEME_COLORS['card_bg'], text_color=THEME_COLORS['text_light'])
        self.api_entry.pack(padx=10, pady=5)
        
        test_frame = ctk.CTkFrame(api_frame, fg_color="transparent")
        test_frame.pack(fill="x", padx=10, pady=5)
        
        self.test_btn = ctk.CTkButton(test_frame, text="API Testen", command=self.test_api, width=120, fg_color=THEME_COLORS['button_main'], hover_color=THEME_COLORS['button_hover'], text_color=THEME_COLORS['text_dark'])
        self.test_btn.pack(side="left")
        
        self.api_status_label = ctk.CTkLabel(test_frame, text="⚠️ Bitte API-Schlüssel eingeben.", width=200, text_color="red")
        self.api_status_label.pack(side="left", padx=(10, 0))
        
        self.elements_scroll = ctk.CTkScrollableFrame(self.left_frame, fg_color="transparent")
        self.elements_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # --- Freischalt-Code Section ---
        unlock_frame = ctk.CTkFrame(self.elements_scroll, fg_color=THEME_COLORS['frame_bg'], corner_radius=12, border_color=THEME_COLORS['border'], border_width=1)
        unlock_frame.pack(fill="x", padx=5, pady=(0, 20))
        
        unlock_title = ctk.CTkLabel(unlock_frame, text="🔓 Freischalt-Code", font=ctk.CTkFont(family="Roboto", weight="bold"), text_color=THEME_COLORS['text_main'])
        unlock_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.unlock_entry = ctk.CTkEntry(unlock_frame, placeholder_text="Code eingeben", width=250)
        self.unlock_entry.pack(padx=10, pady=5, fill="x")
        
        unlock_btn = ctk.CTkButton(unlock_frame, text="Freischalten", command=self.unlock_item, fg_color=THEME_COLORS['button_main'], hover_color=THEME_COLORS['button_hover'], text_color=THEME_COLORS['text_dark'])
        unlock_btn.pack(padx=10, pady=5, fill="x")
        # --- End Freischalt-Code Section ---
        
        # --- Eigener Baustein Section ---
        custom_frame = ctk.CTkFrame(self.elements_scroll, fg_color=THEME_COLORS['frame_bg'], corner_radius=12, border_color=THEME_COLORS['border'], border_width=1)
        custom_frame.pack(fill="x", padx=5, pady=(0, 20))

        custom_title = ctk.CTkLabel(custom_frame, text="✍️ Eigener Baustein", font=ctk.CTkFont(family="Roboto", weight="bold"), text_color=THEME_COLORS['text_main'])
        custom_title.pack(anchor="w", padx=10, pady=(10, 5))

        self.custom_input_entry = ctk.CTkEntry(custom_frame, placeholder_text="Bausteinname", width=250)
        self.custom_input_entry.pack(padx=10, pady=5, fill="x")

        self.create_custom_btn = ctk.CTkButton(custom_frame, text="Erstellen", command=self.create_custom_element, fg_color=THEME_COLORS['button_main'], hover_color=THEME_COLORS['button_hover'], text_color=THEME_COLORS['text_dark'])
        self.create_custom_btn.pack(padx=10, pady=5, fill="x")
        # --- End Eigener Baustein Section ---
        
        base_title = ctk.CTkLabel(self.elements_scroll, text="Basis-Elemente:", font=ctk.CTkFont(family="Roboto", weight="bold"), text_color=THEME_COLORS['text_main'])
        base_title.pack(anchor="w", pady=(0, 10))
        
        self.base_elements_frame = ctk.CTkFrame(self.elements_scroll, fg_color="transparent")
        self.base_elements_frame.pack(fill="x", pady=(0, 20))
        
        self.secondary_title = ctk.CTkLabel(self.elements_scroll, text="Entdeckte Elemente (0):", font=ctk.CTkFont(family="Roboto", weight="bold"), text_color=THEME_COLORS['text_main'])
        self.secondary_title.pack(anchor="w", pady=(0, 10))
        
        self.secondary_elements_frame = ctk.CTkFrame(self.elements_scroll, fg_color="transparent")
        self.secondary_elements_frame.pack(fill="x", pady=(0, 20))
        
        self.spells_title = ctk.CTkLabel(self.elements_scroll, text="Entdeckte Zauber (0):", font=ctk.CTkFont(family="Roboto", weight="bold"), text_color=THEME_COLORS['text_main'])
        self.spells_title.pack(anchor="w", pady=(0, 10))
        
        self.spells_frame = ctk.CTkFrame(self.elements_scroll, fg_color="transparent")
        self.spells_frame.pack(fill="x", pady=(0, 20))
        
        effects_title = ctk.CTkLabel(self.elements_scroll, text="Wirkungsarten:", font=ctk.CTkFont(family="Roboto", weight="bold"), text_color=THEME_COLORS['text_main'])
        effects_title.pack(anchor="w", pady=(0, 10))
        
        self.effects_frame = ctk.CTkFrame(self.elements_scroll, fg_color="transparent")
        self.effects_frame.pack(fill="x", pady=(0, 20))
        
        abilities_title = ctk.CTkLabel(self.elements_scroll, text="Fähigkeitsarten:", font=ctk.CTkFont(family="Roboto", weight="bold"), text_color=THEME_COLORS['text_main'])
        abilities_title.pack(anchor="w", pady=(0, 10))
        
        self.abilities_frame = ctk.CTkFrame(self.elements_scroll, fg_color="transparent")
        self.abilities_frame.pack(fill="x")
        
    def setup_middle_panel(self, parent):
        self.middle_frame = ctk.CTkFrame(parent, fg_color=THEME_COLORS['frame_bg'], corner_radius=15, border_color=THEME_COLORS['border'], border_width=2)
        self.middle_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        
        title = ctk.CTkLabel(self.middle_frame, text="⚗️ Universeller Experimentierlabor", font=ctk.CTkFont(family="Cinzel", size=18, weight="bold"), text_color=THEME_COLORS['text_main'])
        title.pack(pady=(10, 20))
        
        self.drop_zone = ctk.CTkFrame(self.middle_frame, fg_color=THEME_COLORS['card_bg'], border_width=2, border_color=THEME_COLORS['border'], corner_radius=15)
        self.drop_zone.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.drop_zone.bind("<ButtonRelease-1>", self.on_drop)
        
        self.drop_zone_label = ctk.CTkLabel(
            self.drop_zone,
            text="Ziehe Elemente hierher zum Kombinieren\n(Drag-and-Drop)",
            text_color=THEME_COLORS['text_accent'],
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.drop_zone_label.pack(pady=20)
        
        self.components_frame = ctk.CTkFrame(self.drop_zone, fg_color="transparent")
        self.components_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.status_label = ctk.CTkLabel(self.middle_frame, text="", font=ctk.CTkFont(family="Roboto", size=14), text_color=THEME_COLORS['text_accent'])
        self.status_label.pack(pady=10)
        
        button_frame = ctk.CTkFrame(self.middle_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.process_btn = ctk.CTkButton(button_frame, text="Experiment durchführen", 
                                       command=self.process_experiment_threaded, state="disabled", fg_color=THEME_COLORS['button_main'], hover_color=THEME_COLORS['button_hover'], text_color=THEME_COLORS['text_dark'])
        self.process_btn.pack(side="left", expand=True, padx=(0, 10))
        
        self.clear_btn = ctk.CTkButton(button_frame, text="Labor leeren", command=self.clear_experiment, fg_color=THEME_COLORS['button_main'], hover_color=THEME_COLORS['button_hover'], text_color=THEME_COLORS['text_dark'])
        self.clear_btn.pack(side="left", expand=True)
        
    def setup_right_panel(self, parent):
        self.right_frame = ctk.CTkFrame(parent, fg_color=THEME_COLORS['card_bg'], corner_radius=15, border_color=THEME_COLORS['border_dark'], border_width=2)
        self.right_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0))
        
        title = ctk.CTkLabel(self.right_frame, text="📜 Zauber-Details", font=ctk.CTkFont(family="Cinzel", size=18, weight="bold"), text_color=THEME_COLORS['text_main'])
        title.pack(pady=(10, 20))
        
        self.spell_preview_frame = ctk.CTkFrame(self.right_frame, fg_color=THEME_COLORS['frame_bg'], corner_radius=12, border_color=THEME_COLORS['border'], border_width=1)
        self.spell_preview_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        preview_title = ctk.CTkLabel(self.spell_preview_frame, text="📋 Aktueller Zauber:", font=ctk.CTkFont(family="Roboto", weight="bold"), text_color=THEME_COLORS['text_accent'])
        preview_title.pack(pady=(10, 5))
        
        self.spell_display = ctk.CTkTextbox(self.spell_preview_frame, height=200, fg_color=THEME_COLORS['card_bg'], text_color=THEME_COLORS['text_light'], wrap=tk.WORD)
        self.spell_display.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        button_frame1 = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        button_frame1.pack(fill="x", padx=20, pady=(0, 10))
        
        self.generate_btn = ctk.CTkButton(button_frame1, text="🧙‍♂️ Zauber generieren", 
                                        command=self.generate_spell_threaded, state="disabled", fg_color=THEME_COLORS['button_main'], hover_color=THEME_COLORS['button_hover'], text_color=THEME_COLORS['text_dark'])
        self.generate_btn.pack(side="left", expand=True, padx=(0, 10))
        
        self.export_btn = ctk.CTkButton(button_frame1, text="💾 JSON Export", 
                                      command=self.export_spell, state="disabled", fg_color=THEME_COLORS['button_main'], hover_color=THEME_COLORS['button_hover'], text_color=THEME_COLORS['text_dark'])
        self.export_btn.pack(side="left", expand=True)
        
        button_frame2 = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        button_frame2.pack(fill="x", padx=20, pady=(0, 20))
        
        self.reset_btn = ctk.CTkButton(button_frame2, text="🔄 Alles zurücksetzen", command=self.reset_all, fg_color=THEME_COLORS['button_main'], hover_color=THEME_COLORS['button_hover'], text_color=THEME_COLORS['text_dark'])
        self.reset_btn.pack(expand=True)

    def create_custom_element(self):
        element_name = self.custom_input_entry.get().strip()
        if not element_name:
            messagebox.showwarning("Warnung", "Bitte geben Sie einen Namen für den Baustein ein!")
            return
            
        item_data = {'name': element_name, 'type': 'custom_input'}
        self.add_to_experiment(item_data)
        self.custom_input_entry.delete(0, tk.END)

    def unlock_item(self):
        key = self.unlock_entry.get().strip()
        if not key:
            messagebox.showwarning("Warnung", "Bitte geben Sie einen Freischalt-Code ein!")
            return

        unlock_info = self.predefined_data.get("freischalt_codes", {}).get(key)
        if not unlock_info:
            messagebox.showerror("Fehler", "Ungültiger Freischalt-Code.")
            return

        unlocked_items = []
        item_name = unlock_info.get("name")
        item_type = unlock_info.get("type")
        item_data = unlock_info.get("data")
        
        if item_type == "element" and item_name not in self.discovered_secondary_elements:
            self.add_discovered_element(item_name)
            unlocked_items.append(item_name)
        elif item_type == "spell" and item_name not in self.discovered_spells:
            self.add_discovered_spell(item_data)
            unlocked_items.append(item_name)
        
        if unlocked_items:
            messagebox.showinfo("Erfolg", f"Folgende Elemente/Zauber wurden freigeschaltet:\n{', '.join(unlocked_items)}")
            self.unlock_entry.delete(0, tk.END)
            self.update_displays()
        else:
            messagebox.showinfo("Hinweis", "Dieser Code schaltet keine neuen Elemente/Zauber frei.")

    def create_draggable_item(self, parent, item_data):
        item_frame = ctk.CTkFrame(parent, fg_color=THEME_COLORS['button_main'], corner_radius=12)
        
        label_text = item_data.get('text', '')
        if item_data['type'] == 'spell':
            label_text = f"🔮 {item_data['name']}"
        elif item_data['type'] == 'element':
            label_text = f"{self.get_component_emoji(item_data)} {item_data['name']}"
        elif item_data['type'] == 'custom_input':
            label_text = f"✍️ {item_data['name']}"
        else:
            label_text = f"{self.get_component_emoji(item_data)} {item_data['name']}"
            
        label = ctk.CTkLabel(item_frame, text=label_text, text_color=THEME_COLORS['text_dark'], font=ctk.CTkFont(size=14, weight="bold"))
        label.pack(padx=10, pady=5)
        
        item_frame.bind("<Button-1>", lambda event, data=item_data: self.on_drag_start(event, data))
        label.bind("<Button-1>", lambda event, data=item_data: self.on_drag_start(event, data))
        
        item_frame.configure(cursor="hand2")
        return item_frame

    def on_drag_start(self, event, item_data):
        self.dragged_item_data = item_data
        
        self.drag_window = ctk.CTkToplevel(self.root)
        self.drag_window.overrideredirect(True)
        self.drag_window.wm_attributes("-topmost", True)
        self.drag_window.wm_attributes("-alpha", 0.7)
        
        label_text = item_data.get('text', '')
        if item_data['type'] == 'spell':
            label_text = f"🔮 {item_data['name']}"
        elif item_data['type'] == 'element':
            label_text = f"{self.get_component_emoji(item_data)} {item_data['name']}"
        elif item_data['type'] == 'custom_input':
            label_text = f"✍️ {item_data['name']}"
        else:
            label_text = f"{self.get_component_emoji(item_data)} {item_data['name']}"
        
        drag_label = ctk.CTkLabel(self.drag_window, text=label_text, font=ctk.CTkFont(size=14, weight="bold"), fg_color=THEME_COLORS['button_hover'], text_color=THEME_COLORS['text_dark'])
        drag_label.pack(padx=10, pady=5)
        
        self.root.bind("<Motion>", self.on_drag_motion)
        self.root.bind("<ButtonRelease-1>", self.on_drag_stop)

    def on_drag_motion(self, event):
        if self.drag_window:
            x = self.root.winfo_pointerx() - self.drag_window.winfo_width() // 2
            y = self.root.winfo_pointery() - self.drag_window.winfo_height() // 2
            self.drag_window.geometry(f"+{x}+{y}")
            
            dz_x = self.drop_zone.winfo_rootx()
            dz_y = self.drop_zone.winfo_rooty()
            dz_width = self.drop_zone.winfo_width()
            dz_height = self.drop_zone.winfo_height()
            
            if dz_x <= event.x_root <= dz_x + dz_width and dz_y <= event.y_root <= dz_y + dz_height:
                self.drop_zone.configure(border_color=THEME_COLORS['button_success'])
            else:
                self.drop_zone.configure(border_color=THEME_COLORS['border'])

    def on_drag_stop(self, event):
        self.root.unbind("<Motion>")
        self.root.unbind("<ButtonRelease-1>")
        
        if self.drag_window:
            self.drag_window.destroy()
            self.drag_window = None

        dz_x = self.drop_zone.winfo_rootx()
        dz_y = self.drop_zone.winfo_rooty()
        dz_width = self.drop_zone.winfo_width()
        dz_height = self.drop_zone.winfo_height()
        
        if dz_x <= event.x_root <= dz_x + dz_width and dz_y <= event.y_root <= dz_y + dz_height:
            if self.dragged_item_data:
                self.add_to_experiment(self.dragged_item_data)
        
        self.dragged_item_data = None
        self.drop_zone.configure(border_color=THEME_COLORS['border'])

    def on_drop(self, event):
        # The drag_stop event handles this, so this method is mostly for cleanup
        pass

    def setup_base_elements(self):
        for widget in self.base_elements_frame.winfo_children():
            widget.destroy()
        for element in self.base_elements:
            item_data = {'name': element, 'type': 'element'}
            item_frame = self.create_draggable_item(self.base_elements_frame, item_data)
            item_frame.pack(fill="x", padx=5, pady=5)
            
    def setup_effect_types(self):
        for widget in self.effects_frame.winfo_children():
            widget.destroy()
        for effect, emoji in self.effect_types:
            item_data = {'name': effect, 'type': 'effect'}
            item_frame = self.create_draggable_item(self.effects_frame, item_data)
            item_frame.pack(fill="x", padx=5, pady=5)
            
    def setup_ability_types(self):
        for widget in self.abilities_frame.winfo_children():
            widget.destroy()
        for ability, emoji in self.ability_types:
            item_data = {'name': ability, 'type': 'ability'}
            item_frame = self.create_draggable_item(self.abilities_frame, item_data)
            item_frame.pack(fill="x", padx=5, pady=5)

    def add_to_experiment(self, item_data: Dict):
        self.experiment_components.append(item_data)
        self.update_experiment_display()
        
    def update_experiment_display(self):
        for widget in self.components_frame.winfo_children():
            widget.destroy()
            
        if not self.experiment_components:
            self.drop_zone_label.pack(pady=20)
            self.process_btn.configure(state="disabled")
            return
        else:
            self.drop_zone_label.pack_forget()
            
        for i, comp in enumerate(self.experiment_components):
            comp_frame = ctk.CTkFrame(self.components_frame, fg_color=THEME_COLORS['frame_bg'], corner_radius=8)
            comp_frame.pack(fill="x", padx=5, pady=2)
            
            emoji = self.get_component_emoji(comp)
            comp_label = ctk.CTkLabel(comp_frame, text=f"{emoji} {comp['name']}", text_color=THEME_COLORS['text_light'])
            comp_label.pack(side="left", padx=10, pady=5)
            
            remove_btn = ctk.CTkButton(
                comp_frame,
                text="×",
                width=30,
                height=30,
                fg_color=THEME_COLORS['background'],
                hover_color=THEME_COLORS['border'],
                command=lambda idx=i: self.remove_from_experiment(idx)
            )
            remove_btn.pack(side="right", padx=10, pady=5)
            
        can_process = len(self.experiment_components) >= 2 or (len(self.experiment_components) >= 1 and self.api_key)
        self.process_btn.configure(state="normal" if can_process else "disabled")
        
    def get_component_emoji(self, comp: Dict) -> str:
        if comp['type'] == 'element':
            return self.element_emojis.get(comp['name'], '🔮')
        elif comp['type'] == 'effect':
            effect_emojis = {
                'Projektil': '🏹', 'Aura/Fläche': '🌟', 'Verstärkung': '💪',
                'Erschaffung': '🗿', 'Transformation': '🔄', 'Kontrolle': '🎮'
            }
            return effect_emojis.get(comp['name'], '🎯')
        elif comp['type'] == 'ability':
            ability_emojis = {
                'Kampf-Manöver': '⚔️', 'Defensiv-Haltung': '🛡️', 
                'Unterstützung': '🤝', 'Taktik': '♟️'
            }
            return ability_emojis.get(comp['name'], '✨')
        elif comp['type'] == 'spell':
            return '🔮'
        elif comp['type'] == 'custom_input':
            return '✍️'
        return '❓'
        
    def remove_from_experiment(self, index: int):
        if 0 <= index < len(self.experiment_components):
            self.experiment_components.pop(index)
            self.update_experiment_display()
            
    def clear_experiment(self):
        self.experiment_components.clear()
        self.update_experiment_display()
        self.status_label.configure(text="")
        
    def test_api(self):
        api_key = self.api_entry.get().strip()
        if not api_key:
            self.api_status_label.configure(text="⚠️ API-Schlüssel eingeben", text_color="red")
            return
            
        self.api_status_label.configure(text="🔄 Teste API...", text_color="blue")
        self.test_btn.configure(state="disabled")
        
        threading.Thread(target=self._test_api_thread, args=(api_key,), daemon=True).start()
        
    def _test_api_thread(self, api_key: str):
        try:
            test_payload = {
                "contents": [{
                    "parts": [{"text": "Hallo! Dies ist ein Test der Gemini API."}]
                }]
            }
            
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}",
                headers={"Content-Type": "application/json"},
                json=test_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'error' in data:
                    raise Exception(data['error']['message'])
                    
                self.api_key = api_key
                self.root.after(0, lambda: self.api_status_label.configure(
                    text="✅ API erfolgreich getestet!", text_color="green"))
                self.root.after(0, lambda: self.generate_btn.configure(state="normal"))
                self.root.after(0, self.update_experiment_display)
            else:
                print(f"API-Fehler: HTTP {response.status_code}")
                raise Exception(f"HTTP {response.status_code}")
                
        except Exception as e:
            print(f"API-Test Fehler: {str(e)}")
            self.root.after(0, lambda: self.api_status_label.configure(
                text=f"❌ API-Fehler: {str(e)}", text_color="red"))
            self.api_key = ""
            self.root.after(0, lambda: self.generate_btn.configure(state="disabled"))
        finally:
            self.root.after(0, lambda: self.test_btn.configure(state="normal"))
            
    def process_experiment_threaded(self):
        if len(self.experiment_components) < 1:
            return
            
        self.status_label.configure(text="🧠 KI analysiert Kombination...", text_color="blue")
        self.process_btn.configure(state="disabled")
        
        threading.Thread(target=self._process_experiment_thread, daemon=True).start()
        
    def _process_experiment_thread(self):
        try:
            element_components = [c for c in self.experiment_components if c['type'] == 'element']
            
            new_item_data = None
            status_message = ""
            status_color = "red"
            used_components = self.experiment_components[:] # Make a copy

            # Scenario 1: Check for predefined element combinations (exactly 2 elements)
            if len(element_components) == 2 and not any(c['type'] in ['spell', 'effect', 'ability', 'custom_input'] for c in self.experiment_components):
                sorted_components = sorted([c['name'] for c in element_components])
                key = '+'.join(sorted_components)
                predefined = self.predefined_data.get("element_kombinationen", {}).get(key)
                
                if predefined:
                    if predefined['name'] not in self.discovered_secondary_elements:
                        self.discovered_secondary_elements.add(predefined['name'])
                        self.add_discovered_element(predefined['name'])
                        self.element_emojis[predefined['name']] = predefined['emoji']
                        
                        new_item_data = {'name': predefined['name'], 'type': 'element'}
                        status_message = f"🎉 Neues Element entdeckt!\n{predefined['emoji']} {predefined['name']}"
                        status_color = "green"
                    else:
                        status_message = f"Dieses Element wurde bereits entdeckt: {predefined['name']}"
                        status_color = "yellow"
                else:
                    raise Exception('Ungültige Kombination. Pre-defined Kombinationen benötigen genau 2 Basis- oder Entdeckte-Elemente.')
            
                # Update experiment components based on predefined result
                if new_item_data:
                    temp_list = self.experiment_components.copy()
                    for item_to_remove in element_components:
                        temp_list.remove(item_to_remove)
                    temp_list.append(new_item_data)
                    self.experiment_components = temp_list
                else:
                    # If element was already discovered, just remove the two used components
                    temp_list = self.experiment_components.copy()
                    for item_to_remove in element_components:
                        temp_list.remove(item_to_remove)
                    self.experiment_components = temp_list
                
                self.root.after(0, lambda: self.status_label.configure(text=status_message, text_color=status_color))
                self.root.after(0, self.update_displays)
                self.root.after(0, self.update_experiment_display)
                return
            
            # All other AI-based scenarios (spells, abilities, custom elements)
            if not self.api_key:
                raise Exception('KI-API nicht verfügbar. Bitte API-Schlüssel eingeben und testen.')
                
            component_types = [c['type'] for c in self.experiment_components]
            has_spell = 'spell' in component_types
            has_element = 'element' in component_types
            has_effect = 'effect' in component_types
            has_ability = 'ability' in component_types
            has_custom = 'custom_input' in component_types
            num_spells = len([c for c in self.experiment_components if c['type'] == 'spell'])
            num_elements = len([c for c in self.experiment_components if c['type'] == 'element'])

            if num_spells >= 2 and not has_element and not has_effect and not has_ability and not has_custom:
                result_type = 'spell_combination'
            elif has_effect:
                result_type = 'spell'
            elif has_ability:
                result_type = 'ability'
            elif num_elements > 0 or has_custom:
                result_type = 'element'
            else:
                raise Exception('Ungültige Kombination. Bitte fügen Sie Elemente, Zauber oder Wirkungsarten hinzu.')
                
            result = self._generate_with_ai(used_components, result_type)
            new_item_data = {'name': result['name'], 'type': result['type']}
            
            if result_type == 'element':
                if result['name'] not in self.discovered_secondary_elements:
                    self.discovered_secondary_elements.add(result['name'])
                    self.add_discovered_element(result['name'])
                    if 'emoji' in result:
                        self.element_emojis[result['name']] = result['emoji']
                
                    status_message = f"🎉 Neues Element entdeckt!\n{result.get('emoji', '🔮')} {result['name']}"
                    status_color = "green"
                else:
                    status_message = f"Dieses Element wurde bereits entdeckt: {result['name']}"
                    status_color = "yellow"
            else: # spell or ability
                self.discovered_spells[result['name']] = result
                self.add_discovered_spell(result)
                self.current_spell = result
                
                self.root.after(0, lambda: self.display_spell(result))
                self.root.after(0, lambda: self.export_btn.configure(state="normal"))
                status_message = f"✨ Neue {'Zauber' if result_type != 'ability' else 'Fähigkeit'} entdeckt!\n🔮 {result['name']}"
                status_color = "green"

            # In all AI-based cases, we replace all components with the new one.
            self.experiment_components = [new_item_data]
            
            self.root.after(0, lambda: self.status_label.configure(text=status_message, text_color=status_color))
            self.root.after(0, self.update_displays)
            self.root.after(0, self.update_experiment_display)
            
        except Exception as e:
            print(f"Experiment-Fehler: {str(e)}")
            self.root.after(0, lambda: self.status_label.configure(
                text=f"⚠️ Fehler: {str(e)}", text_color="red"))
        finally:
            self.root.after(0, lambda: self.process_btn.configure(state="normal"))
            
    def _generate_with_ai(self, components: List[Dict], result_type: str) -> Dict:
        creative_input = ""
        component_names = []
        bausteine = []
        for c in components:
            if c['type'] == 'custom_input':
                creative_input += f"Stichwort: {c['name']}. "
            else:
                component_names.append(f"{c['name']} ({c['type']})")
                bausteine.append(c['name'])
        
        component_names_str = ', '.join(component_names)
        
        level = max(0, len(components) - 1) if result_type != 'spell_combination' else sum(
            self.discovered_spells.get(c['name'], {}).get('level', 1) 
            for c in components if c['type'] == 'spell'
        )
        mana_cost = level if level > 0 else 1
        
        prompt = f"""Du bist ein Experte für das Tabletop-RPG-Magie-System des Nutzers.
Systemregeln:
- Die Welt benutzt ein d10-Würfelsystem.
- Die 10 Seiten des Würfels sind belegt mit Kritischer Erfolg (1), Kritischer Misserfolg (10), Angriff (A), Verteidigung (V) oder Mana (M).
- Mana ist notwendig, um Zauber oder Fähigkeiten zu wirken.
- Zauber sind magische Effekte, Fähigkeiten sind nicht-magische, kampfspezifische Aktionen.
- Alle Würfel werden gleichzeitig am Anfang der Runde gewürfelt. Reaktive Effekte müssen sich auf diese initialen Würfe beziehen.
- Wenn zwei identische Zauber kombiniert werden, entsteht eine stärkere Version dieses Zaubers.
Komponenten für Experiment: {component_names_str}
Kreative Einflüsse: {creative_input}
Aufgabe: Erschaffe einen neuen {'Zauber' if result_type != 'ability' else 'Fähigkeit'} basierend auf den Komponenten.
Antwortformat (gib NUR das JSON zurück):
{{
  "name": "Kreativer Name",
  "type": "{'spell' if result_type != 'ability' else 'ability'}",
  "level": {level},
  "mana_kosten": {mana_cost},
  "kurzbeschreibung": "Kurze kreative Beschreibung",
  "beschreibung": "Detaillierte Beschreibung mit Atmosphäre",
  "effekt": "Mechanische Spielregeln, die sich auf Angriffs(A), Verteidigungs(V) oder Mana(M) Würfe beziehen. Benutze keinen Kritischen Erfolg auf Verteidigung. Beschreibe keine reaktiven Effekte die während einer Verteidigungsaktion passieren.",
  "schaden": "2W6+1" oder "Variabel",
  "rettungswurf_gegner": "Geschicklichkeit/Konstitution/etc",
  "reaktiver_effekt": "Spezialeffekt basierend auf Würfelergebnissen zu Rundenbeginn. Benutze keinen Kritischen Erfolg auf Verteidigung. Beschreibe keine reaktiven Effekte die während einer Verteidigungsaktion passieren."
}}"""
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 2048
            }
        }
        
        max_retries = 5
        initial_delay = 1
        
        for i in range(max_retries):
            try:
                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.api_key}",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 429:
                    delay = initial_delay * (2 ** i)
                    time.sleep(delay)
                    continue
                    
                if not response.ok:
                    print(f"API-Fehler: HTTP {response.status_code}")
                    raise Exception(f"HTTP {response.status_code}")
                    
                data = response.json()
                
                if 'error' in data:
                    print(f"KI-Fehler: {data['error']['message']}")
                    raise Exception(data['error']['message'])
                    
                ai_response = data['candidates'][0]['content']['parts'][0]['text'].strip()
                
                
                json_match = re.search(r'\{[\s\S]*\}', ai_response)
                if not json_match:
                    print('KI-Antwort enthält kein gültiges JSON-Objekt.')
                    raise Exception('KI-Antwort enthält kein gültiges JSON-Objekt.')
                    
                ai_response = json_match.group(0)
                generated_data = json.loads(ai_response)
                
                generated_data['bausteine'] = bausteine

                if result_type != 'spell_combination':
                    generated_data['level'] = level
                    generated_data['mana_kosten'] = mana_cost
                    
                return generated_data
                
            except Exception as e:
                print(f"API-Anfrage Fehler (Versuch {i+1}): {str(e)}")
                if i == max_retries - 1:
                    raise e
                time.sleep(1)
                
        raise Exception("Max retries exceeded")
        
    def generate_spell_threaded(self):
        if not self.experiment_components:
            messagebox.showwarning("Warnung", "Bitte fügen Sie Komponenten zum Experiment hinzu!")
            return
            
        if not self.api_key:
            messagebox.showwarning("Warnung", "Bitte testen Sie zuerst die API-Verbindung!")
            return
            
        self.status_label.configure(text="🧠 Generiere Zauber...", text_color="blue")
        self.generate_btn.configure(state="disabled")
        
        threading.Thread(target=self._generate_spell_thread, daemon=True).start()
        
    def _generate_spell_thread(self):
        try:
            result = self._generate_with_ai(self.experiment_components, 'spell')
            self.discovered_spells[result['name']] = result
            self.add_discovered_spell(result)
            self.current_spell = result
            
            self.root.after(0, lambda: self.display_spell(result))
            self.root.after(0, self.update_displays)
            self.root.after(0, lambda: self.export_btn.configure(state="normal"))
            self.root.after(0, lambda: self.status_label.configure(
                text=f"✨ Zauber generiert!\n🔮 {result['name']}", text_color="green"))
                
        except Exception as e:
            print(f"Zauber-Generierungsfehler: {str(e)}")
            self.root.after(0, lambda: self.status_label.configure(
                text=f"⚠️ Fehler: {str(e)}", text_color="red"))
        finally:
            self.root.after(0, lambda: self.generate_btn.configure(state="normal"))
            
    def display_spell(self, spell: Dict):
        # Bausteine aus dem Zauber-Objekt holen, ansonsten eine leere Liste verwenden
        bausteine = spell.get('bausteine', [])
        # Prüfen, ob die Liste nicht leer ist, bevor sie gejoint wird
        bausteine_str = ', '.join(f'"{b}"' for b in bausteine) if bausteine else 'Keine Bausteine'
        
        display_text = f"""╔══════════════════════════════════════════════════════════════
{'🧙‍♂️ ZAUBER' if spell.get('type') == 'spell' else '⚔️ FÄHIGKEIT'}: {spell.get('name', 'Unbenannt')} (Level {spell.get('level', 1)})
╚══════════════════════════════════════════════════════════════
📋 DETAILS:
• Typ: {'Zauber' if spell.get('type') == 'spell' else 'Fähigkeit'}
• Bausteine: {bausteine_str}
• Level: {spell.get('level', 1)}
• Mana-Kosten: {spell.get('mana_kosten', 1)}
• Schaden: {spell.get('schaden', 'Variabel')}

💫 KURZBESCHREIBUNG:
{spell.get('kurzbeschreibung', 'Nicht verfügbar')}

📖 BESCHREIBUNG:
{spell.get('beschreibung', 'Nicht verfügbar')}

⚡ EFFEKT:
{spell.get('effekt', 'Nicht verfügbar')}

🎲 RETTUNGSWURF:
{spell.get('rettungswurf_gegner', 'Nicht verfügbar')}

✨ REAKTIVER EFFEKT:
{spell.get('reaktiver_effekt', 'Nicht verfügbar')}
══════════════════════════════════════════════════════════════"""
        
        self.spell_display.delete("0.0", tk.END)
        self.spell_display.insert("0.0", display_text)
        
    def update_displays(self):
        self.discovered_secondary_elements = set(self.discovered_data.get("entdeckte_elemente", []))
        self.discovered_spells = self.discovered_data.get("entdeckte_zauber", {})
        self.setup_base_elements()
        self.setup_effect_types()
        self.setup_ability_types()
        self.update_secondary_elements()
        self.update_discovered_spells()
        
    def update_secondary_elements(self):
        for widget in self.secondary_elements_frame.winfo_children():
            widget.destroy()
            
        count = len(self.discovered_secondary_elements)
        self.secondary_title.configure(text=f"Entdeckte Elemente ({count}):")
        
        for element_name in sorted(list(self.discovered_secondary_elements)):
            item_data = {'name': element_name, 'type': 'element'}
            item_frame = self.create_draggable_item(self.secondary_elements_frame, item_data)
            item_frame.pack(fill="x", padx=5, pady=5)
            
    def update_discovered_spells(self):
        for widget in self.spells_frame.winfo_children():
            widget.destroy()
            
        count = len(self.discovered_spells)
        self.spells_title.configure(text=f"Entdeckte Zauber ({count}):")
        
        for spell_name, spell_data in sorted(self.discovered_spells.items()):
            item_data = {'name': spell_name, 'type': 'spell'}
            item_frame = self.create_draggable_item(self.spells_frame, item_data)
            item_frame.bind("<Button-1>", lambda event, data=spell_data: self.select_spell(data))
            item_frame.pack(fill="x", padx=5, pady=5)
            
    def select_spell(self, spell_data: Dict):
        self.current_spell = spell_data
        self.display_spell(spell_data)
        self.export_btn.configure(state="normal")
        
    def export_spell(self):
        if not self.current_spell:
            messagebox.showwarning("Warnung", "Bitte erstellen Sie zuerst einen Zauber!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Zauber exportieren",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialvalue=f"{self.current_spell.get('name', 'zauber').replace(' ', '_')}.json"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.current_spell, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Erfolg", "💾 Zauber erfolgreich exportiert!")
            except Exception as e:
                messagebox.showerror("Fehler", f"Export-Fehler: {str(e)}")
                
    def import_spell(self):
        filename = filedialog.askopenfilename(
            title="Zauber importieren",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                spell = json.load(f)
            
            if not spell.get('name'):
                raise Exception('Ungültiges Zauber-Format: Name fehlt')
                
            self.current_spell = spell
            self.discovered_spells[spell['name']] = spell
            self.add_discovered_spell(spell)
            self.display_spell(spell)
            self.update_displays()
            
            self.export_btn.configure(state="normal")
            
            messagebox.showinfo("Erfolg", "✨ Zauber erfolgreich importiert!")
            
        except Exception as e:
            messagebox.showerror("Import-Fehler", f"Import-Fehler: {str(e)}")
            
    def reset_all(self):
        if messagebox.askyesno("Bestätigung", "Möchten Sie wirklich alles zurücksetzen?"):
            self.experiment_components.clear()
            self.current_spell = None
            self.discovered_secondary_elements.clear()
            self.discovered_spells.clear()
            self.reset_discovered_data()
            
            self.update_experiment_display()
            self.update_displays()
            
            self.spell_display.delete("0.0", tk.END)
            self.status_label.configure(text="")
            self.custom_input_entry.delete(0, tk.END)
            self.custom_input_entry.insert(0, "Bausteinname")
            
            self.export_btn.configure(state="disabled")
            if not self.api_key:
                self.generate_btn.configure(state="disabled")
                
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MagicWorkshop()
    app.run()
