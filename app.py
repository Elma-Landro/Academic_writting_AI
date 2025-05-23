import streamlit as st
import os
import uuid
from datetime import datetime

from utils.common import sidebar
from core.integration_layer import IntegrationLayer
from core.user_profile import UserProfile
from core.project_context import ProjectContext
from core.adaptive_engine import AdaptiveEngine
from core.history_manager import HistoryManager

from modules.storyboard import render_storyboard
from modules.redaction import render_redaction
from modules.revision import render_revision
from modules.finalisation import render_finalisation

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Système de Rédaction Académique",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation des variables de session
if "page" not in st.session_state:
    st.session_state.page = "home"
    
if "current_project_id" not in st.session_state:
    st.session_state.current_project_id = None

# Initialisation du système
@st.cache_resource
def initialize_system():
    """Initialise le système et retourne les composants principaux."""
    integration_layer = IntegrationLayer()
    integration_layer.initialize_system()
    
    user_profile = integration_layer.get_module("user_profile")
    project_context = integration_layer.get_module("project_context")
    adaptive_engine = integration_layer.get_module("adaptive_engine")
    history_manager = integration_layer.get_module("history_manager")
    
    return integration_layer, user_profile, project_context, adaptive_engine, history_manager

# Récupération des composants du système
integration_layer, user_profile, project_context, adaptive_engine, history_manager = initialize_system()

# Récupération de la liste des projets
projects = project_context.get_all_projects()

# Affichage de la barre latérale
sidebar(projects, st.session_state.current_project_id)

# Gestion des différentes pages
if st.session_state.page == "home":
    st.title("Bienvenue dans le Système de Rédaction Académique")
    
    st.markdown("""
    Ce système vous aide à structurer, rédiger et réviser vos textes académiques
    en suivant un workflow optimisé et en utilisant des techniques d'IA avancées.
    
    ### Pour commencer:
    
    1. Créez un nouveau projet en cliquant sur "➕ Nouveau projet" dans la barre latérale
    2. Définissez le storyboard de votre article
    3. Rédigez chaque section en suivant le plan
    4. Révisez et améliorez votre texte
    5. Finalisez et exportez votre document
    
    ### Fonctionnalités principales:
    
    - **Storyboard Engine**: Structuration narrative et organisation des idées
    - **Agent de Déploiement Théorique**: Rédaction assistée par IA
    - **Module de Révision**: Amélioration du style et de la cohérence
    - **Finalisation**: Export dans différents formats (PDF, DOCX, etc.)
    """)
    
    # Affichage des projets récents
    if projects:
        st.subheader("Projets récents")
        
        # Création de colonnes pour afficher les projets
        cols = st.columns(3)
        
        for i, project in enumerate(projects[:6]):  # Limite à 6 projets récents
            with cols[i % 3]:
                st.markdown(f"**{project.get('title', 'Sans titre')}**")
                st.caption(f"Dernière modification: {project.get('last_modified', '')[:10]}")
                st.caption(f"Type: {project.get('type', 'Non spécifié')}")
                
                if st.button("Ouvrir", key=f"open_{project.get('project_id', '')}"):
                    st.session_state.current_project_id = project.get("project_id", "")
                    st.session_state.page = "project_overview"
                    st.rerun()
    
elif st.session_state.page == "new_project":
    st.title("Créer un nouveau projet")
    
    # Formulaire de création de projet
    with st.form("new_project_form"):
        title = st.text_input("Titre du projet")
        description = st.text_area("Description")
        
        project_type = st.selectbox(
            "Type de projet",
            ["Article académique", "Mémoire", "Thèse", "Rapport de recherche", "Autre"]
        )
        
        style = st.selectbox(
            "Style d'écriture",
            ["Standard", "Académique", "CRÉSUS-NAKAMOTO", "AcademicWritingCrypto"]
        )
        
        discipline = st.selectbox(
            "Discipline",
            ["Sciences sociales", "Économie", "Droit", "Informatique", "Autre"]
        )
        
        preferred_length = st.slider(
            "Longueur cible (mots)",
            min_value=1000,
            max_value=20000,
            value=5000,
            step=1000
        )
        
        submitted = st.form_submit_button("Créer le projet")
        
        if submitted:
            if not title:
                st.error("Le titre est obligatoire.")
            else:
                # Création du projet
                preferences = {
                    "style": style,
                    "discipline": discipline,
                    "preferred_length": preferred_length
                }
                
                project_id = project_context.create_project(
                    title=title,
                    description=description,
                    project_type=project_type,
                    preferences=preferences
                )
                
                # Mise à jour des statistiques utilisateur
                user_profile.update_statistics("projects_created")
                
                # Journalisation de l'activité
                user_profile.log_activity("create_project", {
                    "project_id": project_id,
                    "title": title
                })
                
                # Sauvegarde de la première version dans l'historique
                project_data = project_context.load_project(project_id)
                history_manager.save_version(
                    project_id=project_id,
                    project_data=project_data,
                    description="Création du projet"
                )
                
                # Redirection vers la page du projet
                st.session_state.current_project_id = project_id
                st.session_state.page = "project_overview"
                st.success("Projet créé avec succès!")
                st.rerun()

elif st.session_state.page == "project_overview":
    # Vérification qu'un projet est sélectionné
    if not st.session_state.current_project_id:
        st.error("Aucun projet sélectionné.")
        st.session_state.page = "home"
        st.rerun()
    
    # Chargement des données du projet
    project = project_context.load_project(st.session_state.current_project_id)
    
    # Affichage des informations du projet
    st.title(project.get("title", "Sans titre"))
    st.caption(f"ID: {project.get('project_id', '')}")
    
    # Affichage des métadonnées
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Mots", project.get("metadata", {}).get("word_count", 0))
    
    with col2:
        st.metric("Révisions", project.get("metadata", {}).get("revision_count", 0))
    
    with col3:
        st.metric("Complétion", f"{project.get('metadata', {}).get('completion_percentage', 0):.1f}%")
    
    # Description du projet
    st.subheader("Description")
    st.write(project.get("description", "Aucune description."))
    
    # Suggestion du moteur adaptatif
    suggestion = adaptive_engine.suggest_next_step(
        project_id=st.session_state.current_project_id,
        project_context=project_context
    )
    
    st.info(f"💡 **Suggestion**: {suggestion}")
    
    # Sections du projet
    st.subheader("Sections")
    
    if not project.get("sections"):
        st.write("Aucune section n'a encore été créée.")
        
        if st.button("Commencer le storyboard"):
            st.session_state.page = "storyboard"
            st.rerun()
    else:
        # Affichage des sections existantes
        for i, section in enumerate(project.get("sections", [])):
            with st.expander(f"{i+1}. {section.get('title', 'Sans titre')}"):
                st.write(section.get("content", ""))
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Éditer", key=f"edit_{section.get('section_id', '')}"):
                        st.session_state.current_section_id = section.get("section_id", "")
                        st.session_state.page = "redaction"
                        st.rerun()
                
                with col2:
                    if st.button("Réviser", key=f"revise_{section.get('section_id', '')}"):
                        st.session_state.current_section_id = section.get("section_id", "")
                        st.session_state.page = "revision"
                        st.rerun()
    
    # Boutons d'action
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Storyboard"):
            st.session_state.page = "storyboard"
            st.rerun()
    
    with col2:
        if st.button("Rédaction"):
            st.session_state.page = "redaction"
            st.rerun()
    
    with col3:
        if st.button("Révision"):
            st.session_state.page = "revision"
            st.rerun()
    
    with col4:
        if st.button("Finalisation"):
            st.session_state.page = "finalisation"
            st.rerun()

elif st.session_state.page == "storyboard":
    # Vérification qu'un projet est sélectionné
    if not st.session_state.current_project_id:
        st.error("Aucun projet sélectionné.")
        st.session_state.page = "home"
        st.rerun()
    
    # Rendu du module de storyboard
    render_storyboard(
        project_id=st.session_state.current_project_id,
        project_context=project_context,
        history_manager=history_manager,
        adaptive_engine=adaptive_engine
    )

elif st.session_state.page == "redaction":
    # Vérification qu'un projet est sélectionné
    if not st.session_state.current_project_id:
        st.error("Aucun projet sélectionné.")
        st.session_state.page = "home"
        st.rerun()
    
    # Rendu du module de rédaction
    render_redaction(
        project_id=st.session_state.current_project_id,
        section_id=st.session_state.get("current_section_id"),
        project_context=project_context,
        history_manager=history_manager,
        adaptive_engine=adaptive_engine,
        integration_layer=integration_layer
    )

elif st.session_state.page == "revision":
    # Vérification qu'un projet est sélectionné
    if not st.session_state.current_project_id:
        st.error("Aucun projet sélectionné.")
        st.session_state.page = "home"
        st.rerun()
    
    # Rendu du module de révision
    render_revision(
        project_id=st.session_state.current_project_id,
        section_id=st.session_state.get("current_section_id"),
        project_context=project_context,
        history_manager=history_manager,
        adaptive_engine=adaptive_engine,
        integration_layer=integration_layer
    )

elif st.session_state.page == "finalisation":
    # Vérification qu'un projet est sélectionné
    if not st.session_state.current_project_id:
        st.error("Aucun projet sélectionné.")
        st.session_state.page = "home"
        st.rerun()
    
    # Rendu du module de finalisation
    render_finalisation(
        project_id=st.session_state.current_project_id,
        project_context=project_context,
        history_manager=history_manager
    )

elif st.session_state.page == "project_settings":
    # Vérification qu'un projet est sélectionné
    if not st.session_state.current_project_id:
        st.error("Aucun projet sélectionné.")
        st.session_state.page = "home"
        st.rerun()
    
    # Chargement des données du projet
    project = project_context.load_project(st.session_state.current_project_id)
    
    st.title("Paramètres du projet")
    st.subheader(project.get("title", "Sans titre"))
    
    # Formulaire de modification des paramètres
    with st.form("project_settings_form"):
        title = st.text_input("Titre du projet", value=project.get("title", ""))
        description = st.text_area("Description", value=project.get("description", ""))
        
        project_type = st.selectbox(
            "Type de projet",
            ["Article académique", "Mémoire", "Thèse", "Rapport de recherche", "Autre"],
            index=["Article académique", "Mémoire", "Thèse", "Rapport de recherche", "Autre"].index(project.get("type", "Article académique"))
        )
        
        style = st.selectbox(
            "Style d'écriture",
            ["Standard", "Académique", "CRÉSUS-NAKAMOTO", "AcademicWritingCrypto"],
            index=["Standard", "Académique", "CRÉSUS-NAKAMOTO", "AcademicWritingCrypto"].index(project.get("preferences", {}).get("style", "Standard"))
        )
        
        discipline = st.selectbox(
            "Discipline",
            ["Sciences sociales", "Économie", "Droit", "Informatique", "Autre"],
            index=["Sciences sociales", "Économie", "Droit", "Informatique", "Autre"].index(project.get("preferences", {}).get("discipline", "Sciences sociales"))
        )
        
        preferred_length = st.slider(
            "Longueur cible (mots)",
            min_value=1000,
            max_value=20000,
            value=project.get("preferences", {}).get("preferred_length", 5000),
            step=1000
        )
        
        submitted = st.form_submit_button("Enregistrer les modifications")
        
        if submitted:
            if not title:
                st.error("Le titre est obligatoire.")
            else:
                # Mise à jour des données du projet
                project["title"] = title
                project["description"] = description
                project["type"] = project_type
                project["preferences"] = {
                    "style": style,
                    "discipline": discipline,
                    "preferred_length": preferred_length
                }
                
                # Sauvegarde du projet
                project_context.save_project(project)
                
                # Sauvegarde de la version dans l'historique
                history_manager.save_version(
                    project_id=st.session_state.current_project_id,
                    project_data=project,
                    description="Modification des paramètres"
                )
                
                st.success("Paramètres enregistrés avec succès!")
                
                # Redirection vers la page du projet
                st.session_state.page = "project_overview"
                st.rerun()
    
    # Bouton de suppression du projet
    st.markdown("---")
    st.subheader("Zone de danger")
    
    if st.button("Supprimer ce projet", type="primary", help="Cette action est irréversible!"):
        if project_context.delete_project(st.session_state.current_project_id):
            st.success("Projet supprimé avec succès!")
            
            # Redirection vers la page d'accueil
            st.session_state.current_project_id = None
            st.session_state.page = "home"
            st.rerun()
        else:
            st.error("Erreur lors de la suppression du projet.")

elif st.session_state.page == "history":
    # Vérification qu'un projet est sélectionné
    if not st.session_state.current_project_id:
        st.error("Aucun projet sélectionné.")
        st.session_state.page = "home"
        st.rerun()
    
    st.title("Historique du projet")
    
    # Chargement des données du projet
    project = project_context.load_project(st.session_state.current_project_id)
    st.subheader(project.get("title", "Sans titre"))
    
    # Récupération de l'historique
    history = history_manager.get_project_history(st.session_state.current_project_id)
    
    if not history:
        st.write("Aucun historique disponible pour ce projet.")
    else:
        # Filtrage par type d'événement
        event_type = st.radio(
            "Type d'événement",
            ["Tous", "Actions", "Versions"],
            horizontal=True
        )
        
        filtered_history = history
        if event_type == "Actions":
            filtered_history = [entry for entry in history if entry.get("type") == "action"]
        elif event_type == "Versions":
            filtered_history = [entry for entry in history if entry.get("type") == "version"]
        
        # Affichage de l'historique
        for entry in filtered_history:
            timestamp = datetime.fromisoformat(entry.get("timestamp", "")).strftime("%Y-%m-%d %H:%M:%S")
            
            if entry.get("type") == "action":
                st.markdown(f"**{timestamp}** - Action: {entry.get('action_type', '')}")
                
                if "details" in entry and entry["details"]:
                    with st.expander("Détails"):
                        for key, value in entry["details"].items():
                            st.write(f"{key}: {value}")
            
            elif entry.get("type") == "version":
                st.markdown(f"**{timestamp}** - Version: {entry.get('description', '')}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Voir les différences", key=f"diff_{entry.get('id', '')}"):
                        st.session_state.selected_version = entry.get("id", "")
                        st.session_state.show_diff = True
                
                with col2:
                    if st.button("Restaurer cette version", key=f"restore_{entry.get('id', '')}"):
                        if history_manager.restore_version(
                            project_id=st.session_state.current_project_id,
                            version_id=entry.get("id", "")
                        ):
                            st.success("Version restaurée avec succès!")
                            st.rerun()
                        else:
                            st.error("Erreur lors de la restauration de la version.")
                
                # Affichage des différences si demandé
                if st.session_state.get("show_diff", False) and st.session_state.get("selected_version") == entry.get("id", ""):
                    st.markdown("---")
                    st.subheader("Différences")
                    
                    if "diff" in entry:
                        st.code(entry["diff"], language="diff")
                    else:
                        st.write("Aucune différence disponible.")
                    
                    if st.button("Fermer"):
                        st.session_state.show_diff = False
                        st.rerun()
        
        # Bouton pour nettoyer l'historique
        st.markdown("---")
        st.subheader("Maintenance de l'historique")
        
        with st.expander("Options de nettoyage"):
            keep_last_n = st.slider(
                "Conserver les N dernières versions",
                min_value=0,
                max_value=20,
                value=5,
                step=1
            )
            
            if st.button("Nettoyer l'historique"):
                if history_manager.clear_history(
                    project_id=st.session_state.current_project_id,
                    keep_last_n=keep_last_n
                ):
                    st.success("Historique nettoyé avec succès!")
                    st.rerun()
                else:
                    st.error("Erreur lors du nettoyage de l'historique.")

elif st.session_state.page == "statistics":
    # Vérification qu'un projet est sélectionné
    if not st.session_state.current_project_id:
        st.error("Aucun projet sélectionné.")
        st.session_state.page = "home"
        st.rerun()
    
    st.title("Statistiques du projet")
    
    # Chargement des données du projet
    project = project_context.load_project(st.session_state.current_project_id)
    st.subheader(project.get("title", "Sans titre"))
    
    # Mise à jour des métadonnées du projet
    project_context.update_project_metadata(st.session_state.current_project_id)
    project = project_context.load_project(st.session_state.current_project_id)
    
    # Affichage des statistiques générales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Nombre de mots", project.get("metadata", {}).get("word_count", 0))
    
    with col2:
        st.metric("Nombre de sections", len(project.get("sections", [])))
    
    with col3:
        st.metric("Taux de complétion", f"{project.get('metadata', {}).get('completion_percentage', 0):.1f}%")
    
    # Statistiques par section
    st.subheader("Statistiques par section")
    
    if not project.get("sections"):
        st.write("Aucune section n'a encore été créée.")
    else:
        # Création d'un tableau de statistiques
        data = []
        for section in project.get("sections", []):
            word_count = section.get("metadata", {}).get("word_count", 0)
            revision_count = section.get("metadata", {}).get("revision_count", 0)
            
            data.append({
                "Section": section.get("title", "Sans titre"),
                "Mots": word_count,
                "Révisions": revision_count,
                "Dernière modification": section.get("last_modified", "")[:10]
            })
        
        # Affichage du tableau
        st.dataframe(data)
    
    # Analyse de complexité du texte
    st.subheader("Analyse de complexité")
    
    # Concaténation de tout le contenu
    all_content = "\n\n".join([section.get("content", "") for section in project.get("sections", [])])
    
    if not all_content:
        st.write("Aucun contenu à analyser.")
    else:
        # Analyse de la complexité
        complexity = adaptive_engine.analyze_text_complexity(all_content)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Phrases", complexity.get("sentence_count", 0))
        
        with col2:
            st.metric("Longueur moyenne des phrases", f"{complexity.get('avg_sentence_length', 0):.1f} mots")
        
        with col3:
            st.metric("Longueur moyenne des mots", f"{complexity.get('avg_word_length', 0):.1f} caractères")
        
        with col4:
            st.metric("Score de complexité", f"{complexity.get('complexity_score', 0):.1f}/20")
        
        # Suggestions de style
        st.subheader("Suggestions de style")
        
        target_style = project.get("preferences", {}).get("style", "Standard")
        suggestions = adaptive_engine.suggest_style_improvements(all_content, target_style)
        
        for suggestion in suggestions:
            st.info(f"💡 {suggestion}")
        
        # Suggestions de citations
        st.subheader("Suggestions de citations")
        
        discipline = project.get("preferences", {}).get("discipline", "Sciences sociales")
        citation_suggestions = adaptive_engine.suggest_citations(all_content, discipline)
        
        if not citation_suggestions:
            st.write("Aucune suggestion de citation pour le moment.")
        else:
            for suggestion in citation_suggestions:
                with st.expander(f"Citation suggérée: \"{suggestion.get('trigger', '')}\""):
                    st.write(f"**Phrase:** {suggestion.get('sentence', '')}")
                    st.write(f"**Suggestion:** {suggestion.get('suggestion', '')}")
