# Visualiseur de Données IFC

## Description

Le Visualiseur de Données IFC est une application web développée avec Python, Dash et IfcOpenShell. Elle permet aux utilisateurs de téléverser des fichiers IFC (Industry Foundation Classes), de les analyser et d'explorer leur contenu, y compris les types d'objets et les propriétés des éléments. Cet outil est conçu pour fournir une interface simple pour inspecter les données au sein des modèles IFC.

## Fonctionnalités

-   **Téléversement de Fichiers IFC**: Téléversez en toute sécurité des fichiers IFC (versions supportées par IfcOpenShell, typiquement IFC2X3 et IFC4).
-   **Exploration des Types d'Objets**: Identifie et liste automatiquement tous les types d'objets uniques présents dans le fichier IFC téléversé (par ex., IfcWall, IfcDoor, IfcWindow).
-   **Visualisation des Propriétés des Éléments**: Sélectionnez un type d'objet pour afficher un tableau de tous les éléments de ce type, ainsi que leurs propriétés (GlobalId, Name, IfcType, et tous les jeux de propriétés associés - Property Sets).
-   **Tableau Dynamique**: Les colonnes du tableau des propriétés sont générées dynamiquement en fonction des données présentes dans les éléments sélectionnés.
-   **Indicateurs de Chargement**: Retour visuel pendant l'analyse des fichiers et le chargement du tableau de données.
-   **Espace Réservé pour Visualisation 3D**: Inclut un espace réservé pour une future visualisation 3D du modèle.

## Structure du Projet

Le répertoire principal du projet `ifc-visualizer` est typiquement situé sous `/app` dans l'environnement de développement/exécution.

```
/app/
├── ifc-visualizer/
│   ├── src/
│   │   ├── __init__.py       (peut être vide, fait de src un package)
│   │   ├── app.py            (Mise en page de l'application Dash, callbacks et logique serveur)
│   │   └── ifc_parser.py     (Gère le chargement des fichiers IFC et l'extraction des données avec IfcOpenShell)
│   ├── requirements.txt      (Liste des dépendances Python)
│   └── README.md             (Ce fichier, en français)
├── test.ifc                  (Un fichier IFC fictif créé par ifc_parser.py s'il est exécuté directement depuis /app)
└── ... (autres fichiers ou répertoires potentiels au niveau racine comme .git)
```
*(Note : `test.ifc` est créé dans `/app` si `src/ifc_parser.py` est exécuté directement depuis `/app` et que `test.ifc` n'y est pas trouvé. Ce n'est pas une partie de la structure déployée de l'application principale mais un effet secondaire du code de test du parseur.)*

## Configuration et Installation

1.  **Cloner le Dépôt (Exemple)** :
    Si ce projet était dans un dépôt Git, vous le cloneriez. Pour cet environnement, les fichiers sont déjà en place.
    ```bash
    # git clone <url-du-depot>
    # cd ifc-visualizer
    ```
    Typiquement, vous naviguerez vers le répertoire `ifc-visualizer` : `cd ifc-visualizer` si vous êtes dans `/app`.

2.  **Créer et Activer un Environnement Virtuel**:
    Il est fortement recommandé d'utiliser un environnement virtuel. Si vous en avez créé un dans `/tmp/ifc-visualizer-venv` lors des étapes précédentes :
    ```bash
    # python3 -m venv /tmp/ifc-visualizer-venv # Si création d'un nouveau
    source /tmp/ifc-visualizer-venv/bin/activate
    ```
    Ou, si vous créez localement dans `ifc-visualizer` (plus conventionnel) :
    ```bash
    # cd /app/ifc-visualizer
    # python3 -m venv venv
    # source venv/bin/activate
    ```
    *(Sous Windows, utilisez `venv\Scripts\activate`)*

3.  **Installer les Dépendances**:
    Installez tous les paquets requis en utilisant le fichier `requirements.txt` situé dans `/app/ifc-visualizer/`.
    ```bash
    pip install -r /app/ifc-visualizer/requirements.txt
    ```
    *(Le paquet `ifcopenshell` peut avoir des prérequis spécifiques en fonction de votre SE. Veuillez consulter le [guide d'installation d'IfcOpenShell](http://ifcopenshell.org/python) si vous rencontrez des problèmes.)*

## Lancement de l'Application

1.  **Activez l'Environnement Virtuel** (par ex., `source /tmp/ifc-visualizer-venv/bin/activate`).

2.  **Naviguez vers le Répertoire `/app`**:
    Le script de l'application `src/app.py` est exécuté depuis le répertoire `/app`.
    ```bash
    cd /app
    ```

3.  **Exécutez l'Application Dash**:
    ```bash
    python ifc-visualizer/src/app.py
    ```
    Alternativement, si vous êtes dans `/app/ifc-visualizer`:
    ```bash
    python src/app.py
    ```

4.  **Accédez à l'Application**:
    Ouvrez votre navigateur web et naviguez vers l'adresse affichée dans le terminal, habituellement :
    [http://127.0.0.1:8050/](http://127.0.0.1:8050/)

## Utilisation

1.  **Téléversez un Fichier IFC**: Glissez-déposez votre fichier IFC dans la zone de téléversement, ou cliquez pour sélectionner un fichier depuis votre système. Le fichier est temporairement stocké dans `/tmp/ifc_uploads/` pendant le traitement.
2.  **Sélectionnez un Type d'Objet**: Une fois le fichier traité, un menu déroulant sera peuplé avec tous les types d'objets uniques trouvés dans le fichier. Sélectionnez un type d'objet dans cette liste.
3.  **Visualisez les Propriétés**: Le tableau sous le menu déroulant affichera les propriétés de tous les éléments appartenant au type d'objet sélectionné. Vous pouvez naviguer entre les pages s'il y a de nombreux éléments.
4.  **Visualisation 3D**: Actuellement, cette section est un espace réservé et n'affiche pas le modèle 3D réel.

---

Ce README fournit un guide de base pour comprendre, configurer et exécuter l'application Visualiseur de Données IFC.
