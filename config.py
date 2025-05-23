"""
Configuration centralisée du système de rédaction académique.
Contient les constantes, chemins et paramètres globaux.
"""

import os
from pathlib import Path

# Chemins des répertoires de données
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROFILES_DIR = os.path.join(DATA_DIR, "profiles")
PROJECTS_DIR = os.path.join(DATA_DIR, "projects")
HISTORY_DIR = os.path.join(DATA_DIR, "history")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
EXPORTS_DIR = os.path.join(DATA_DIR, "exports")

# Création des répertoires s'ils n'existent pas
for directory in [DATA_DIR, PROFILES_DIR, PROJECTS_DIR, HISTORY_DIR, CACHE_DIR, EXPORTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Configuration des styles d'écriture
WRITING_STYLES = {
    "Standard": {
        "description": "Style académique standard, clair et précis",
        "prompt_prefix": "Utilise un style académique standard, clair et précis."
    },
    "Académique": {
        "description": "Style académique formel avec terminologie spécialisée",
        "prompt_prefix": "Utilise un style académique formel avec terminologie spécialisée."
    },
    "CRÉSUS-NAKAMOTO": {
        "description": "Style analytique avec tensions conceptuelles et perspective historique",
        "prompt_prefix": "Utilise un style analytique avec tensions conceptuelles et perspective historique."
    },
    "AcademicWritingCrypto": {
        "description": "Style technique orienté crypto-ethnographie",
        "prompt_prefix": "Utilise un style technique orienté crypto-ethnographie."
    }
}

# Configuration des disciplines académiques
ACADEMIC_DISCIPLINES = [
    "Sciences sociales",
    "Économie",
    "Droit",
    "Informatique",
    "Autre"
]

# Configuration des styles de citation
CITATION_STYLES = {
    "APA": {
        "description": "American Psychological Association",
        "example": "Auteur, A. (Année). Titre. Source."
    },
    "MLA": {
        "description": "Modern Language Association",
        "example": "Auteur, Prénom. Titre. Source, Année."
    },
    "Chicago": {
        "description": "Chicago Manual of Style",
        "example": "Auteur, Prénom. Année. Titre. Source."
    },
    "Harvard": {
        "description": "Harvard Referencing",
        "example": "Auteur (Année) Titre, Source."
    }
}

# Configuration des modèles d'IA
AI_MODELS = {
    "gpt-4o": {
        "description": "Modèle OpenAI GPT-4o - Haute qualité, coût élevé",
        "max_tokens": 4000,
        "default_temperature": 0.7
    },
    "gpt-3.5-turbo": {
        "description": "Modèle OpenAI GPT-3.5 Turbo - Bon rapport qualité/prix",
        "max_tokens": 4000,
        "default_temperature": 0.7
    },
    "venice-large": {
        "description": "Modèle Venice Large - Alternative à OpenAI",
        "max_tokens": 4000,
        "default_temperature": 0.7
    }
}

# Configuration des statuts de projet
PROJECT_STATUSES = [
    "created",
    "storyboard_ready",
    "draft_in_progress",
    "revision_in_progress",
    "completed"
]

# Configuration de l'interface utilisateur
UI_CONFIG = {
    "theme": "light",
    "primary_color": "#1E88E5",
    "secondary_color": "#FFC107",
    "font": "sans-serif",
    "sidebar_width": 300
}

# Configuration des messages système
SYSTEM_MESSAGES = {
    "welcome": "Bienvenue dans le Système de Rédaction Académique",
    "project_created": "Projet créé avec succès!",
    "project_updated": "Projet mis à jour avec succès!",
    "project_deleted": "Projet supprimé avec succès!",
    "version_saved": "Version sauvegardée avec succès!",
    "version_restored": "Version restaurée avec succès!",
    "export_completed": "Export terminé avec succès!"
}

# Version du système
VERSION = "1.0.0"
