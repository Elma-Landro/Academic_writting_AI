def render_redaction(project_id, section_id, project_context, history_manager, adaptive_engine, integration_layer):
    """
    Affiche l'interface de rédaction pour une section de projet.
    
    Args:
        project_id: ID du projet
        section_id: ID de la section (optionnel)
        project_context: Instance de ProjectContext
        history_manager: Instance de HistoryManager
        adaptive_engine: Instance de AdaptiveEngine
        integration_layer: Instance de IntegrationLayer
    """
    import streamlit as st
    from utils.ai_service import generate_academic_text
    
    st.title("Rédaction")
    
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
        st.write("Sélectionnez une section à rédiger:")
        
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
    
    # Interface de rédaction
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
            if st.button("Enregistrer"):
                if project_context.update_section(
                    project_id=project_id,
                    section_id=section_id,
                    content=new_content
                ):
                    # Mise à jour des métadonnées
                    project_context.update_project_metadata(project_id)
                    
                    # Mise à jour du statut du projet
                    if project.get("status") == "storyboard_ready":
                        project_context.update_project_status(project_id, "draft_in_progress")
                    
                    # Sauvegarde de la version dans l'historique
                    project_data = project_context.load_project(project_id)
                    history_manager.save_version(
                        project_id=project_id,
                        project_data=project_data,
                        description=f"Mise à jour de la section: {current_section.get('title', 'Sans titre')}"
                    )
                    
                    st.success("Section enregistrée avec succès!")
                    st.rerun()
                else:
                    st.error("Erreur lors de l'enregistrement de la section.")
        
        with cancel_col:
            if st.button("Annuler"):
                st.session_state.current_section_id = None
                st.session_state.page = "project_overview"
                st.rerun()
    
    with col2:
        # Suggestions et outils d'aide à la rédaction
        st.subheader("Outils d'aide")
        
        # Analyse de complexité
        if current_content:
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
        
        # Génération de contenu assistée
        st.subheader("Génération assistée")
        
        with st.form("generate_content_form"):
            prompt = st.text_area(
                "Description du contenu à générer",
                placeholder="Décrivez le contenu que vous souhaitez générer..."
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
            
            generate_button = st.form_submit_button("Générer")
            
            if generate_button and prompt:
                with st.spinner("Génération du contenu en cours..."):
                    result = generate_academic_text(
                        prompt=prompt,
                        style=style,
                        length=length
                    )
                    
                    generated_text = result.get("text", "")
                    
                    if generated_text:
                        st.session_state.generated_text = generated_text
                        st.success("Contenu généré avec succès!")
                    else:
                        st.error("Erreur lors de la génération du contenu.")
        
        # Affichage du texte généré
        if "generated_text" in st.session_state:
            st.subheader("Contenu généré")
            st.write(st.session_state.generated_text)
            
            if st.button("Insérer ce contenu"):
                # Insertion du contenu généré dans l'éditeur
                new_content = st.session_state.generated_text
                
                # Mise à jour de la section
                if project_context.update_section(
                    project_id=project_id,
                    section_id=section_id,
                    content=new_content
                ):
                    # Mise à jour des métadonnées
                    project_context.update_project_metadata(project_id)
                    
                    # Sauvegarde de la version dans l'historique
                    project_data = project_context.load_project(project_id)
                    history_manager.save_version(
                        project_id=project_id,
                        project_data=project_data,
                        description=f"Contenu généré pour la section: {current_section.get('title', 'Sans titre')}"
                    )
                    
                    st.success("Contenu inséré avec succès!")
                    st.rerun()
                else:
                    st.error("Erreur lors de l'insertion du contenu.")
    
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
