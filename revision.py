def render_revision(project_id, section_id, project_context, history_manager, adaptive_engine, integration_layer):
    """
    Affiche l'interface de révision pour une section de projet.
    
    Args:
        project_id: ID du projet
        section_id: ID de la section (optionnel)
        project_context: Instance de ProjectContext
        history_manager: Instance de HistoryManager
        adaptive_engine: Instance de AdaptiveEngine
        integration_layer: Instance de IntegrationLayer
    """
    import streamlit as st
    from utils.ai_service import call_ai_safe
    
    st.title("Révision")
    
    # Chargement des données du projet
    project = project_context.load_project(project_id)
    
    st.subheader(project.get("title", "Sans titre"))
    
    # Sélection de la section
    sections = project.get("sections", [])
    
    if not sections:
        st.warning("Aucune section n'a été créée. Veuillez d'abord créer des sections dans le storyboard.")
        
        if st.button("Aller au storyboard"):
            st.session_state.page = "storyboard"
            st.rerun()
            
        return
    
    # Si aucune section n'est sélectionnée, afficher la liste des sections
    if not section_id:
        st.write("Sélectionnez une section à réviser:")
        
        for i, section in enumerate(sections):
            if st.button(f"{i+1}. {section.get('title', 'Sans titre')}", key=f"select_{section.get('section_id', '')}"):
                st.session_state.current_section_id = section.get("section_id", "")
                st.rerun()
                
        return
    
    # Récupération de la section sélectionnée
    current_section = None
    for section in sections:
        if section.get("section_id") == section_id:
            current_section = section
            break
    
    if not current_section:
        st.error("Section non trouvée.")
        st.session_state.current_section_id = None
        st.rerun()
        return
    
    # Affichage du titre de la section
    st.write(f"Section: **{current_section.get('title', 'Sans titre')}**")
    
    # Affichage du contenu actuel
    current_content = current_section.get("content", "")
    
    if not current_content:
        st.warning("Cette section ne contient pas encore de contenu. Veuillez d'abord rédiger du contenu.")
        
        if st.button("Aller à la rédaction"):
            st.session_state.page = "redaction"
            st.rerun()
            
        return
    
    # Interface de révision
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Éditeur de texte
        new_content = st.text_area(
            "Contenu de la section",
            value=current_content,
            height=400
        )
        
        # Boutons d'action
        save_col, cancel_col = st.columns(2)
        
        with save_col:
            if st.button("Enregistrer les modifications"):
                if project_context.update_section(
                    project_id=project_id,
                    section_id=section_id,
                    content=new_content
                ):
                    # Mise à jour des métadonnées
                    project_context.update_project_metadata(project_id)
                    
                    # Mise à jour du statut du projet
                    project_context.update_project_status(project_id, "revision_in_progress")
                    
                    # Sauvegarde de la version dans l'historique
                    project_data = project_context.load_project(project_id)
                    history_manager.save_version(
                        project_id=project_id,
                        project_data=project_data,
                        description=f"Révision de la section: {current_section.get('title', 'Sans titre')}"
                    )
                    
                    st.success("Modifications enregistrées avec succès!")
                    st.rerun()
                else:
                    st.error("Erreur lors de l'enregistrement des modifications.")
        
        with cancel_col:
            if st.button("Annuler"):
                st.session_state.current_section_id = None
                st.session_state.page = "project_overview"
                st.rerun()
    
    with col2:
        # Outils d'aide à la révision
        st.subheader("Outils de révision")
        
        # Analyse de complexité
        complexity = adaptive_engine.analyze_text_complexity(current_content)
        
        st.write("**Analyse du texte:**")
        st.write(f"- Mots: {complexity.get('word_count', 0)}")
        st.write(f"- Phrases: {complexity.get('sentence_count', 0)}")
        st.write(f"- Longueur moyenne des phrases: {complexity.get('avg_sentence_length', 0):.1f} mots")
        st.write(f"- Score de complexité: {complexity.get('complexity_score', 0):.1f}/20")
        
        # Suggestions de style
        st.write("**Suggestions de style:**")
        
        target_style = project.get("preferences", {}).get("style", "Standard")
        suggestions = adaptive_engine.suggest_style_improvements(current_content, target_style)
        
        for suggestion in suggestions[:3]:  # Limite à 3 suggestions
            st.info(f"💡 {suggestion}")
        
        # Suggestions de citations
        st.write("**Suggestions de citations:**")
        
        discipline = project.get("preferences", {}).get("discipline", "Sciences sociales")
        citation_suggestions = adaptive_engine.suggest_citations(current_content, discipline)
        
        if not citation_suggestions:
            st.write("Aucune suggestion de citation pour le moment.")
        else:
            for suggestion in citation_suggestions[:2]:  # Limite à 2 suggestions
                st.info(f"💡 Considérez ajouter une citation pour: \"{suggestion.get('trigger', '')}\"")
        
        # Outils de révision assistée
        st.subheader("Révision assistée")
        
        revision_type = st.selectbox(
            "Type de révision",
            ["Amélioration du style", "Correction grammaticale", "Clarification", "Condensation"]
        )
        
        if st.button("Appliquer la révision assistée"):
            with st.spinner("Révision en cours..."):
                # Construction du prompt en fonction du type de révision
                prompt_prefix = ""
                
                if revision_type == "Amélioration du style":
                    prompt_prefix = f"Améliore le style de ce texte académique en utilisant un style {target_style}, sans changer le sens:"
                elif revision_type == "Correction grammaticale":
                    prompt_prefix = "Corrige les erreurs grammaticales et typographiques dans ce texte académique, sans changer le sens:"
                elif revision_type == "Clarification":
                    prompt_prefix = "Clarifie les passages complexes de ce texte académique, sans changer le sens global:"
                elif revision_type == "Condensation":
                    prompt_prefix = "Condense ce texte académique en le rendant plus concis, tout en préservant les idées principales:"
                
                # Appel à l'API
                result = call_ai_safe(
                    prompt=f"{prompt_prefix}\n\n{current_content}",
                    max_tokens=len(current_content.split()) * 2,  # Estimation grossière
                    temperature=0.3,  # Température basse pour une révision plus fidèle
                    model="gpt-4o"
                )
                
                revised_text = result.get("text", "")
                
                if revised_text:
                    st.session_state.revised_text = revised_text
                    st.success("Révision terminée avec succès!")
                else:
                    st.error("Erreur lors de la révision du texte.")
        
        # Affichage du texte révisé
        if "revised_text" in st.session_state:
            st.subheader("Texte révisé")
            st.write(st.session_state.revised_text)
            
            if st.button("Appliquer cette révision"):
                # Mise à jour de la section avec le texte révisé
                if project_context.update_section(
                    project_id=project_id,
                    section_id=section_id,
                    content=st.session_state.revised_text
                ):
                    # Mise à jour des métadonnées
                    project_context.update_project_metadata(project_id)
                    
                    # Sauvegarde de la version dans l'historique
                    project_data = project_context.load_project(project_id)
                    history_manager.save_version(
                        project_id=project_id,
                        project_data=project_data,
                        description=f"Révision assistée ({revision_type}) de la section: {current_section.get('title', 'Sans titre')}"
                    )
                    
                    st.success("Révision appliquée avec succès!")
                    st.rerun()
                else:
                    st.error("Erreur lors de l'application de la révision.")
    
    # Navigation entre les sections
    st.markdown("---")
    st.subheader("Navigation")
    
    prev_col, next_col = st.columns(2)
    
    # Trouver l'index de la section actuelle
    current_index = -1
    for i, section in enumerate(sections):
        if section.get("section_id") == section_id:
            current_index = i
            break
    
    with prev_col:
        if current_index > 0:
            prev_section = sections[current_index - 1]
            if st.button(f"← Section précédente: {prev_section.get('title', 'Sans titre')}"):
                st.session_state.current_section_id = prev_section.get("section_id", "")
                st.rerun()
    
    with next_col:
        if current_index < len(sections) - 1:
            next_section = sections[current_index + 1]
            if st.button(f"Section suivante: {next_section.get('title', 'Sans titre')} →"):
                st.session_state.current_section_id = next_section.get("section_id", "")
                st.rerun()
