"""
Configuration globale de l'application
"""
import os

# Chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'tontine.db')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
EXPORTS_DIR = os.path.join(BASE_DIR, 'exports')
PDF_OUTPUT_DIR = os.path.join(os.path.expanduser('~'), 'Desktop', 'dcomitee')

# Application
APP_NAME = "Death Comitee"
APP_VERSION = "1.0.0"

# Base de données
DB_TIMEOUT = 30

# Interface
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FONT_FAMILY = "Arial"
FONT_SIZE = 10
FONT_SIZE_TITLE = 14
FONT_SIZE_SUBTITLE = 12

# Couleurs
COLOR_PRIMARY = "#2C3E50"
COLOR_SECONDARY = "#3498DB"
COLOR_SUCCESS = "#27AE60"
COLOR_WARNING = "#F39C12"
COLOR_DANGER = "#E74C3C"
COLOR_BG = "#ECF0F1"
COLOR_BG_DARK = "#BDC3C7"

# Formats
DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%d/%m/%Y %H:%M"
CURRENCY_SYMBOL = "€"

# Modes de paiement
PAYMENT_MODES = ["Especes", "Cheque", "Virement", "Mobile Money", "Autre"]

# Administrateurs (pour enregistrer qui fait le paiement)
ADMIN_IDS = {
    1: "Admin 1",
    2: "Admin 2",
    3: "Admin 3",
    4: "Admin 4",
    5: "Admin 5"
}

# Postes de depenses (categories de frais pour un deces)
POSTES_DEPENSES = {
    'transport_services': 'Transport / Services',
    'billet_avion': "Billet d'avion",
    'imam': 'Imam',
    'mairie': 'Mairie',
    'autre1': 'Autre 1',
    'autre2': 'Autre 2',
    'autre3': 'Autre 3'
}

# Relations (pour les deces - lien entre le defunt et l'adherent)
RELATIONS = [
    "Pere", "Mere", "Epoux/Epouse", "Fils", "Fille",
    "Frere", "Soeur", "Grand-parent", "Oncle", "Tante",
    "Cousin/Cousine", "Autre"
]

# Pagination
ITEMS_PER_PAGE = 50

# Messages
MSG_SUCCESS_CREATE = "Création réussie"
MSG_SUCCESS_UPDATE = "Mise à jour réussie"
MSG_SUCCESS_DELETE = "Suppression réussie"
MSG_ERROR_GENERIC = "Une erreur s'est produite"
MSG_CONFIRM_DELETE = "Êtes-vous sûr de vouloir supprimer cet élément ?"

# Validation
MIN_MONTANT = 0
MAX_TELEPHONE_LENGTH = 20
MAX_EMAIL_LENGTH = 100
