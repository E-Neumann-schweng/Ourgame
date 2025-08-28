import customtkinter as ctk
from PIL import Image
import os
import sys
from global_config import get_paths

class NeuAltFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#2c1e1e")
        self.controller = controller
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        image_dir, _, _ = get_paths()
        old_abenteurer_pfad = os.path.join(image_dir, "Start", "OldAbenteurer.png")
        young_abenteurer_pfad = os.path.join(image_dir, "Start", "YoungAbenteruer.png")

        try:
            self.original_old_image = Image.open(old_abenteurer_pfad)
            self.original_young_image = Image.open(young_abenteurer_pfad)
        except FileNotFoundError:
            self.original_old_image = Image.new('RGB', (200, 200), color = 'red')
            self.original_young_image = Image.new('RGB', (200, 200), color = 'blue')

        self.old_char_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.old_char_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.old_char_frame.grid_rowconfigure(0, weight=1)
        self.old_char_frame.grid_columnconfigure(0, weight=1)

        self.old_image_label = self.create_image_label(
            self.old_char_frame, self.original_old_image, self.alter_charakter_geclickt
        )
        self.old_image_label.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.old_char_frame, text="Alter Charakter", font=("Cinzel", 16, "bold"), text_color="#f0e6d2").grid(row=1, column=0, pady=(10,0))

        self.young_char_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.young_char_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.young_char_frame.grid_rowconfigure(0, weight=1)
        self.young_char_frame.grid_columnconfigure(0, weight=1)

        self.young_image_label = self.create_image_label(
            self.young_char_frame, self.original_young_image, self.neuer_charakter_geclickt
        )
        self.young_image_label.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.young_char_frame, text="Neuer Charakter", font=("Cinzel", 16, "bold"), text_color="#f0e6d2").grid(row=1, column=0, pady=(10,0))
        
        self.bind("<Configure>", self.on_resize)
        
        # Initial call to ensure correct sizing on startup
        self.after(100, self.on_resize)

    def create_image_label(self, master, image_data, command):
        image_ctk = ctk.CTkImage(light_image=image_data, size=(1, 1))
        label = ctk.CTkLabel(master, image=image_ctk, text="", fg_color="transparent", anchor="n")
        label.bind("<Button-1>", lambda event: command())
        label.bind("<Enter>", lambda event: label.configure(fg_color="#3e2b2b"))
        label.bind("<Leave>", lambda event: label.configure(fg_color="transparent"))
        label.configure(cursor="hand2")
        return label

    def alter_charakter_geclickt(self):
        self.controller.show_frame("CharakterauswahlFrame")

    def neuer_charakter_geclickt(self):
        self.controller.show_frame("SpezienauswahlFrame")

    def on_resize(self, event=None):
        if self.winfo_exists():
            self.update_image_size(self.old_image_label, self.original_old_image)
            self.update_image_size(self.young_image_label, self.original_young_image)

    def update_image_size(self, label, original_image):
        if not label.winfo_exists() or label.winfo_width() == 1 or label.winfo_height() == 1:
            return

        scaling_factor = self.winfo_toplevel()._get_window_scaling()
        physische_breite = label.winfo_width() * scaling_factor
        physische_hoehe = label.winfo_height() * scaling_factor

        if physische_breite <= 1 or physische_hoehe <= 1:
            return

        img_ratio = original_image.width / original_image.height
        btn_ratio = physische_breite / physische_hoehe

        if btn_ratio > img_ratio:
            new_height = physische_hoehe
            new_width = int(new_height * img_ratio)
        else:
            new_width = physische_breite
            new_height = int(new_width / img_ratio)
            
        if new_width <= 0 or new_height <= 0:
            return
            
        resized_pil_image = original_image.resize((int(new_width), int(new_height)), Image.Resampling.LANCZOS)
        resized_ctk_image = ctk.CTkImage(
            light_image=resized_pil_image,
            size=(new_width / scaling_factor, new_height / scaling_factor)
        )
        label.configure(image=resized_ctk_image)
