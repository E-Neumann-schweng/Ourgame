import customtkinter as ctk
import os
import json
from neu_alt import NeuAltFrame
from charakterauswahl import CharakterauswahlFrame
from speziensauswahl import SpezienauswahlFrame
from charakterseite import CharakterseiteFrame
from talentseite import TalentseiteFrame
from kampfseite import KampfseiteFrame
from global_config import get_paths
from tkinter import messagebox

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Fenster-Konfiguration
        self.title("OurGame - Charakter-App")
        self.geometry("1200x800")
        
        # Farbschema, angepasst an die Charakterseite
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color="#2c1e1e")
        
        # Zentrales Datenmanagement
        self.current_character_data = {}
        
        # Frame-Container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Seiten als Frames initialisieren
        self.frames = {
            "NeuAltFrame": NeuAltFrame(parent=self.container, controller=self),
            "CharakterauswahlFrame": CharakterauswahlFrame(parent=self.container, controller=self),
            "SpezienauswahlFrame": SpezienauswahlFrame(parent=self.container, controller=self),
            "CharakterseiteFrame": CharakterseiteFrame(parent=self.container, controller=self),
            "TalentseiteFrame": TalentseiteFrame(parent=self.container, controller=self),
            "KampfseiteFrame": KampfseiteFrame(parent=self.container, controller=self),
        }
        
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("NeuAltFrame")
    
    def show_frame(self, page_name, character_data=None):
        """Zeigt den angeforderten Frame an und übergibt die Daten."""
        if character_data:
            self.current_character_data = character_data
            # Lade Daten für die entsprechenden Seiten
            if page_name in ["CharakterseiteFrame", "TalentseiteFrame", "KampfseiteFrame"]:
                self.frames[page_name].load_character_data(self.current_character_data)
        
        frame = self.frames[page_name]
        frame.tkraise()
        # Spezieller Aufruf, um die Charakterliste zu aktualisieren, falls wir zur Charakterauswahl zurückkehren
        if page_name == "CharakterauswahlFrame":
            frame.load_character_list()
        # Rufe on_resize auf, um die Bilder korrekt zu skalieren
        if page_name == "NeuAltFrame":
            frame.on_resize()

    def update_character_data(self, data):
        """Aktualisiert die globalen Charakterdaten."""
        self.current_character_data = data
        
    def save_character_data(self):
        """Speichert die aktuellen Charakterdaten in eine JSON-Datei."""
        if not self.current_character_data:
            return
            
        _, character_dir, _ = get_paths()
        char_name = self.current_character_data["Charakterdata"]["Name"]
        output_file_path = os.path.join(character_dir, f"{char_name}.json")
        
        try:
            with open(output_file_path, "w", encoding="utf-8") as f:
                json.dump(self.current_character_data, f, indent=4)
        except IOError as e:
            print(f"Fehler beim Speichern der Datei: {e}")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
