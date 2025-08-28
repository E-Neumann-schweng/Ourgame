import customtkinter as ctk
import math
from tkinter import messagebox
from global_config import (
    MAX_KOPFWERT, MAX_TALENTWERT, AP_KOSTEN_TALENT,
    TALENT_PROGRESS_THRESHOLD, WERT_ZU_TALENTE_MAPPING, TALENT_GRUPPEN
)

class TalentseiteFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#2c1e1e")
        self.controller = controller
        
        # Daten-Container
        self.kopfwerte = {}
        self.talentwerte = {}
        self.talent_increase_progress = {}
        self.step_size = 1

        # UI-Elemente
        self.kopfwerte_elements = {}
        self.talentwerte_elements = {}
        self.step_buttons = {}

        # Layout-Konfiguration
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_widgets()
        
        # UI-Element für Feedback
        self.feedback_label = ctk.CTkLabel(self, text="", font=("Roboto", 12), text_color="#52a67c")
        self.feedback_label.grid(row=3, column=0, pady=(0, 5))
        
    def create_widgets(self):
        # Header-Frame mit AP und Buttons (oben)
        header_frame = ctk.CTkFrame(master=self, fg_color="#3e2b2b", corner_radius=20, border_color="#a67c52", border_width=2)
        header_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        # AP-Anzeige links
        self.ap_label = ctk.CTkLabel(master=header_frame, text="Verfügbare AP: --", font=("Cinzel", 20, "bold"), text_color="#a67c52")
        self.ap_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        # Schrittgrößen-Buttons in der Mitte
        step_container = ctk.CTkFrame(master=header_frame, fg_color="transparent")
        step_container.grid(row=0, column=1, pady=10)
        
        step_label = ctk.CTkLabel(master=step_container, text="Schritt:", font=("Roboto", 16), text_color="#d4c59a")
        step_label.pack(side="left", padx=(0, 8))
        
        btn_step_1 = ctk.CTkButton(master=step_container, text="1", width=40, command=lambda: self.set_step_size(1), fg_color="#a67c52", hover_color="#c49a6c", text_color="black")
        btn_step_1.pack(side="left", padx=4)
        self.step_buttons[1] = btn_step_1

        btn_step_10 = ctk.CTkButton(master=step_container, text="10", width=40, command=lambda: self.set_step_size(10), fg_color="#a67c52", hover_color="#c49a6c", text_color="black")
        btn_step_10.pack(side="left", padx=4)
        self.step_buttons[10] = btn_step_10

        # Speichern-Button rechts
        save_button = ctk.CTkButton(master=header_frame, text="Speichern", command=self.save_data, font=("Cinzel", 16, "bold"), fg_color="#52a67c", hover_color="#6cc49a", corner_radius=12, text_color="black")
        save_button.grid(row=0, column=2, padx=15, pady=10, sticky="e")

        # Haupt-Content-Frame
        main_content_frame = ctk.CTkFrame(master=self, fg_color="#3e2b2b", corner_radius=20, border_color="#a67c52", border_width=2)
        main_content_frame.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        main_content_frame.grid_rowconfigure((0, 1), weight=1)
        main_content_frame.grid_columnconfigure(0, weight=1)

        # Kopfwerte-Bereich
        kopfwerte_frame = ctk.CTkFrame(master=main_content_frame, fg_color="#2b2b2b", corner_radius=15, border_color="#555555", border_width=1)
        kopfwerte_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        for i in range(len(WERT_ZU_TALENTE_MAPPING)):
            kopfwerte_frame.grid_columnconfigure(i, weight=1)

        kopfwerte_title = ctk.CTkLabel(master=kopfwerte_frame, text="Kopfwerte", font=("Cinzel", 20, "bold"), text_color="#f5deb3")
        kopfwerte_title.grid(row=0, column=0, columnspan=len(WERT_ZU_TALENTE_MAPPING), pady=(8, 10))

        for col, name in enumerate(WERT_ZU_TALENTE_MAPPING.keys()):
            wert_frame = ctk.CTkFrame(master=kopfwerte_frame, fg_color="transparent")
            wert_frame.grid(row=1, column=col, padx=3, pady=(0, 8), sticky="ew")

            label_name = ctk.CTkLabel(master=wert_frame, text=name, font=("Roboto", 14, "bold"), text_color="#d4c59a")
            label_name.pack(pady=(0, 3))

            button_container = ctk.CTkFrame(master=wert_frame, fg_color="transparent")
            button_container.pack()

            minus_button = ctk.CTkButton(master=button_container, text="-", width=25, height=25, command=lambda n=name: self.decrease_wert(n), fg_color="#a67c52", hover_color="#c49a6c", text_color="black")
            minus_button.pack(side="left", padx=(0, 2))

            label_value = ctk.CTkLabel(master=button_container, text="--", font=("Roboto", 14), width=25, text_color="white")
            label_value.pack(side="left")

            plus_button = ctk.CTkButton(master=button_container, text="+", width=25, height=25, command=lambda n=name: self.increase_wert(n), fg_color="#a67c52", hover_color="#c49a6c", text_color="black")
            plus_button.pack(side="left", padx=(2, 0))

            self.kopfwerte_elements[name] = {"label": label_value, "plus_btn": plus_button, "minus_btn": minus_button}

        # Talente-Bereich in Spalten (horizontale Anordnung)
        talente_frame = ctk.CTkFrame(master=main_content_frame, fg_color="transparent")
        talente_frame.grid(row=1, column=0, sticky="nsew")
        talente_frame.grid_columnconfigure(0, weight=1)
        talente_frame.grid_columnconfigure(1, weight=1)
        talente_frame.grid_columnconfigure(2, weight=1)
        talente_frame.grid_columnconfigure(3, weight=1)

        col_index = 0
        for group_name, talents in TALENT_GRUPPEN.items():
            group_frame = ctk.CTkFrame(master=talente_frame, fg_color="#2b2b2b", corner_radius=15, border_width=1, border_color="#555555")
            group_frame.grid(row=0, column=col_index, padx=10, pady=10, sticky="nsew")

            group_label = ctk.CTkLabel(master=group_frame, text=group_name, font=("Roboto", 16, "bold"), text_color="#f0e6d2")
            group_label.pack(pady=(8, 3))

            for name in talents:
                talent_row_frame = ctk.CTkFrame(master=group_frame, fg_color="transparent")
                talent_row_frame.pack(fill="x", padx=10, pady=1)
                talent_row_frame.grid_columnconfigure(0, weight=1)

                label_name = ctk.CTkLabel(master=talent_row_frame, text=name, font=("Roboto", 14), anchor="w", text_color="#d4c59a")
                label_name.grid(row=0, column=0, sticky="ew", padx=8, pady=3)

                button_frame = ctk.CTkFrame(master=talent_row_frame, fg_color="transparent")
                button_frame.grid(row=0, column=1, sticky="e", padx=(0, 3))

                minus_button = ctk.CTkButton(master=button_frame, text="-", width=25, height=25, command=lambda n=name: self.decrease_talent(n), fg_color="#a67c52", hover_color="#c49a6c", text_color="black")
                minus_button.pack(side="left", padx=1)

                label_value = ctk.CTkLabel(master=button_frame, text="--", font=("Roboto", 14), width=25, text_color="white")
                label_value.pack(side="left", padx=1)

                plus_button = ctk.CTkButton(master=button_frame, text="+", width=25, height=25, command=lambda n=name: self.increase_talent(n), fg_color="#a67c52", hover_color="#c49a6c", text_color="black")
                plus_button.pack(side="left", padx=1)

                self.talentwerte_elements[name] = {"label": label_value, "plus_btn": plus_button, "minus_btn": minus_button}
            
            col_index += 1
            
        # Zurück-Buttons am unteren Rand
        back_buttons = ctk.CTkFrame(self, fg_color="transparent")
        back_buttons.grid(row=2, column=0, padx=15, pady=10, sticky="ew")
        back_buttons.grid_columnconfigure((0, 1), weight=1)

        back_to_char_button = ctk.CTkButton(back_buttons, text="Zurück zur Charakterseite", command=self.go_back_to_character, font=("Cinzel", 16, "bold"), fg_color="#a67c52", hover_color="#c49a6c", corner_radius=12, text_color="black")
        back_to_char_button.grid(row=0, column=0, padx=10, sticky="ew")

        to_combat_button = ctk.CTkButton(back_buttons, text="Kampfseite", command=self.go_to_combat_page, font=("Cinzel", 16, "bold"), fg_color="#a67c52", hover_color="#c49a6c", corner_radius=12, text_color="black")
        to_combat_button.grid(row=0, column=1, padx=10, sticky="ew")


    def load_character_data(self, data):
        """Lädt die übergebenen Charakterdaten in die UI."""
        self.kopfwerte = data.get("kopfwerte", {})
        self.talentwerte = data.get("talentwerte", {})
        self.available_ap = data.get("available_ap", 0)
        self.talent_increase_progress = data.get("talent_increase_progress", {name: 0 for name in self.talentwerte.keys()})
        self.set_step_size(1)
        self.update_ui()

    def set_step_size(self, new_size):
        """Aktualisiert die Schrittgröße und Button-Farben."""
        self.step_size = new_size
        for size, btn in self.step_buttons.items():
            if size == self.step_size:
                btn.configure(fg_color="#454648", text_color="white")
            else:
                btn.configure(fg_color="#a67c52", text_color="black")
        self.update_ui()
    
    def update_ui(self):
        """Aktualisiert alle Labels und Button-Zustände."""
        self.ap_label.configure(text=f"Verfügbare AP: {self.available_ap}")
        
        for name, value in self.kopfwerte.items():
            if name in self.kopfwerte_elements:
                label = self.kopfwerte_elements[name]["label"]
                plus_btn = self.kopfwerte_elements[name]["plus_btn"]
                minus_btn = self.kopfwerte_elements[name]["minus_btn"]
                label.configure(text=f"{value}")
                
                ap_cost = len(WERT_ZU_TALENTE_MAPPING.get(name, [])) * self.step_size
                plus_btn.configure(state="normal" if self.available_ap >= ap_cost and value + self.step_size <= MAX_KOPFWERT else "disabled")
                minus_btn.configure(state="normal" if value >= self.step_size else "disabled")
                
        for name, value in self.talentwerte.items():
            if name in self.talentwerte_elements:
                label = self.talentwerte_elements[name]["label"]
                plus_btn = self.talentwerte_elements[name]["plus_btn"]
                minus_btn = self.talentwerte_elements[name]["minus_btn"]
                label.configure(text=f"{value}")
                
                ap_cost = AP_KOSTEN_TALENT * self.step_size
                plus_btn.configure(state="normal" if self.available_ap >= ap_cost and value + self.step_size <= MAX_TALENTWERT else "disabled")
                minus_btn.configure(state="normal" if value >= self.step_size else "disabled")
    
    def increase_wert(self, wert_name):
        """Erhöht den Wert eines Kopfwertes und der entsprechenden Talente."""
        points_to_add = self.step_size
        num_talents = len(WERT_ZU_TALENTE_MAPPING.get(wert_name, []))
        ap_cost = num_talents * self.step_size
        
        if self.available_ap >= ap_cost and self.kopfwerte.get(wert_name, 0) + points_to_add <= MAX_KOPFWERT:
            self.available_ap -= ap_cost
            self.kopfwerte[wert_name] += points_to_add
            
            for talent in WERT_ZU_TALENTE_MAPPING.get(wert_name, []):
                if talent in self.talent_increase_progress:
                    self.talent_increase_progress[talent] += points_to_add
                    points_gained = math.floor(self.talent_increase_progress[talent] / TALENT_PROGRESS_THRESHOLD)
                    if points_gained > 0:
                        increase_amount = min(points_gained, MAX_TALENTWERT - self.talentwerte[talent])
                        if increase_amount > 0:
                            self.talentwerte[talent] += increase_amount
                            self.talent_increase_progress[talent] -= increase_amount * TALENT_PROGRESS_THRESHOLD
            self.update_ui()
    
    def decrease_wert(self, wert_name):
        """Verringert den Wert eines Kopfwertes und der entsprechenden Talente."""
        points_to_remove = self.step_size
        if self.kopfwerte.get(wert_name, 0) >= points_to_remove:
            num_talents = len(WERT_ZU_TALENTE_MAPPING.get(wert_name, []))
            ap_cost = num_talents * points_to_remove
            self.available_ap += ap_cost
            self.kopfwerte[wert_name] -= points_to_remove
            
            for talent in WERT_ZU_TALENTE_MAPPING.get(wert_name, []):
                if talent in self.talent_increase_progress:
                    self.talent_increase_progress[talent] -= points_to_remove
                    if self.talent_increase_progress[talent] < 0 and self.talentwerte.get(talent, 0) > 0:
                        self.talentwerte[talent] -= 1
                        self.talent_increase_progress[talent] += TALENT_PROGRESS_THRESHOLD
            self.update_ui()

    def increase_talent(self, talent_name):
        """Erhöht den Wert eines Talents und zieht AP ab."""
        points_to_add = self.step_size
        ap_cost = AP_KOSTEN_TALENT * self.step_size
        if self.available_ap >= ap_cost and self.talentwerte.get(talent_name, 0) + points_to_add <= MAX_TALENTWERT:
            self.available_ap -= ap_cost
            self.talentwerte[talent_name] += points_to_add
            self.update_ui()
            
    def decrease_talent(self, talent_name):
        """Verringert den Wert eines Talents und fügt AP hinzu."""
        points_to_remove = self.step_size
        if self.talentwerte.get(talent_name, 0) >= points_to_remove:
            self.available_ap += AP_KOSTEN_TALENT * points_to_remove
            self.talentwerte[talent_name] -= points_to_remove
            self.update_ui()

    def go_back_to_character(self):
        """Speichert die Daten und wechselt zur Charakterseite."""
        self.save_data(switch_frame='CharakterseiteFrame')
    
    def go_to_combat_page(self):
        """Speichert die Daten und wechselt zur Kampfseite."""
        self.save_data(switch_frame='KampfseiteFrame')

    def save_data(self, switch_frame=None):
        """Speichert die Talentdaten in den Charakterdaten."""
        self.controller.current_character_data["available_ap"] = self.available_ap
        self.controller.current_character_data["kopfwerte"] = self.kopfwerte
        self.controller.current_character_data["talentwerte"] = self.talentwerte
        self.controller.current_character_data["talent_increase_progress"] = self.talent_increase_progress
        self.controller.save_character_data()
        self.show_feedback("Talente gespeichert!")

        if switch_frame:
            self.controller.show_frame(switch_frame, self.controller.current_character_data)
            
    def show_feedback(self, message):
        """Zeigt eine temporäre Feedback-Nachricht an."""
        self.feedback_label.configure(text=message, text_color="#52a67c")
        self.after(3000, lambda: self.feedback_label.configure(text=""))
