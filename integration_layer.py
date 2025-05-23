"""
Module d'intégration pour le système de rédaction académique.
Orchestre les interactions entre les différents services et modules.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

class IntegrationLayer:
    """
    Couche d'intégration qui coordonne les interactions entre les différents
    modules du système de rédaction académique.
    """
    
    def __init__(self):
        """Initialise la couche d'intégration."""
        self.registered_modules = {}
        self.event_handlers = {}
        self.service_registry = {}
        
        # Initialisation du journal d'événements
        self.event_log = []
    
    def register_module(self, module_name: str, module_instance: Any) -> None:
        """
        Enregistre un module dans la couche d'intégration.
        
        Args:
            module_name: Nom du module
            module_instance: Instance du module
        """
        self.registered_modules[module_name] = module_instance
        self.log_event("module_registered", {"module_name": module_name})
    
    def get_module(self, module_name: str) -> Optional[Any]:
        """
        Récupère un module enregistré.
        
        Args:
            module_name: Nom du module
            
        Returns:
            Instance du module ou None si non trouvé
        """
        return self.registered_modules.get(module_name)
    
    def register_service(self, service_name: str, service_function: Callable) -> None:
        """
        Enregistre un service dans la couche d'intégration.
        
        Args:
            service_name: Nom du service
            service_function: Fonction de service
        """
        self.service_registry[service_name] = service_function
        self.log_event("service_registered", {"service_name": service_name})
    
    def call_service(self, service_name: str, **kwargs) -> Any:
        """
        Appelle un service enregistré.
        
        Args:
            service_name: Nom du service
            **kwargs: Arguments du service
            
        Returns:
            Résultat du service
            
        Raises:
            ValueError: Si le service n'est pas trouvé
        """
        if service_name not in self.service_registry:
            raise ValueError(f"Service non trouvé: {service_name}")
        
        service = self.service_registry[service_name]
        self.log_event("service_called", {"service_name": service_name, "args": str(kwargs)})
        
        try:
            result = service(**kwargs)
            return result
        except Exception as e:
            self.log_event("service_error", {
                "service_name": service_name, 
                "error": str(e),
                "args": str(kwargs)
            })
            raise
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Enregistre un gestionnaire d'événements.
        
        Args:
            event_type: Type d'événement
            handler: Fonction de gestion d'événement
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
    
    def trigger_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Déclenche un événement.
        
        Args:
            event_type: Type d'événement
            event_data: Données de l'événement
        """
        self.log_event(event_type, event_data)
        
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    self.log_event("event_handler_error", {
                        "event_type": event_type,
                        "error": str(e)
                    })
    
    def log_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Enregistre un événement dans le journal.
        
        Args:
            event_type: Type d'événement
            event_data: Données de l'événement
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": event_data
        }
        
        self.event_log.append(event)
        
        # Limite la taille du journal
        if len(self.event_log) > 1000:
            self.event_log = self.event_log[-1000:]
    
    def get_event_log(self, event_type: Optional[str] = None, 
                     limit: int = 100) -> List[Dict[str, Any]]:
        """
        Récupère le journal d'événements.
        
        Args:
            event_type: Type d'événement à filtrer (optionnel)
            limit: Nombre maximum d'événements à retourner
            
        Returns:
            Liste d'événements
        """
        if event_type:
            filtered_log = [event for event in self.event_log if event["type"] == event_type]
            return filtered_log[-limit:]
        
        return self.event_log[-limit:]
    
    def coordinate_workflow(self, workflow_name: str, 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordonne un workflow entre plusieurs modules.
        
        Args:
            workflow_name: Nom du workflow
            context: Contexte du workflow
            
        Returns:
            Résultat du workflow
        """
        self.log_event("workflow_started", {
            "workflow_name": workflow_name,
            "context": {k: str(v) for k, v in context.items()}
        })
        
        result = {"status": "success", "data": {}}
        
        try:
            if workflow_name == "create_project":
                # Exemple de workflow de création de projet
                user_profile = self.get_module("user_profile")
                project_context = self.get_module("project_context")
                
                if not user_profile or not project_context:
                    raise ValueError("Modules requis non disponibles")
                
                # Création du projet
                project_id = project_context.create_project(
                    title=context.get("title", ""),
                    description=context.get("description", ""),
                    project_type=context.get("type", ""),
                    preferences=context.get("preferences", {})
                )
                
                # Mise à jour des statistiques utilisateur
                user_profile.update_statistics("projects_created")
                
                # Journalisation de l'activité
                user_profile.log_activity("create_project", {
                    "project_id": project_id,
                    "title": context.get("title", "")
                })
                
                result["data"]["project_id"] = project_id
            
            elif workflow_name == "generate_content":
                # Exemple de workflow de génération de contenu
                project_context = self.get_module("project_context")
                adaptive_engine = self.get_module("adaptive_engine")
                
                if not project_context or not adaptive_engine:
                    raise ValueError("Modules requis non disponibles")
                
                project_id = context.get("project_id")
                section_id = context.get("section_id")
                prompt = context.get("prompt", "")
                
                # Appel du service d'IA
                ai_response = self.call_service("ai_service", 
                                               prompt=prompt,
                                               max_tokens=context.get("max_tokens", 1000))
                
                # Mise à jour de la section
                if section_id:
                    project_context.update_section(
                        project_id=project_id,
                        section_id=section_id,
                        content=ai_response.get("text", "")
                    )
                else:
                    section_id = project_context.add_section(
                        project_id=project_id,
                        title=context.get("title", "Section générée"),
                        content=ai_response.get("text", "")
                    )
                
                # Mise à jour des métadonnées
                project_context.update_project_metadata(project_id)
                
                result["data"]["section_id"] = section_id
                result["data"]["content"] = ai_response.get("text", "")
                result["data"]["source"] = ai_response.get("source", "")
            
            else:
                result["status"] = "error"
                result["error"] = f"Workflow non reconnu: {workflow_name}"
        
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            
            self.log_event("workflow_error", {
                "workflow_name": workflow_name,
                "error": str(e)
            })
        
        self.log_event("workflow_completed", {
            "workflow_name": workflow_name,
            "status": result["status"]
        })
        
        return result
    
    def initialize_system(self) -> bool:
        """
        Initialise le système complet.
        
        Returns:
            True si l'initialisation a réussi, False sinon
        """
        try:
            # Import des modules core
            from core.user_profile import UserProfile
            from core.project_context import ProjectContext
            from core.adaptive_engine import AdaptiveEngine
            from core.history_manager import HistoryManager
            
            # Création des instances
            user_profile = UserProfile()
            project_context = ProjectContext()
            adaptive_engine = AdaptiveEngine()
            history_manager = HistoryManager()
            
            # Enregistrement des modules
            self.register_module("user_profile", user_profile)
            self.register_module("project_context", project_context)
            self.register_module("adaptive_engine", adaptive_engine)
            self.register_module("history_manager", history_manager)
            
            # Import et enregistrement des services
            from utils.ai_service import call_ai_safe
            
            self.register_service("ai_service", call_ai_safe)
            
            self.log_event("system_initialized", {"status": "success"})
            return True
            
        except Exception as e:
            self.log_event("initialization_error", {"error": str(e)})
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Récupère l'état actuel du système.
        
        Returns:
            État du système
        """
        return {
            "modules": list(self.registered_modules.keys()),
            "services": list(self.service_registry.keys()),
            "event_handlers": {k: len(v) for k, v in self.event_handlers.items()},
            "last_events": self.get_event_log(limit=5)
        }
