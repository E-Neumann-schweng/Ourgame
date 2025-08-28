# ======================================================================
# Globale Konfiguration für OurGame
# ======================================================================
import os

# Maximale Werte für die Charakter-Attribute
MAX_KOPFWERT = 65
MAX_TALENTWERT = 70

# Kosten für das Steigern von Werten
AP_KOSTEN_TALENT = 1
# Die erforderliche Anzahl an Kopfwert-Steigerungen für 1 Punkt im Talent
TALENT_PROGRESS_THRESHOLD = 2

# Zuordnung von Kopfwerten zu Talentwerten
WERT_ZU_TALENTE_MAPPING = {
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
TALENT_GRUPPEN = {
    "Körperliche Talente": ["Jagen", "Körperbeherrschung", "Kraftakt", "Schwimmen", "Fesseln", "Klettern", "Verbergen", "Taschendiebstahl", "Schlösserknacken"],
    "Gesellschaftstalente": ["Überreden", "Menschenkenntnis", "Ablenkung", "Einschüchtern", "Betören", "Handel"],
    "Wissens-/Handwerkstalente": ["Pflanzenkunde", "Sammeln", "Tierkunde", "Wildniskunde", "Kriegskunst", "Handwerk", "Lebensmittelbearbeitung", "Alchemie"],
    "Geistige Talente": ["Selbstbeherrschung", "Wahrnehmung", "Gassenwissen", "Orientierung", "Magiekunde", "Sagen und legenden", "Heilkunde", "Götter und Kulte", "Geistesblitz", "Zechen"]
}

def get_paths():
    """Gibt die korrekten Pfade für die Ressourcen zurück."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        script_dir = os.getcwd()
    
    image_dir = os.path.join(script_dir, "..", "Bilder")
    character_dir = os.path.join(script_dir, "..", "Charaktere")
    template_dir = os.path.join(script_dir, "..", "Vorlagen")
    
    return image_dir, character_dir, template_dir

# --- Farbkonfiguration basierend auf Talentseite ---
THEME_COLORS = {
    "background": "#2c1e1e",
    "frame_bg": "#3e2b2b",
    "card_bg": "#2b2b2b",
    "border": "#a67c52",
    "border_dark": "#555555",
    "button_main": "#a67c52",
    "button_hover": "#c49a6c",
    "button_success": "#52a67c",
    "button_success_hover": "#6cc49a",
    "text_accent": "#d4c59a",
    "text_main": "#f0e6d2",
    "text_light": "white",
    "text_dark": "black",
}

# Stat-Farben, angepasst an das neue Theme
STAT_COLORS = {
    "Angriff": ("#b33939", "#d45858"),
    "Verteidigung": ("#316b8b", "#588fa8"),
    "Mana": ("#7a52a8", "#9973c1"),
    "Leer": ("#2b2b2b", "#555555"),
    "Selected": "#a67c52"
}

# --- Konfiguration ---
MAX_SIDES_ON_DIE = 10
FILLABLE_SIDES = 6
STAT_TYPES = ["Angriff", "Verteidigung", "Mana"]
