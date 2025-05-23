"""
Module de moteur adaptatif pour le système de rédaction académique.
Fournit des suggestions contextuelles et adapte l'expérience utilisateur.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

class AdaptiveEngine:
    """
    Moteur adaptatif qui analyse le contexte et fournit des suggestions
    personnalisées pour améliorer l'expérience de rédaction.
    """
    
    def __init__(self):
        """Initialise le moteur adaptatif."""
        self.suggestion_templates = {
            "created": [
                "Commencez par créer un storyboard pour structurer votre article.",
                "Définissez les sections principales de votre document.",
                "Établissez un plan détaillé avant de commencer la rédaction."
            ],
            "storyboard_ready": [
                "Vous avez un plan! Commencez la rédaction de l'introduction.",
                "Développez votre première section en vous basant sur le plan.",
                "Rédigez un paragraphe pour chaque point clé de votre plan."
            ],
            "draft_in_progress": [
                "Continuez la rédaction de votre brouillon.",
                "Assurez-vous que chaque section développe une idée principale.",
                "N'oubliez pas d'ajouter des transitions entre vos paragraphes."
            ],
            "revision_in_progress": [
                "Vérifiez la cohérence de votre argumentation.",
                "Assurez-vous que chaque paragraphe soutient votre thèse principale.",
                "Améliorez la clarté et la précision de votre langage."
            ],
            "completed": [
                "Exportez votre document dans le format souhaité.",
                "Vérifiez une dernière fois l'orthographe et la grammaire.",
                "Partagez votre travail ou commencez un nouveau projet."
            ]
        }
        
        self.style_suggestions = {
            "Standard": {
                "tone": "équilibré",
                "structure": "classique avec introduction, développement et conclusion",
                "examples": ["paragraphes de taille moyenne", "vocabulaire accessible"]
            },
            "Académique": {
                "tone": "formel et précis",
                "structure": "rigoureuse avec thèse, arguments et contre-arguments",
                "examples": ["citations académiques", "terminologie spécialisée"]
            },
            "CRÉSUS-NAKAMOTO": {
                "tone": "analytique et critique",
                "structure": "dialectique avec tensions conceptuelles",
                "examples": ["mise en perspective historique", "analyse multi-niveaux"]
            },
            "AcademicWritingCrypto": {
                "tone": "technique et spécialisé",
                "structure": "orientée crypto-ethnographie",
                "examples": ["références blockchain", "analyses socio-techniques"]
            }
        }
    
    def suggest_next_step(self, project_id: str, project_context=None) -> str:
        """
        Suggère la prochaine étape pour un projet en fonction de son état actuel.
        
        Args:
            project_id: ID du projet
            project_context: Instance de ProjectContext (optionnel)
            
        Returns:
            Suggestion textuelle pour la prochaine étape
        """
        # Si project_context n'est pas fourni, on l'importe ici pour éviter les imports circulaires
        if project_context is None:
            from core.project_context import ProjectContext
            project_context = ProjectContext()
        
        project = project_context.load_project(project_id)
        status = project.get("status", "created")
        
        # Sélection d'une suggestion basée sur le statut
        suggestions = self.suggestion_templates.get(status, self.suggestion_templates["created"])
        
        # Personnalisation basée sur les métadonnées du projet
        if status == "draft_in_progress":
            word_count = project.get("metadata", {}).get("word_count", 0)
            target_length = project.get("preferences", {}).get("preferred_length", 3000)
            
            if word_count < target_length * 0.25:
                return "Vous avez bien commencé! Continuez à développer vos idées principales."
            elif word_count < target_length * 0.75:
                return "Vous avancez bien. Assurez-vous d'approfondir vos arguments clés."
            else:
                return "Vous approchez de votre objectif. Pensez à préparer votre conclusion."
        
        # Rotation des suggestions pour éviter la répétition
        import random
        return random.choice(suggestions)
    
    def analyze_text_complexity(self, text: str) -> Dict[str, Any]:
        """
        Analyse la complexité d'un texte et fournit des métriques.
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dictionnaire de métriques de complexité
        """
        if not text:
            return {
                "word_count": 0,
                "avg_sentence_length": 0,
                "avg_word_length": 0,
                "complexity_score": 0
            }
        
        # Analyse basique
        words = text.split()
        word_count = len(words)
        
        # Estimation des phrases (simplifiée)
        sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
        sentence_count = max(1, len(sentences))
        
        # Calculs
        avg_sentence_length = word_count / sentence_count
        avg_word_length = sum(len(word) for word in words) / max(1, word_count)
        
        # Score de complexité (formule simplifiée)
        complexity_score = (avg_sentence_length * 0.6) + (avg_word_length * 0.4)
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": round(avg_sentence_length, 2),
            "avg_word_length": round(avg_word_length, 2),
            "complexity_score": round(complexity_score, 2)
        }
    
    def suggest_style_improvements(self, text: str, target_style: str) -> List[str]:
        """
        Suggère des améliorations de style basées sur le style cible.
        
        Args:
            text: Texte à analyser
            target_style: Style cible (Standard, Académique, etc.)
            
        Returns:
            Liste de suggestions d'amélioration
        """
        if not text:
            return ["Commencez par rédiger du contenu pour recevoir des suggestions de style."]
        
        complexity = self.analyze_text_complexity(text)
        style_info = self.style_suggestions.get(target_style, self.style_suggestions["Standard"])
        
        suggestions = []
        
        # Suggestions basées sur la complexité
        if target_style == "Académique" or target_style == "CRÉSUS-NAKAMOTO":
            if complexity["avg_sentence_length"] < 15:
                suggestions.append("Développez vos phrases pour un style plus académique.")
            if complexity["complexity_score"] < 10:
                suggestions.append(f"Augmentez la complexité de votre texte pour un style {target_style}.")
        
        elif target_style == "Standard":
            if complexity["avg_sentence_length"] > 25:
                suggestions.append("Raccourcissez vos phrases pour un style plus accessible.")
            if complexity["complexity_score"] > 15:
                suggestions.append("Simplifiez votre langage pour un style standard plus clair.")
        
        # Suggestions génériques basées sur le style
        suggestions.append(f"Adoptez un ton {style_info['tone']} pour ce style.")
        suggestions.append(f"Utilisez une structure {style_info['structure']}.")
        
        # Exemples concrets
        for example in style_info["examples"]:
            suggestions.append(f"Intégrez {example} pour renforcer ce style.")
        
        return suggestions
    
    def suggest_citations(self, text: str, discipline: str) -> List[Dict[str, str]]:
        """
        Suggère des points où des citations pourraient être nécessaires.
        
        Args:
            text: Texte à analyser
            discipline: Discipline académique
            
        Returns:
            Liste de suggestions de citations
        """
        if not text:
            return []
        
        # Mots-clés qui pourraient nécessiter une citation
        citation_triggers = {
            "Sciences sociales": ["études montrent", "recherches indiquent", "selon", "d'après", "comme l'affirme"],
            "Économie": ["théorie", "modèle", "analyse économique", "études empiriques", "données suggèrent"],
            "Droit": ["jurisprudence", "doctrine", "selon la loi", "comme l'indique", "d'après le code"],
            "Informatique": ["algorithme", "méthode", "approche", "technique", "framework"]
        }
        
        triggers = citation_triggers.get(discipline, citation_triggers["Sciences sociales"])
        
        suggestions = []
        sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
        
        for i, sentence in enumerate(sentences):
            for trigger in triggers:
                if trigger.lower() in sentence.lower() and "(" not in sentence and "[" not in sentence:
                    suggestions.append({
                        "sentence": sentence,
                        "position": i,
                        "trigger": trigger,
                        "suggestion": f"Considérez ajouter une citation pour appuyer cette affirmation."
                    })
                    break
        
        return suggestions[:5]  # Limite à 5 suggestions pour éviter la surcharge
    
    def adapt_interface(self, user_profile, project_context) -> Dict[str, Any]:
        """
        Adapte l'interface utilisateur en fonction du profil et du contexte.
        
        Args:
            user_profile: Instance de UserProfile
            project_context: Instance de ProjectContext
            
        Returns:
            Dictionnaire de paramètres d'interface adaptés
        """
        profile = user_profile.load_profile()
        preferences = profile.get("preferences", {})
        
        # Adaptation de l'interface
        interface_settings = {
            "layout": "wide" if preferences.get("preferred_length", 3000) > 5000 else "centered",
            "show_advanced_options": preferences.get("discipline") in ["Sciences sociales", "Économie"],
            "citation_panel_visible": preferences.get("citation_style") != "None",
            "suggested_tools": []
        }
        
        # Suggestions d'outils basées sur le profil
        if preferences.get("discipline") == "Sciences sociales":
            interface_settings["suggested_tools"].append({
                "name": "Analyse qualitative",
                "description": "Outils pour l'analyse de données qualitatives"
            })
        
        if preferences.get("style") == "CRÉSUS-NAKAMOTO":
            interface_settings["suggested_tools"].append({
                "name": "Générateur de tensions conceptuelles",
                "description": "Aide à formuler des tensions théoriques"
            })
        
        return interface_settings
    
    def get_learning_resources(self, topic: str, style: str) -> List[Dict[str, str]]:
        """
        Fournit des ressources d'apprentissage adaptées au sujet et au style.
        
        Args:
            topic: Sujet d'intérêt
            style: Style d'écriture
            
        Returns:
            Liste de ressources d'apprentissage
        """
        # Ressources fictives pour démonstration
        resources = [
            {
                "title": f"Guide d'écriture {style}",
                "description": f"Techniques d'écriture pour le style {style}",
                "url": f"https://example.com/writing-guides/{style.lower()}"
            },
            {
                "title": f"Exemples de {topic} en style {style}",
                "description": f"Exemples annotés de textes sur {topic}",
                "url": f"https://example.com/examples/{topic.lower()}/{style.lower()}"
            },
            {
                "title": f"Vocabulaire spécialisé: {topic}",
                "description": f"Lexique pour écrire sur {topic}",
                "url": f"https://example.com/vocabulary/{topic.lower()}"
            }
        ]
        
        return resources
