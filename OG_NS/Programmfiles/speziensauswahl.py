import customtkinter as ctk
from PIL import Image
import os
import json
from tkinter import messagebox
from global_config import get_paths

class SpezienauswahlFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#2c1e1e")
        self.controller = controller
        
        self.selected_species = None
        self.last_selected_button = None
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        top_frame = ctk.CTkFrame(master=self, fg_color="transparent")
        top_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)

        self.name_entry = ctk.CTkEntry(master=top_frame, placeholder_text="Gib deinen Namen ein...", font=("Roboto", 16))
        self.name_entry.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        self.name_entry.bind("<KeyRelease>", self.update_continue_button)

        self.continue_button = ctk.CTkButton(master=top_frame, text="Weiter", command=self.continue_program, state="disabled", font=("Cinzel", 16, "bold"), fg_color="#a67c52", hover_color="#c49a6c", text_color="black")
        self.continue_button.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="ew")

        self.species_frame = ctk.CTkScrollableFrame(master=self, label_text="Wähle deine Spezies", fg_color="#3e2b2b", label_font=("Cinzel", 20, "bold"), corner_radius=20)
        self.species_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.species_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.load_species_buttons()
    
    def load_species_buttons(self):
        """Lädt die Speziesbilder und erstellt die Buttons."""
        image_dir, _, _ = get_paths()
        species_dir_path = os.path.join(image_dir, "Spezies")
        species_files = []
        try:
            species_files = sorted([f for f in os.listdir(species_dir_path) if f.endswith(".png")])
        except FileNotFoundError:
            ctk.CTkLabel(self.species_frame, text=f"Fehler: Der Ordner '{species_dir_path}' wurde nicht gefunden.", text_color="red").pack(pady=20, padx=20)
            return

        for i, file in enumerate(species_files):
            species_name = os.path.splitext(file)[0]
            image_path = os.path.join(species_dir_path, file)
            
            try:
                species_image = ctk.CTkImage(light_image=Image.open(image_path), size=(120, 120))
            except FileNotFoundError:
                continue
                
            species_button = ctk.CTkButton(master=self.species_frame,
                                             image=species_image,
                                             text=species_name.capitalize(),
                                             compound="top",
                                             fg_color="#2b2b2b",
                                             hover_color="#454648",
                                             border_width=0,
                                             corner_radius=10,
                                             font=("Roboto", 16))
            
            species_button.configure(command=lambda name=species_name, btn=species_button: self.select_species_button(name, btn))
            row = i // 4
            col = i % 4
            species_button.grid(row=row, column=col, padx=10, pady=10, sticky="ew")

    def select_species_button(self, species_name, button):
        if self.last_selected_button:
            self.last_selected_button.configure(border_width=0)
        
        button.configure(border_color="#a67c52", border_width=3)
        self.selected_species = species_name
        self.last_selected_button = button
        self.update_continue_button()
        
    def update_continue_button(self, *args):
        if self.name_entry.get() and self.selected_species:
            self.continue_button.configure(state="normal")
        else:
            self.continue_button.configure(state="disabled")

    def continue_program(self):
        selected_name = self.name_entry.get()
        if not selected_name:
            messagebox.showerror("Fehler", "Bitte gib einen Namen ein.")
            return

        _, character_dir, template_dir = get_paths()
        template_file_path = os.path.join(template_dir, f"{self.selected_species}.json")
        try:
            with open(template_file_path, "r", encoding="utf-8") as f:
                character_data = json.load(f)
            
            character_data["Charakterdata"]["Name"] = selected_name
            # Füge den Fortschritt der Talentsteigerung hinzu
            character_data["talent_increase_progress"] = {name: 0 for name in character_data["talentwerte"].keys()}
            
            output_file_path = os.path.join(character_dir, f"{selected_name}.json")
            with open(output_file_path, "w", encoding="utf-8") as f:
                json.dump(character_data, f, indent=4)
            
            self.controller.show_frame("CharakterseiteFrame", character_data)

        except FileNotFoundError:
            messagebox.showerror("Fehler", f"Die Vorlagendatei für '{self.selected_species}' wurde nicht gefunden.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten: {e}")
