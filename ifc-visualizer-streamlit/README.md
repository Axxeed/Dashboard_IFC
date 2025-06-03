# Visualiseur de Données IFC (Version Streamlit)

## Description

Cette application est une visionneuse de données pour les fichiers IFC (Industry Foundation Classes), développée avec Python, Streamlit et IfcOpenShell. Elle permet aux utilisateurs de téléverser des fichiers IFC, d'analyser leur structure et d'explorer les propriétés des objets qu'ils contiennent. L'objectif est de fournir une interface utilisateur simple et interactive pour l'inspection de modèles IFC.

## Prérequis

-   Python 3.7+ (recommandé Python 3.9+)
-   `pip` (gestionnaire de paquets Python)

## Installation

1.  **Cloner le Dépôt (si applicable)**:
    Si vous avez obtenu ce projet via un dépôt Git, clonez-le d'abord. Sinon, si les fichiers sont déjà présents (par exemple, dans cet environnement de développement), passez à l'étape suivante.
    ```bash
    # git clone <URL-du-dépôt>
    # cd ifc-visualizer-streamlit
    ```

2.  **Naviguer vers le Répertoire du Projet**:
    Assurez-vous d'être dans le répertoire `ifc-visualizer-streamlit`.
    ```bash
    cd chemin/vers/votre/projet/ifc-visualizer-streamlit
    ```
    *(Dans l'environnement de développement actuel, cela correspondrait à `/app/ifc-visualizer-streamlit/`)*

3.  **Créer un Environnement Virtuel**:
    Il est fortement recommandé d'utiliser un environnement virtuel pour isoler les dépendances du projet.
    ```bash
    python3 -m venv venv
    ```

4.  **Activer l'Environnement Virtuel**:
    -   Sur Linux/macOS :
        ```bash
        source venv/bin/activate
        ```
    -   Sur Windows :
        ```bash
        venv\Scripts\activate
        ```
    *(Note : L'environnement virtuel pour ce projet, s'il a été créé par des étapes précédentes dans cet outil, pourrait être situé à `/tmp/ifc-visualizer-streamlit-venv/`)*

5.  **Installer les Dépendances**:
    Installez toutes les bibliothèques Python nécessaires à l'aide du fichier `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```
    *(Si vous rencontrez des problèmes avec `ifcopenshell`, consultez leur documentation officielle pour des instructions d'installation spécifiques à votre système d'exploitation.)*

## Lancement de l'Application

1.  **Activez l'Environnement Virtuel** (si ce n'est pas déjà fait, voir étape 4 de l'installation).

2.  **Assurez-vous d'être dans le bon répertoire**:
    Vous devez être dans le répertoire `ifc-visualizer-streamlit` où se trouve `streamlit_app.py`.

3.  **Exécutez la Commande Streamlit**:
    ```bash
    streamlit run streamlit_app.py
    ```

4.  **Accédez à l'Application**:
    Streamlit devrait automatiquement ouvrir l'application dans votre navigateur web par défaut. Sinon, ouvrez votre navigateur et allez à l'adresse locale affichée dans le terminal (généralement `http://localhost:8501`).

## Utilisation

1.  **Téléversement du Fichier IFC**:
    -   Sur la page principale de l'application, vous verrez une zone de téléversement. Cliquez sur "Browse files" (ou glissez-déposez un fichier) pour sélectionner un fichier `.ifc` depuis votre ordinateur.
    -   L'application supporte les fichiers IFC valides (par exemple, IFC2X3, IFC4).

2.  **Traitement du Fichier**:
    -   Une fois le fichier téléversé, l'application l'analysera. Un message de succès s'affichera si le chargement réussit.
    -   Le nom du projet IFC (si trouvé) sera affiché.

3.  **Sélection d'un Type d'Objet**:
    -   Un menu déroulant intitulé "Sélectionnez un type d'objet à inspecter :" apparaîtra. Il contiendra la liste de tous les types d'objets uniques (par exemple, `IfcWall`, `IfcDoor`, `IfcWindow`) présents dans votre fichier.
    -   Choisissez un type d'objet dans cette liste pour voir les éléments correspondants.

4.  **Visualisation des Propriétés**:
    -   Après avoir sélectionné un type d'objet, un tableau s'affichera avec les propriétés des éléments de ce type.
    -   Les colonnes principales comme `StepId`, `GlobalId`, `Name`, et `IfcType` sont affichées en premier pour une identification facile.
    -   Les autres colonnes correspondent aux propriétés trouvées dans les jeux de propriétés (Property Sets) des éléments.
    -   Pour des raisons de performance, l'affichage peut être limité aux 50 premiers éléments pour les types d'objets très nombreux.

5.  **Graphique de Distribution des Types**:
    -   Un graphique à barres sous la section des propriétés montre le nombre d'occurrences pour chaque type d'objet dans le fichier, vous donnant un aperçu de la composition du modèle.

---

Ce fichier README fournit les instructions nécessaires pour installer, lancer et utiliser l'application "Visualiseur de Données IFC (Version Streamlit)".
