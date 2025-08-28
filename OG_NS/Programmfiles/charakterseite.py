import customtkinter as ctk
from PIL import Image
import os
import json
from tkinter import filedialog, messagebox
from global_config import get_paths

class CharakterseiteFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#2c1e1e")
        self.controller = controller
        
        # UI-Elemente
        self.input_fields = {}
        
        # Layout
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.create_widgets()
        
        # UI-Elemente für das Feedback
        self.feedback_label = ctk.CTkLabel(self, text="", font=("Roboto", 12), text_color="#52a67c")
        self.feedback_label.grid(row=2, column=0, columnspan=2, pady=(0, 10))

    def create_widgets(self):
        # Oberer Bereich mit Portrait + Titel
        top_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#3e2b2b", border_color="#a67c52", border_width=2)
        top_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        top_frame.grid_columnconfigure(0, weight=0)
        top_frame.grid_columnconfigure(1, weight=1)

        self.image_label = ctk.CTkLabel(master=top_frame, text="📜 Kein Portrait", font=("Cinzel", 14, "bold"), text_color="#d4c59a", anchor="center", width=200, height=200)
        self.image_label.grid(row=0, column=0, padx=20, pady=20, sticky="n")

        upload_button = ctk.CTkButton(master=top_frame, text="Portrait hochladen", command=self.upload_image, font=("Cinzel", 12, "bold"), fg_color="#a67c52", hover_color="#c49a6c", corner_radius=12, text_color="black")
        upload_button.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.title_label = ctk.CTkLabel(master=top_frame, text="Charakterdetails", font=("Cinzel", 28, "bold"), text_color="#f5deb3")
        self.title_label.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="w")
        
        # Bereich für Eingaben
        form_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#3e2b2b", border_color="#a67c52", border_width=2)
        form_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")
        form_frame.grid_columnconfigure((0, 1), weight=1)

        self.create_input_field(form_frame, "Name", 0, 0)
        self.create_input_field(form_frame, "Beruf", 0, 1)
        self.create_input_field(form_frame, "Spezies", 1, 0, readonly=True)
        self.create_input_field(form_frame, "Haarfarbe", 1, 1)
        self.create_input_field(form_frame, "Alter", 2, 0)
        self.create_input_field(form_frame, "Geburtsort", 2, 1)
        self.create_input_field(form_frame, "Geschlecht", 3, 0)
        self.create_input_field(form_frame, "Körpergröße", 3, 1)
        self.create_input_field(form_frame, "Gewicht", 4, 0)

        # Buttons für Navigation und Speichern
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 10), sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2), weight=1) # Dritte Spalte für neuen Button

        to_talents_button = ctk.CTkButton(master=button_frame, text="Talente bearbeiten", command=self.go_to_talents, font=("Cinzel", 16, "bold"), fg_color="#a67c52", hover_color="#c49a6c", corner_radius=12, text_color="black")
        to_talents_button.grid(row=0, column=0, padx=10, sticky="ew")
        
        to_combat_button = ctk.CTkButton(master=button_frame, text="Kampfseite", command=self.go_to_combat_page, font=("Cinzel", 16, "bold"), fg_color="#a67c52", hover_color="#c49a6c", corner_radius=12, text_color="black")
        to_combat_button.grid(row=0, column=1, padx=10, sticky="ew")
        
        save_button = ctk.CTkButton(master=button_frame, text="Charakter speichern", command=self.save_data, font=("Cinzel", 16, "bold"), fg_color="#52a67c", hover_color="#6cc49a", corner_radius=12, text_color="black")
        save_button.grid(row=0, column=2, padx=10, sticky="ew")

    def create_input_field(self, parent_frame, label_text, row_index, col_index, readonly=False):
        input_frame = ctk.CTkFrame(master=parent_frame, fg_color="transparent")
        input_frame.grid(row=row_index, column=col_index, padx=20, pady=8, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)

        label = ctk.CTkLabel(master=input_frame, text=f"{label_text}:", font=("Roboto", 14), text_color="#f0e6d2", anchor="w")
        label.grid(row=0, column=0, padx=(0, 10), sticky="w")

        entry = ctk.CTkEntry(master=input_frame, placeholder_text=label_text, corner_radius=10, border_color="#a67c52", border_width=2, font=("Roboto", 14))
        entry.grid(row=0, column=1, sticky="ew")
        self.input_fields[label_text] = entry
        
        if readonly:
            entry.configure(state="disabled")

    def load_character_data(self, data):
        """Lädt die übergebenen Charakterdaten in die Eingabefelder und das Portrait."""
        self.controller.update_character_data(data)
        char_data = data.get("Charakterdata", {})
        for key, entry in self.input_fields.items():
            value = char_data.get(key, "")
            entry.configure(state="normal") # Enable for loading
            entry.delete(0, "end")
            entry.insert(0, value)
            if key == "Spezies": # Re-disable Spezies field
                entry.configure(state="disabled")
        
        portrait_path = data.get("portrait_path", None)
        if portrait_path and os.path.exists(portrait_path):
            try:
                pil_image = Image.open(portrait_path)
                pil_image.thumbnail((200, 200), Image.Resampling.LANCZOS)
                self.charakter_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(pil_image.width, pil_image.height))
                self.image_label.configure(image=self.charakter_image, text="")
            except Exception:
                self.image_label.configure(text="❌ Fehler beim Laden")
        else:
            self.image_label.configure(image=None, text="📜 Kein Portrait")
            

    def upload_image(self):
        image_path = filedialog.askopenfilename(title="Bild für Charakter auswählen", filetypes=[("Bilddateien", "*.png *.jpg *.jpeg *.gif")])
        if image_path:
            try:
                pil_image = Image.open(image_path)
                pil_image.thumbnail((200, 200), Image.Resampling.LANCZOS)
                self.charakter_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(pil_image.width, pil_image.height))
                self.image_label.configure(image=self.charakter_image, text="")
                self.controller.current_character_data["portrait_path"] = image_path
                self.show_feedback("Portrait erfolgreich hochgeladen!")
            except Exception:
                messagebox.showerror("Fehler", "Fehler beim Laden des Bildes.")

    def go_to_talents(self):
        self.save_data(switch_frame='TalentseiteFrame')
        
    def go_to_combat_page(self):
        """Speichert die Daten und wechselt zur Kampfseite."""
        self.save_data(switch_frame='KampfseiteFrame')
        
    def save_data(self, switch_frame=None):
        """Speichert die Daten aus den Eingabefeldern in den Charakterdaten."""
        for key, entry in self.input_fields.items():
            value = entry.get()
            if key == "Spezies":
                # Do not change Spezies
                pass
            else:
                self.controller.current_character_data["Charakterdata"][key] = value
        
        self.controller.save_character_data()
        self.show_feedback("Charakter gespeichert!")

        if switch_frame:
            self.controller.show_frame(switch_frame, self.controller.current_character_data)
            
    def show_feedback(self, message):
        """Zeigt eine temporäre Feedback-Nachricht an."""
        self.feedback_label.configure(text=message, text_color="#52a67c")
        self.after(3000, lambda: self.feedback_label.configure(text=""))
