def sidebar(projects, current_id):
    """
    Affiche la barre latérale avec la liste des projets et les options de navigation.
    
    Args:
        projects: Liste des projets
        current_id: ID du projet actuel
    """
    import streamlit as st
    
    st.sidebar.title("Système de Rédaction Académique")
    
    # Sélection du projet
    st.sidebar.header("Projets")
    
    # Bouton pour créer un nouveau projet
    if st.sidebar.button("➕ Nouveau projet"):
        st.session_state.page = "new_project"
        st.session_state.current_project_id = None
    
    # Liste des projets existants
    for project in projects:
        project_id = project.get("project_id", "")
        title = project.get("title", "Sans titre")
        
        # Affichage du statut avec badge coloré
        status = project.get("status", "created")
        status_colors = {
            "created": "🟤",
            "storyboard_ready": "🟠",
            "draft_in_progress": "🟡",
            "revision_in_progress": "🟢",
            "completed": "🔵"
        }
        status_icon = status_colors.get(status, "⚪")
        
        # Bouton pour chaque projet
        if st.sidebar.button(f"{status_icon} {title}", key=f"project_{project_id}"):
            st.session_state.current_project_id = project_id
            st.session_state.page = "project_overview"
    
    # Navigation du workflow (visible uniquement si un projet est sélectionné)
    if current_id:
        st.sidebar.markdown("---")
        st.sidebar.header("Workflow")
        
        # Étapes du workflow
        workflow_steps = [
            ("storyboard", "1️⃣ Storyboard"),
            ("redaction", "2️⃣ Rédaction"),
            ("revision", "3️⃣ Révision"),
            ("finalisation", "4️⃣ Finalisation")
        ]
        
        for step_id, step_name in workflow_steps:
            if st.sidebar.button(step_name, key=f"nav_{step_id}"):
                st.session_state.page = step_id
        
        # Options supplémentaires
        st.sidebar.markdown("---")
        st.sidebar.header("Options")
        
        if st.sidebar.button("⚙️ Paramètres du projet"):
            st.session_state.page = "project_settings"
            
        if st.sidebar.button("📊 Statistiques"):
            st.session_state.page = "statistics"
            
        if st.sidebar.button("📋 Historique"):
            st.session_state.page = "history"
    
    # Pied de page
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2025 Academic Writing System")
    
    # Affichage des informations de version
    st.sidebar.caption("Version 1.0.0")
