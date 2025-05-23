import streamlit as st
from utils.ai_service import generate_academic_text

def render_storyboard(project_id, project_context, history_manager, adaptive_engine):
    """
    Affiche l'interface de storyboard pour un projet.
    
    Args:
        project_id: ID du projet
        project_context: Instance de ProjectContext
        history_manager: Instance de HistoryManager
        adaptive_engine: Instance de AdaptiveEngine
    """
    st.title("Storyboard")
    
    # Chargement des données du projet
    project = project_context.load_project(project_id)
    
    st.subheader(project.get("title", "Sans titre"))
    
    # Affichage des sections existantes
    sections = project.get("sections", [])
    
    if sections:
        st.write("Structure actuelle du document:")
        
        for i, section in enumerate(sections):
            with st.expander(f"{i+1}. {section.get('title', 'Sans titre')}"):
                st.write(section.get("content", ""))
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Éditer", key=f"edit_{section.get('section_id', '')}"):
                        st.session_state.current_section_id = section.get("section_id", "")
                        st.session_state.page = "redaction"
                        st.rerun()
                
                with col2:
                    if st.button("Supprimer", key=f"delete_{section.get('section_id', '')}"):
                        if project_context.delete_section(project_id, section.get("section_id", "")):
                            # Mise à jour des métadonnées
                            project_context.update_project_metadata(project_id)
                            
                            # Sauvegarde de la version dans l'historique
                            project_data = project_context.load_project(project_id)
                            history_manager.save_version(
                                project_id=project_id,
                                project_data=project_data,
                                description=f"Suppression de la section: {section.get('title', 'Sans titre')}"
                            )
                            
                            st.success("Section supprimée avec succès!")
                            st.rerun()
                        else:
                            st.error("Erreur lors de la suppression de la section.")
    
    # Formulaire d'ajout de section
    st.markdown("---")
    st.subheader("Ajouter une nouvelle section")
    
    with st.form("add_section_form"):
        title = st.text_input("Titre de la section")
        
        # Options pour la génération de contenu
        generate_content = st.checkbox("Générer un contenu initial")
        
        if generate_content:
            content_prompt = st.text_area(
                "Description du contenu à générer",
                placeholder="Décrivez le contenu que vous souhaitez générer pour cette section..."
            )
            
            style = st.selectbox(
                "Style d'écriture",
                ["Standard", "Académique", "CRÉSUS-NAKAMOTO", "AcademicWritingCrypto"],
                index=["Standard", "Académique", "CRÉSUS-NAKAMOTO", "AcademicWritingCrypto"].index(
                    project.get("preferences", {}).get("style", "Standard")
                )
            )
            
            length = st.slider(
                "Longueur approximative (mots)",
                min_value=100,
                max_value=1000,
                value=300,
                step=100
            )
        
        submitted = st.form_submit_button("Ajouter la section")
        
        if submitted:
            if not title:
                st.error("Le titre est obligatoire.")
            else:
                content = ""
                
                # Génération du contenu si demandé
                if generate_content and content_prompt:
                    with st.spinner("Génération du contenu en cours..."):
                        result = generate_academic_text(
                            prompt=content_prompt,
                            style=style,
                            length=length
                        )
                        
                        content = result.get("text", "")
                
                # Ajout de la section
                section_id = project_context.add_section(
                    project_id=project_id,
                    title=title,
                    content=content
                )
                
                # Mise à jour des métadonnées
                project_context.update_project_metadata(project_id)
                
                # Mise à jour du statut du projet
                if project.get("status") == "created":
                    project_context.update_project_status(project_id, "storyboard_ready")
                
                # Sauvegarde de la version dans l'historique
                project_data = project_context.load_project(project_id)
                history_manager.save_version(
                    project_id=project_id,
                    project_data=project_data,
                    description=f"Ajout de la section: {title}"
                )
                
                st.success("Section ajoutée avec succès!")
                st.rerun()
    
    # Réorganisation des sections
    if sections:
        st.markdown("---")
        st.subheader("Réorganiser les sections")
        
        st.write("Faites glisser les sections pour les réorganiser:")
        
        # Simulation d'interface de réorganisation
        section_titles = [section.get("title", "Sans titre") for section in sections]
        
        # Dans une vraie implémentation, on utiliserait une bibliothèque de drag-and-drop
        # Pour cette démonstration, on utilise une liste de sélection
        selected_indices = []
        for i, title in enumerate(section_titles):
            if st.checkbox(f"{i+1}. {title}", key=f"reorder_{i}"):
                selected_indices.append(i)
        
        new_order = st.selectbox(
            "Nouvelle position pour les sections sélectionnées",
            range(1, len(sections) + 1)
        )
        
        if st.button("Appliquer la réorganisation") and selected_indices:
            st.info("Fonctionnalité de réorganisation à implémenter.")
            # Dans une vraie implémentation, on réorganiserait les sections ici
    
    # Suggestions du moteur adaptatif
    st.markdown("---")
    st.subheader("Suggestions pour votre storyboard")
    
    # Suggestions basées sur le type de projet
    project_type = project.get("type", "Article académique")
    
    if project_type == "Article académique":
        st.info("""
        💡 **Structure recommandée pour un article académique:**
        
        1. Introduction (contexte, problématique, plan)
        2. Revue de littérature / Cadre théorique
        3. Méthodologie
        4. Résultats
        5. Discussion
        6. Conclusion
        """)
    
    elif project_type == "Mémoire" or project_type == "Thèse":
        st.info("""
        💡 **Structure recommandée pour un mémoire/thèse:**
        
        1. Introduction générale
        2. Revue de littérature
        3. Cadre théorique
        4. Méthodologie
        5. Résultats (plusieurs chapitres possibles)
        6. Discussion
        7. Conclusion générale
        """)
    
    # Bouton pour terminer le storyboard
    st.markdown("---")
    
    if st.button("Terminer le storyboard"):
        # Mise à jour du statut du projet
        project_context.update_project_status(project_id, "storyboard_ready")
        
        # Sauvegarde de la version dans l'historique
        project_data = project_context.load_project(project_id)
        history_manager.save_version(
            project_id=project_id,
            project_data=project_data,
            description="Storyboard terminé"
        )
        
        st.success("Storyboard terminé avec succès! Vous pouvez maintenant passer à la phase de rédaction.")
        
        # Redirection vers la page du projet
        st.session_state.page = "project_overview"
        st.rerun()
