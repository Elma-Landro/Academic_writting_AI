# Système de Rédaction Académique

Un système complet pour structurer, rédiger et réviser des textes académiques avec assistance IA.

## Présentation

Le Système de Rédaction Académique est une application web conçue pour aider les chercheurs, enseignants et étudiants à produire des textes académiques de qualité en suivant un workflow optimisé et en bénéficiant d'une assistance IA adaptée.

Ce système intègre la méthodologie Michelat et l'Agent de Construction Sectionnelle pour offrir une expérience de rédaction structurée, cohérente et efficace.

## Fonctionnalités principales

- **Storyboard Engine** : Structuration narrative et organisation des idées
- **Agent de Déploiement Théorique** : Rédaction assistée par IA
- **Module de Révision** : Amélioration du style et de la cohérence
- **Finalisation** : Export dans différents formats (TXT, MD, JSON)
- **Gestion de l'historique** : Suivi des versions et restauration
- **Profil utilisateur** : Personnalisation de l'expérience
- **Moteur adaptatif** : Suggestions contextuelles et aide à la rédaction

## Architecture du système

Le système est organisé en modules distincts :

- **Core** : Modules fondamentaux (profil utilisateur, contexte de projet, moteur adaptatif, etc.)
- **Modules** : Fonctionnalités spécifiques (storyboard, rédaction, révision, finalisation)
- **Utils** : Services utilitaires (IA, cache, fonctions communes)

## Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Configuration

1. Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```
OPENAI_API_KEY=votre_clé_api_openai
VENICE_API_KEY=votre_clé_api_venice (optionnel)
```

2. Assurez-vous que les dossiers de données sont créés (ils seront automatiquement créés au premier lancement) :

```
data/
├── cache/
├── exports/
├── history/
├── profiles/
└── projects/
```

## Utilisation

### Lancement de l'application

```bash
streamlit run app.py
```

L'application sera accessible à l'adresse http://localhost:8501

### Workflow recommandé

1. **Création d'un projet** : Définissez le titre, la description et les préférences
2. **Storyboard** : Structurez votre document en sections
3. **Rédaction** : Rédigez le contenu de chaque section
4. **Révision** : Améliorez le style et la cohérence
5. **Finalisation** : Exportez votre document dans le format souhaité

## Styles d'écriture

Le système prend en charge plusieurs styles d'écriture académique :

- **Standard** : Style académique standard, clair et précis
- **Académique** : Style académique formel avec terminologie spécialisée
- **CRÉSUS-NAKAMOTO** : Style analytique avec tensions conceptuelles et perspective historique
- **AcademicWritingCrypto** : Style technique orienté crypto-ethnographie

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## Remerciements

- Méthodologie Michelat pour la structure de workflow
- Agent de Construction Sectionnelle pour les techniques de rédaction
- OpenAI pour les services d'IA
