"""
Module de gestion du contexte de projet.
Gère le chargement, la sauvegarde et la manipulation des données de projet.
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import PROJECTS_DIR

class ProjectContext:
    """
    Classe de gestion du contexte de projet.
    Permet de stocker, récupérer et mettre à jour les informations de projet.
    """
    
    def __init__(self):
        """Initialise le gestionnaire de contexte de projet."""
        self.projects_dir = Path(PROJECTS_DIR)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
    
    def create_project(self, title: str, description: str, project_type: str, 
                      preferences: Optional[Dict[str, Any]] = None) -> str:
        """
        Crée un nouveau projet et retourne son ID.
        
        Args:
            title: Titre du projet
            description: Description du projet
            project_type: Type de projet (article, mémoire, etc.)
            preferences: Préférences spécifiques au projet
            
        Returns:
            ID du projet créé
        """
        project_id = str(uuid.uuid4())[:8]
        
        # Création du projet avec les métadonnées de base
        project = {
            "project_id": project_id,
            "title": title,
            "description": description,
            "type": project_type,
            "status": "created",
            "created_date": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "preferences": preferences or {},
            "sections": [],
            "metadata": {
                "word_count": 0,
                "revision_count": 0,
                "completion_percentage": 0
            }
        }
        
        # Sauvegarde du projet
        self.save_project(project)
        
        return project_id
    
    def get_project_file(self, project_id: str) -> Path:
        """Retourne le chemin du fichier de projet."""
        return self.projects_dir / f"{project_id}.json"
    
    def load_project(self, project_id: str) -> Dict[str, Any]:
        """
        Charge les données d'un projet.
        
        Args:
            project_id: ID du projet à charger
            
        Returns:
            Données du projet ou un projet vide si non trouvé
        """
        project_file = self.get_project_file(project_id)
        
        if project_file.exists():
            with open(project_file, "r", encoding="utf-8") as f:
                return json.load(f)
        
        # Retourne un projet vide avec l'ID spécifié si non trouvé
        return {
            "project_id": project_id,
            "title": "",
            "description": "",
            "type": "",
            "status": "created",
            "created_date": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "preferences": {},
            "sections": [],
            "metadata": {
                "word_count": 0,
                "revision_count": 0,
                "completion_percentage": 0
            }
        }
    
    def save_project(self, project: Dict[str, Any]) -> None:
        """
        Sauvegarde les données d'un projet.
        
        Args:
            project: Données du projet à sauvegarder
        """
        project_id = project.get("project_id")
        if not project_id:
            raise ValueError("Le projet doit avoir un ID valide")
        
        # Mise à jour de la date de modification
        project["last_modified"] = datetime.now().isoformat()
        
        # Sauvegarde du projet
        project_file = self.get_project_file(project_id)
        with open(project_file, "w", encoding="utf-8") as f:
            json.dump(project, f, indent=2, ensure_ascii=False)
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste de tous les projets.
        
        Returns:
            Liste des projets avec leurs métadonnées de base
        """
        projects = []
        
        for project_file in self.projects_dir.glob("*.json"):
            try:
                with open(project_file, "r", encoding="utf-8") as f:
                    project = json.load(f)
                    # Inclut seulement les métadonnées essentielles pour la liste
                    projects.append({
                        "project_id": project.get("project_id", ""),
                        "title": project.get("title", ""),
                        "description": project.get("description", ""),
                        "type": project.get("type", ""),
                        "status": project.get("status", "created"),
                        "created_date": project.get("created_date", ""),
                        "last_modified": project.get("last_modified", "")
                    })
            except (json.JSONDecodeError, IOError):
                # Ignore les fichiers corrompus
                continue
        
        # Tri par date de modification décroissante
        return sorted(projects, key=lambda x: x.get("last_modified", ""), reverse=True)
    
    def delete_project(self, project_id: str) -> bool:
        """
        Supprime un projet.
        
        Args:
            project_id: ID du projet à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        project_file = self.get_project_file(project_id)
        
        if project_file.exists():
            try:
                project_file.unlink()
                return True
            except IOError:
                return False
        
        return False
    
    def update_project_status(self, project_id: str, status: str) -> None:
        """
        Met à jour le statut d'un projet.
        
        Args:
            project_id: ID du projet
            status: Nouveau statut
        """
        project = self.load_project(project_id)
        project["status"] = status
        self.save_project(project)
    
    def add_section(self, project_id: str, title: str, content: str = "", 
                   section_type: str = "text") -> str:
        """
        Ajoute une section à un projet.
        
        Args:
            project_id: ID du projet
            title: Titre de la section
            content: Contenu de la section
            section_type: Type de section (text, code, etc.)
            
        Returns:
            ID de la section créée
        """
        section_id = str(uuid.uuid4())[:8]
        
        project = self.load_project(project_id)
        
        section = {
            "section_id": section_id,
            "title": title,
            "content": content,
            "type": section_type,
            "created_date": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "metadata": {
                "word_count": len(content.split()),
                "revision_count": 0
            }
        }
        
        project["sections"].append(section)
        self.save_project(project)
        
        return section_id
    
    def update_section(self, project_id: str, section_id: str, 
                      content: Optional[str] = None, 
                      title: Optional[str] = None) -> bool:
        """
        Met à jour une section d'un projet.
        
        Args:
            project_id: ID du projet
            section_id: ID de la section
            content: Nouveau contenu (optionnel)
            title: Nouveau titre (optionnel)
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        project = self.load_project(project_id)
        
        for section in project["sections"]:
            if section["section_id"] == section_id:
                if content is not None:
                    section["content"] = content
                    section["metadata"]["word_count"] = len(content.split())
                    section["metadata"]["revision_count"] += 1
                
                if title is not None:
                    section["title"] = title
                
                section["last_modified"] = datetime.now().isoformat()
                self.save_project(project)
                return True
        
        return False
    
    def get_section(self, project_id: str, section_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une section d'un projet.
        
        Args:
            project_id: ID du projet
            section_id: ID de la section
            
        Returns:
            Données de la section ou None si non trouvée
        """
        project = self.load_project(project_id)
        
        for section in project["sections"]:
            if section["section_id"] == section_id:
                return section
        
        return None
    
    def delete_section(self, project_id: str, section_id: str) -> bool:
        """
        Supprime une section d'un projet.
        
        Args:
            project_id: ID du projet
            section_id: ID de la section
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        project = self.load_project(project_id)
        
        for i, section in enumerate(project["sections"]):
            if section["section_id"] == section_id:
                project["sections"].pop(i)
                self.save_project(project)
                return True
        
        return False
    
    def update_project_metadata(self, project_id: str) -> None:
        """
        Met à jour les métadonnées d'un projet (comptage de mots, etc.).
        
        Args:
            project_id: ID du projet
        """
        project = self.load_project(project_id)
        
        # Calcul du nombre total de mots
        total_words = sum(section.get("metadata", {}).get("word_count", 0) 
                          for section in project["sections"])
        
        # Calcul du nombre total de révisions
        total_revisions = sum(section.get("metadata", {}).get("revision_count", 0) 
                             for section in project["sections"])
        
        # Calcul du pourcentage de complétion (basé sur le nombre de sections avec contenu)
        if project["sections"]:
            sections_with_content = sum(1 for section in project["sections"] 
                                       if section.get("content", "").strip())
            completion_percentage = (sections_with_content / len(project["sections"])) * 100
        else:
            completion_percentage = 0
        
        # Mise à jour des métadonnées
        project["metadata"] = {
            "word_count": total_words,
            "revision_count": total_revisions,
            "completion_percentage": completion_percentage
        }
        
        self.save_project(project)
    
    def export_project(self, project_id: str, export_format: str = "json") -> str:
        """
        Exporte un projet dans un format spécifique.
        
        Args:
            project_id: ID du projet
            export_format: Format d'export (json, txt, etc.)
            
        Returns:
            Chemin du fichier exporté
        """
        project = self.load_project(project_id)
        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)
        
        if export_format == "json":
            export_file = export_dir / f"{project_id}_export.json"
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(project, f, indent=2, ensure_ascii=False)
            return str(export_file)
        
        elif export_format == "txt":
            export_file = export_dir / f"{project_id}_export.txt"
            with open(export_file, "w", encoding="utf-8") as f:
                f.write(f"# {project.get('title', 'Sans titre')}\n\n")
                f.write(f"Description: {project.get('description', '')}\n\n")
                
                for section in project.get("sections", []):
                    f.write(f"## {section.get('title', 'Sans titre')}\n\n")
                    f.write(f"{section.get('content', '')}\n\n")
            
            return str(export_file)
        
        else:
            raise ValueError(f"Format d'export non supporté: {export_format}")
