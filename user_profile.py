"""
Module de gestion du profil utilisateur.
Gère les préférences, l'historique et les données personnelles de l'utilisateur.
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import PROFILES_DIR

class UserProfile:
    """
    Classe de gestion du profil utilisateur et des préférences.
    Permet de stocker, récupérer et mettre à jour les informations utilisateur.
    """
    
    def __init__(self):
        """Initialise le gestionnaire de profil utilisateur."""
        self.profiles_dir = Path(PROFILES_DIR)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.current_profile_id = self._get_or_create_default_profile_id()
        self.profile_file = self.profiles_dir / f"{self.current_profile_id}.json"
        
        # Charge ou crée le profil
        if not self.profile_file.exists():
            self._create_default_profile()
    
    def _get_or_create_default_profile_id(self) -> str:
        """Récupère ou crée un ID de profil par défaut."""
        default_id_file = self.profiles_dir / "default_profile_id.txt"
        
        if default_id_file.exists():
            return default_id_file.read_text().strip()
        
        # Crée un nouvel ID si aucun n'existe
        profile_id = str(uuid.uuid4())
        default_id_file.write_text(profile_id)
        return profile_id
    
    def _create_default_profile(self) -> None:
        """Crée un profil utilisateur par défaut."""
        default_profile = {
            "profile_id": self.current_profile_id,
            "created_date": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "preferences": {
                "style": "Standard",
                "tone": "formel",
                "citation_style": "APA",
                "language": "Français",
                "discipline": "Sciences sociales",
                "preferred_length": 3000
            },
            "activity": [],
            "statistics": {
                "projects_created": 0,
                "drafts_completed": 0,
                "revisions_made": 0,
                "total_words_generated": 0
            }
        }
        
        with open(self.profile_file, "w", encoding="utf-8") as f:
            json.dump(default_profile, f, indent=2, ensure_ascii=False)
    
    def load_profile(self) -> Dict[str, Any]:
        """Charge le profil utilisateur actuel."""
        if not self.profile_file.exists():
            self._create_default_profile()
            
        with open(self.profile_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def save_profile(self, profile: Dict[str, Any]) -> None:
        """Sauvegarde le profil utilisateur."""
        profile["last_modified"] = datetime.now().isoformat()
        
        with open(self.profile_file, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
    
    def update_preference(self, key: str, value: Any) -> None:
        """Met à jour une préférence utilisateur spécifique."""
        profile = self.load_profile()
        profile["preferences"][key] = value
        self.save_profile(profile)
    
    def update_preferences(self, preferences: Dict[str, Any]) -> None:
        """Met à jour plusieurs préférences utilisateur."""
        profile = self.load_profile()
        profile["preferences"].update(preferences)
        self.save_profile(profile)
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Récupère une préférence utilisateur spécifique."""
        profile = self.load_profile()
        return profile["preferences"].get(key, default)
    
    def log_activity(self, action: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Enregistre une activité utilisateur dans l'historique."""
        profile = self.load_profile()
        
        activity_entry = {
            "date": datetime.now().isoformat(),
            "action": action,
            "details": details or {}
        }
        
        profile["activity"].append(activity_entry)
        
        # Limite la taille de l'historique d'activité
        if len(profile["activity"]) > 100:
            profile["activity"] = profile["activity"][-100:]
            
        self.save_profile(profile)
    
    def update_statistics(self, stat_key: str, increment: int = 1) -> None:
        """Met à jour les statistiques utilisateur."""
        profile = self.load_profile()
        
        if stat_key in profile["statistics"]:
            profile["statistics"][stat_key] += increment
            self.save_profile(profile)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques utilisateur."""
        profile = self.load_profile()
        return profile["statistics"]
    
    def reset_preferences(self) -> None:
        """Réinitialise les préférences utilisateur aux valeurs par défaut."""
        profile = self.load_profile()
        
        profile["preferences"] = {
            "style": "Standard",
            "tone": "formel",
            "citation_style": "APA",
            "language": "Français",
            "discipline": "Sciences sociales",
            "preferred_length": 3000
        }
        
        self.save_profile(profile)
    
    def export_profile(self, export_path: str) -> str:
        """Exporte le profil utilisateur vers un fichier JSON."""
        profile = self.load_profile()
        
        # Supprime les informations sensibles si nécessaire
        export_profile = profile.copy()
        
        export_file = Path(export_path) / f"profile_{self.current_profile_id}.json"
        with open(export_file, "w", encoding="utf-8") as f:
            json.dump(export_profile, f, indent=2, ensure_ascii=False)
            
        return str(export_file)
    
    def import_profile(self, import_file: str) -> bool:
        """Importe un profil utilisateur depuis un fichier JSON."""
        try:
            with open(import_file, "r", encoding="utf-8") as f:
                imported_profile = json.load(f)
            
            # Vérifie la structure minimale requise
            if "preferences" not in imported_profile:
                return False
                
            # Conserve l'ID de profil actuel
            current_profile = self.load_profile()
            imported_profile["profile_id"] = current_profile["profile_id"]
            imported_profile["last_modified"] = datetime.now().isoformat()
            
            self.save_profile(imported_profile)
            return True
            
        except (json.JSONDecodeError, FileNotFoundError):
            return False
