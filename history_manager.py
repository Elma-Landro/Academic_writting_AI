"""
Module de gestion de l'historique des actions et versions.
Permet de suivre les modifications apportées aux projets et de restaurer des versions antérieures.
"""

import os
import json
import uuid
import difflib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import HISTORY_DIR

class HistoryManager:
    """
    Classe de gestion de l'historique des projets.
    Enregistre les actions, les versions et permet la restauration.
    """
    
    def __init__(self):
        """Initialise le gestionnaire d'historique."""
        self.history_dir = Path(HISTORY_DIR)
        self.history_dir.mkdir(parents=True, exist_ok=True)
    
    def get_project_history_file(self, project_id: str) -> Path:
        """Retourne le chemin du fichier d'historique pour un projet."""
        return self.history_dir / f"{project_id}_history.jsonl"
    
    def log_action(self, project_id: str, action_type: str, 
                  details: Optional[Dict[str, Any]] = None, 
                  user: str = "system") -> None:
        """
        Enregistre une action dans l'historique du projet.
        
        Args:
            project_id: ID du projet
            action_type: Type d'action (e.g., 'create_project', 'update_section')
            details: Détails de l'action
            user: Utilisateur ayant effectué l'action
        """
        history_file = self.get_project_history_file(project_id)
        
        log_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "type": "action",
            "action_type": action_type,
            "user": user,
            "details": details or {}
        }
        
        with open(history_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def save_version(self, project_id: str, project_data: Dict[str, Any], 
                     description: str = "Version automatique", 
                     user: str = "system") -> Optional[str]:
        """
        Sauvegarde une version complète du projet dans l'historique.
        Calcule les différences par rapport à la version précédente.
        
        Args:
            project_id: ID du projet
            project_data: Données complètes du projet
            description: Description de la version
            user: Utilisateur ayant sauvegardé la version
            
        Returns:
            ID de la version sauvegardée ou None si aucune modification
        """
        history_file = self.get_project_history_file(project_id)
        
        # Récupère la dernière version sauvegardée
        last_version_data = self._get_last_version_data(project_id)
        
        # Convertit les données actuelles et précédentes en JSON pour comparaison
        current_data_str = json.dumps(project_data, sort_keys=True, indent=2)
        last_data_str = json.dumps(last_version_data, sort_keys=True, indent=2) if last_version_data else ""
        
        # Ne sauvegarde pas si aucune modification
        if current_data_str == last_data_str:
            return None
            
        # Calcule les différences
        diff = list(difflib.unified_diff(
            last_data_str.splitlines(keepends=True),
            current_data_str.splitlines(keepends=True),
            fromfile="previous_version",
            tofile="current_version",
            lineterm=""
        ))
        
        version_id = str(uuid.uuid4())
        
        log_entry = {
            "id": version_id,
            "timestamp": datetime.now().isoformat(),
            "type": "version",
            "user": user,
            "description": description,
            "diff": "".join(diff),
            "full_data": project_data  # Stocke la version complète
        }
        
        with open(history_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
        return version_id
        
    def _get_last_version_data(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les données complètes de la dernière version sauvegardée."""
        history_file = self.get_project_history_file(project_id)
        last_version = None
        
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                for line in reversed(f.readlines()):
                    try:
                        entry = json.loads(line)
                        if entry.get("type") == "version" and "full_data" in entry:
                            last_version = entry["full_data"]
                            break
                    except json.JSONDecodeError:
                        continue
        return last_version

    def get_project_history(self, project_id: str, 
                           event_type: Optional[str] = None, 
                           limit: int = 50) -> List[Dict[str, Any]]:
        """
        Récupère l'historique d'un projet.
        
        Args:
            project_id: ID du projet
            event_type: Type d'événement à filtrer ('action' ou 'version')
            limit: Nombre maximum d'entrées à retourner
            
        Returns:
            Liste des entrées d'historique
        """
        history_file = self.get_project_history_file(project_id)
        history = []
        
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
                for line in reversed(lines):
                    if len(history) >= limit:
                        break
                    try:
                        entry = json.loads(line)
                        # Ne pas inclure les données complètes dans la liste d'historique
                        if "full_data" in entry:
                            del entry["full_data"]
                            
                        if event_type is None or entry.get("type") == event_type:
                            history.append(entry)
                    except json.JSONDecodeError:
                        continue
                        
        return history

    def get_version_data(self, project_id: str, version_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les données complètes d'une version spécifique.
        
        Args:
            project_id: ID du projet
            version_id: ID de la version
            
        Returns:
            Données complètes de la version ou None si non trouvée
        """
        history_file = self.get_project_history_file(project_id)
        
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("id") == version_id and entry.get("type") == "version":
                            return entry.get("full_data")
                    except json.JSONDecodeError:
                        continue
        return None

    def restore_version(self, project_id: str, version_id: str) -> bool:
        """
        Restaure un projet à une version spécifique.
        Cela implique de remplacer le fichier de projet actuel par les données de la version.
        
        Args:
            project_id: ID du projet
            version_id: ID de la version à restaurer
            
        Returns:
            True si la restauration a réussi, False sinon
        """
        version_data = self.get_version_data(project_id, version_id)
        
        if not version_data:
            return False
            
        try:
            # Import ProjectContext ici pour éviter les imports circulaires
            from core.project_context import ProjectContext
            project_context = ProjectContext()
            
            # Sauvegarde les données de la version restaurée comme projet actuel
            project_context.save_project(version_data)
            
            # Log l'action de restauration
            self.log_action(project_id, "restore_version", {"version_id": version_id})
            
            # Sauvegarde une nouvelle version après restauration
            self.save_version(project_id, version_data, 
                              description=f"Restauré depuis la version {version_id[:8]}")
                              
            return True
            
        except Exception as e:
            # Log l'erreur
            self.log_action(project_id, "restore_error", {"version_id": version_id, "error": str(e)})
            return False

    def compare_versions(self, project_id: str, version1_id: str, version2_id: str) -> Optional[str]:
        """
        Compare deux versions d'un projet et retourne les différences.
        
        Args:
            project_id: ID du projet
            version1_id: ID de la première version
            version2_id: ID de la seconde version
            
        Returns:
            Différences au format unified diff ou None si une version est manquante
        """
        data1 = self.get_version_data(project_id, version1_id)
        data2 = self.get_version_data(project_id, version2_id)
        
        if data1 is None or data2 is None:
            return None
            
        data1_str = json.dumps(data1, sort_keys=True, indent=2)
        data2_str = json.dumps(data2, sort_keys=True, indent=2)
        
        diff = list(difflib.unified_diff(
            data1_str.splitlines(keepends=True),
            data2_str.splitlines(keepends=True),
            fromfile=f"version_{version1_id[:8]}",
            tofile=f"version_{version2_id[:8]}",
            lineterm=""
        ))
        
        return "".join(diff)

    def clear_history(self, project_id: str, keep_last_n: int = 0) -> bool:
        """
        Nettoie l'historique d'un projet, en conservant éventuellement les N dernières versions.
        
        Args:
            project_id: ID du projet
            keep_last_n: Nombre de dernières versions à conserver (0 pour tout supprimer)
            
        Returns:
            True si le nettoyage a réussi, False sinon
        """
        history_file = self.get_project_history_file(project_id)
        
        if not history_file.exists():
            return True # Rien à nettoyer
            
        try:
            if keep_last_n <= 0:
                history_file.unlink()
            else:
                history = []
                with open(history_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            history.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
                
                # Garde les N dernières versions et les actions associées
                versions_to_keep = [entry for entry in history if entry.get("type") == "version"][-keep_last_n:]
                actions_to_keep = [entry for entry in history if entry.get("type") == "action"]
                
                kept_history = sorted(versions_to_keep + actions_to_keep, key=lambda x: x["timestamp"])
                
                with open(history_file, "w", encoding="utf-8") as f:
                    for entry in kept_history:
                        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                        
            self.log_action(project_id, "clear_history", {"kept_versions": keep_last_n})
            return True
            
        except Exception as e:
            self.log_action(project_id, "clear_history_error", {"error": str(e)})
            return False
