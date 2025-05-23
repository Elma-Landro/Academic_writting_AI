def render_finalisation(project_id, project_context, history_manager):
    """
    Affiche l'interface de finalisation pour un projet.
    
    Args:
        project_id: ID du projet
        project_context: Instance de ProjectContext
        history_manager: Instance de HistoryManager
    """
    import streamlit as st
    import os
    from datetime import datetime
    
    st.title("Finalisation")
    
    # Chargement des données du projet
    project = project_context.load_project(project_id)
    
    st.subheader(project.get("title", "Sans titre"))
    
    # Vérification que le projet contient des sections
    sections = project.get("sections", [])
    
    if not sections:
        st.warning("Aucune section n'a été créée. Veuillez d'abord créer des sections dans le storyboard.")
        
        if st.button("Aller au storyboard"):
            st.session_state.page = "storyboard"
            st.rerun()
            
        return
    
    # Affichage du contenu complet
    st.write("Aperçu du document complet:")
    
    with st.expander("Voir le document complet", expanded=True):
        # Titre du document
        st.markdown(f"# {project.get('title', 'Sans titre')}")
        
        # Description/Résumé
        if project.get("description"):
            st.markdown("## Résumé")
            st.markdown(project.get("description"))
        
        # Sections
        for i, section in enumerate(sections):
            st.markdown(f"## {section.get('title', f'Section {i+1}')}")
            st.markdown(section.get("content", ""))
    
    # Options d'export
    st.markdown("---")
    st.subheader("Options d'export")
    
    export_format = st.selectbox(
        "Format d'export",
        ["Texte brut (.txt)", "Markdown (.md)", "JSON (.json)"]
    )
    
    include_metadata = st.checkbox("Inclure les métadonnées", value=False)
    
    if st.button("Exporter"):
        try:
            # Création du répertoire d'export si nécessaire
            export_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "exports")
            os.makedirs(export_dir, exist_ok=True)
            
            # Nom du fichier d'export
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{project.get('title', 'document').replace(' ', '_')}_{timestamp}"
            
            if export_format == "Texte brut (.txt)":
                export_path = os.path.join(export_dir, f"{filename}.txt")
                
                with open(export_path, "w", encoding="utf-8") as f:
                    # Titre et description
                    f.write(f"{project.get('title', 'Sans titre')}\n\n")
                    
                    if include_metadata:
                        f.write(f"Type: {project.get('type', '')}\n")
                        f.write(f"Créé le: {project.get('created_date', '')[:10]}\n")
                        f.write(f"Dernière modification: {project.get('last_modified', '')[:10]}\n\n")
                    
                    if project.get("description"):
                        f.write("RÉSUMÉ\n\n")
                        f.write(f"{project.get('description')}\n\n")
                    
                    # Sections
                    for i, section in enumerate(sections):
                        f.write(f"{section.get('title', f'Section {i+1}').upper()}\n\n")
                        f.write(f"{section.get('content', '')}\n\n")
            
            elif export_format == "Markdown (.md)":
                export_path = os.path.join(export_dir, f"{filename}.md")
                
                with open(export_path, "w", encoding="utf-8") as f:
                    # Titre et description
                    f.write(f"# {project.get('title', 'Sans titre')}\n\n")
                    
                    if include_metadata:
                        f.write(f"*Type: {project.get('type', '')}*\n\n")
                        f.write(f"*Créé le: {project.get('created_date', '')[:10]}*\n\n")
                        f.write(f"*Dernière modification: {project.get('last_modified', '')[:10]}*\n\n")
                    
                    if project.get("description"):
                        f.write("## Résumé\n\n")
                        f.write(f"{project.get('description')}\n\n")
                    
                    # Sections
                    for i, section in enumerate(sections):
                        f.write(f"## {section.get('title', f'Section {i+1}')}\n\n")
                        f.write(f"{section.get('content', '')}\n\n")
            
            elif export_format == "JSON (.json)":
                export_path = os.path.join(export_dir, f"{filename}.json")
                
                # Export au format JSON
                project_context.export_project(project_id, "json")
                
                # Copie du fichier exporté
                import shutil
                source_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports", f"{project_id}_export.json")
                shutil.copy(source_path, export_path)
            
            # Mise à jour du statut du projet
            project_context.update_project_status(project_id, "completed")
            
            # Sauvegarde de la version dans l'historique
            project_data = project_context.load_project(project_id)
            history_manager.save_version(
                project_id=project_id,
                project_data=project_data,
                description=f"Finalisation et export au format {export_format}"
            )
            
            st.success(f"Document exporté avec succès: {export_path}")
            
            # Bouton de téléchargement
            with open(export_path, "r", encoding="utf-8") as f:
                content = f.read()
                
                st.download_button(
                    label="Télécharger le fichier",
                    data=content,
                    file_name=os.path.basename(export_path),
                    mime="text/plain"
                )
                
        except Exception as e:
            st.error(f"Erreur lors de l'export: {str(e)}")
    
    # Options de conversion avancées (placeholder pour fonctionnalités futures)
    st.markdown("---")
    st.subheader("Conversion avancée")
    
    with st.expander("Options de conversion (à venir)"):
        st.selectbox(
            "Format cible",
            ["PDF (.pdf)", "Word (.docx)", "LaTeX (.tex)"]
        )
        
        st.selectbox(
            "Style de citation",
            ["APA", "MLA", "Chicago", "Harvard"]
        )
        
        st.checkbox("Inclure une bibliographie", value=True)
        st.checkbox("Inclure une table des matières", value=True)
        
        st.button("Convertir (fonctionnalité à venir)")
        
        st.info("Ces fonctionnalités de conversion avancée seront disponibles dans une prochaine version.")
    
    # Finalisation du projet
    st.markdown("---")
    st.subheader("Finalisation du projet")
    
    if st.button("Marquer le projet comme terminé"):
        # Mise à jour du statut du projet
        project_context.update_project_status(project_id, "completed")
        
        # Sauvegarde de la version dans l'historique
        project_data = project_context.load_project(project_id)
        history_manager.save_version(
            project_id=project_id,
            project_data=project_data,
            description="Projet marqué comme terminé"
        )
        
        st.success("Projet marqué comme terminé avec succès!")
        
        # Redirection vers la page du projet
        st.session_state.page = "project_overview"
        st.rerun()
