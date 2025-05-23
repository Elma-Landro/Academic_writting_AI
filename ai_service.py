import os
import openai
import json
import time
from typing import Dict, Any, Optional, List, Union

from utils.cache import DiskCache

# Configuration du cache
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "cache")
ai_cache = DiskCache(CACHE_DIR)

def call_ai_safe(prompt: str, 
                max_tokens: int = 1000, 
                temperature: float = 0.7,
                model: str = "gpt-4o",
                use_cache: bool = True) -> Dict[str, Any]:
    """
    Appelle l'API OpenAI avec gestion des erreurs et cache.
    
    Args:
        prompt: Texte du prompt
        max_tokens: Nombre maximum de tokens dans la réponse
        temperature: Température (créativité) de la réponse
        model: Modèle à utiliser
        use_cache: Utiliser le cache pour les requêtes identiques
        
    Returns:
        Dictionnaire contenant la réponse et les métadonnées
    """
    # Clé de cache basée sur les paramètres de la requête
    cache_key = f"{prompt}|{max_tokens}|{temperature}|{model}"
    
    # Vérifier si la réponse est dans le cache
    if use_cache and cache_key in ai_cache:
        cached_response = ai_cache[cache_key]
        cached_response["source"] = "cache"
        return cached_response
    
    # Configuration de l'API OpenAI
    try:
        openai.api_key = os.environ.get("OPENAI_API_KEY", "")
        
        # Tentative avec OpenAI
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            result = {
                "text": response.choices[0].message.content,
                "model": model,
                "tokens": response.usage.total_tokens,
                "source": "openai"
            }
            
            # Mise en cache de la réponse
            if use_cache:
                ai_cache[cache_key] = result
                
            return result
            
        except Exception as openai_error:
            # Fallback vers Venice API si OpenAI échoue
            try:
                # Configuration de l'API Venice (fictive pour l'exemple)
                venice_api_key = os.environ.get("VENICE_API_KEY", "")
                
                # Simulation d'un appel à une API alternative
                time.sleep(1)  # Simuler un délai réseau
                
                # Réponse fictive pour l'exemple
                fallback_response = {
                    "text": f"[Réponse de secours] {prompt[:50]}...",
                    "model": "venice-large",
                    "tokens": len(prompt.split()) * 2,  # Estimation grossière
                    "source": "venice_fallback"
                }
                
                # Mise en cache de la réponse de secours
                if use_cache:
                    ai_cache[cache_key] = fallback_response
                    
                return fallback_response
                
            except Exception as venice_error:
                # Si les deux API échouent, retourner une erreur
                return {
                    "text": "Désolé, je ne peux pas traiter cette demande pour le moment.",
                    "error": f"OpenAI: {str(openai_error)}; Venice: {str(venice_error)}",
                    "source": "error"
                }
    
    except Exception as e:
        # Erreur générale (clé API manquante, etc.)
        return {
            "text": "Erreur de configuration du service IA.",
            "error": str(e),
            "source": "config_error"
        }

def generate_academic_text(prompt: str, style: str = "Standard", 
                          length: int = 1000) -> Dict[str, Any]:
    """
    Génère un texte académique avec un style spécifique.
    
    Args:
        prompt: Description du texte à générer
        style: Style académique (Standard, CRÉSUS-NAKAMOTO, etc.)
        length: Longueur approximative en tokens
        
    Returns:
        Dictionnaire contenant le texte généré et les métadonnées
    """
    # Adaptation du prompt en fonction du style
    style_instructions = {
        "Standard": "Utilise un style académique standard, clair et précis.",
        "Académique": "Utilise un style académique formel avec terminologie spécialisée.",
        "CRÉSUS-NAKAMOTO": "Utilise un style analytique avec tensions conceptuelles et perspective historique.",
        "AcademicWritingCrypto": "Utilise un style technique orienté crypto-ethnographie."
    }
    
    instruction = style_instructions.get(style, style_instructions["Standard"])
    
    enhanced_prompt = f"""
    {instruction}
    
    Génère un texte académique sur le sujet suivant:
    {prompt}
    
    Le texte doit être structuré, rigoureux et d'une longueur d'environ {length} mots.
    """
    
    # Appel à l'API avec le prompt enrichi
    result = call_ai_safe(
        prompt=enhanced_prompt,
        max_tokens=min(length * 2, 4000),  # Limite de sécurité
        temperature=0.7 if style == "Standard" else 0.8,
        model="gpt-4o"
    )
    
    # Ajout des métadonnées de style
    result["style"] = style
    result["requested_length"] = length
    
    return result

def analyze_text_structure(text: str) -> Dict[str, Any]:
    """
    Analyse la structure d'un texte académique.
    
    Args:
        text: Texte à analyser
        
    Returns:
        Dictionnaire contenant l'analyse structurelle
    """
    analysis_prompt = f"""
    Analyse la structure du texte académique suivant et identifie:
    1. Les sections principales
    2. La thèse ou argument central
    3. Les points forts et faibles de la structure
    4. Suggestions d'amélioration structurelle
    
    Texte à analyser:
    {text[:4000]}  # Limite pour éviter de dépasser les contraintes de tokens
    """
    
    result = call_ai_safe(
        prompt=analysis_prompt,
        max_tokens=1500,
        temperature=0.3,  # Température basse pour une analyse plus factuelle
        model="gpt-4o"
    )
    
    return result
