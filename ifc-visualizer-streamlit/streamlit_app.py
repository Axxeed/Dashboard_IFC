import streamlit as st
import pandas as pd
import ifc_parser # Assumes ifc_parser.py is in the same directory
import os
import logging

# Configure logging for the Streamlit app
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

# --- Page Configuration ---
st.set_page_config(
    page_title="Visualiseur de Données IFC (Streamlit)",
    layout="wide"
)

# --- Main Application ---
st.title("Visualiseur de Données IFC avec Streamlit")

# --- Instructions Expander ---
with st.expander("ℹ️ Comment utiliser cette application", expanded=False):
    st.markdown("""
        1.  **Téléversez votre fichier IFC**: Utilisez le bouton ci-dessous pour choisir un fichier `.ifc` depuis votre ordinateur.
        2.  **Attendez le traitement**: L'application va charger et analyser le fichier. Cela peut prendre quelques instants pour les gros fichiers.
        3.  **Informations du projet**: Si un nom de projet est trouvé dans le fichier, il sera affiché.
        4.  **Explorez les types d'objets**:
            *   Un menu déroulant apparaîtra avec tous les types d'objets uniques (par exemple, `IfcWall`, `IfcDoor`) trouvés dans votre fichier.
            *   Sélectionnez un type d'objet dans ce menu.
        5.  **Consultez les propriétés**:
            *   Un tableau affichera les propriétés des éléments du type sélectionné.
            *   Pour des raisons de performance, seules les propriétés des 50 premiers éléments sont affichées par défaut.
        6.  **Distribution des types**: Un graphique à barres montre le nombre d'occurrences pour chaque type d'objet dans le fichier.
    """)
    st.caption("Note : Le traitement des fichiers et l'extraction des données sont optimisés grâce à la mise en cache. Les chargements répétés du même fichier ou la sélection répétée des mêmes types d'objets devraient être plus rapides après la première fois.")

# --- File Upload ---
uploaded_file = st.file_uploader("Choisissez un fichier IFC (.ifc) pour l'analyse", type=["ifc"])
st.caption("Après le téléversement, les types d'objets détectés apparaîtront dans le menu déroulant ci-dessous.")

# Define a fixed path for the temporary file
TEMP_IFC_FILE_PATH = "/tmp/streamlit_uploaded_ifc.ifc" # Using a common temp location

if uploaded_file is not None:
    logging.info(f"File uploaded: {uploaded_file.name}")
    # Save uploaded_file to a temporary file on disk for ifcopenshell
    try:
        with open(TEMP_IFC_FILE_PATH, "wb") as f:
            f.write(uploaded_file.getbuffer())
        logging.info(f"Uploaded file saved temporarily to: {TEMP_IFC_FILE_PATH}")

        # Load IFC file using the parser (should be cached by the parser)
        ifc_file = ifc_parser.load_ifc_file(TEMP_IFC_FILE_PATH)

        if ifc_file is None:
            st.error("Erreur : Le fichier téléversé ne semble pas être un fichier IFC valide ou n'a pas pu être lu. Veuillez vérifier le fichier et réessayer.")
            logging.error(f"Failed to load IFC from {TEMP_IFC_FILE_PATH} via ifc_parser. It might be invalid or corrupted.")
        else:
            st.success(f"Fichier IFC '{uploaded_file.name}' chargé et analysé avec succès!")
            logging.info("IFC file loaded successfully into Streamlit app.")

            # Display basic file information (e.g., Project Name)
            try:
                project_elements = ifc_parser.get_elements_by_type(ifc_file, "IfcProject")
                if project_elements and hasattr(project_elements[0], 'Name') and project_elements[0].Name:
                    project_name = project_elements[0].Name
                    st.subheader(f"Nom du Projet : {project_name}")
                else:
                    st.info("Aucun nom de projet (élément IfcProject avec un attribut 'Name') trouvé dans le fichier IFC.")
            except Exception as e:
                st.warning(f"Impossible d'extraire le nom du projet : {e}")
                logging.warning(f"Could not extract project name: {e}")

            st.markdown("---")

            # --- Object Type Selection and Property Display ---
            st.header("Exploration des Objets IFC")
            object_types_list = ifc_parser.get_object_types(ifc_file)

            if not object_types_list:
                st.warning("Aucun type d'objet n'a été trouvé dans ce fichier IFC. Le fichier pourrait être vide ou ne pas contenir d'entités IFC typiques.")
            else:
                selected_type = st.selectbox(
                    "Sélectionnez un type d'objet à inspecter :",
                    options=object_types_list,
                    index=None,
                    placeholder="Choisissez un type d'objet..."
                )
                st.caption("Le tableau ci-dessous affichera les propriétés des éléments du type sélectionné.")


                if selected_type:
                    st.write(f"Affichage des propriétés pour les objets de type : **{selected_type}**")

                    elements = ifc_parser.get_elements_by_type(ifc_file, selected_type)
                    if not elements:
                        st.info(f"Aucun élément trouvé pour le type '{selected_type}'.")
                    else:
                        st.write(f"Nombre d'éléments trouvés : {len(elements)}")

                        all_props_list = []
                        MAX_ELEMENTS_TO_PROCESS = 50
                        for i, elem in enumerate(elements):
                            if i < MAX_ELEMENTS_TO_PROCESS:
                                props = ifc_parser.get_element_properties(elem)
                                all_props_list.append(props)
                            else:
                                st.caption(f"Affichage des propriétés des {MAX_ELEMENTS_TO_PROCESS} premiers éléments sur {len(elements)}. "
                                           f"Pour analyser plus d'éléments, une modification du code source est nécessaire.")
                                break

                        if all_props_list:
                            try:
                                df = pd.DataFrame(all_props_list)

                                preferred_cols_order = ['StepId', 'GlobalId', 'Name', 'IfcType']
                                existing_cols = [col for col in preferred_cols_order if col in df.columns]
                                remaining_cols = sorted([col for col in df.columns if col not in existing_cols])
                                final_cols_order = existing_cols + remaining_cols

                                st.dataframe(df[final_cols_order], height=300, use_container_width=True)
                            except Exception as e_df:
                                st.error(f"Erreur lors de la création du DataFrame des propriétés : {e_df}")
                                logging.error(f"Error creating DataFrame: {e_df}")
                        else:
                            st.info(f"Aucune propriété extractible ou aucun élément avec des propriétés substantielles trouvé pour le type '{selected_type}'.")

            st.markdown("---")
            st.header("Distribution des Types d'Objets")
            try:
                counts = {}
                for elem_count_obj in ifc_file:
                    try:
                        elem_type = elem_count_obj.is_a()
                        counts[elem_type] = counts.get(elem_type, 0) + 1
                    except AttributeError:
                        continue

                if counts:
                    counts_df = pd.DataFrame(list(counts.items()), columns=['Type d\'Objet', 'Nombre'])
                    counts_df = counts_df.sort_values(by='Nombre', ascending=False)

                    top_n_chart = 20
                    if len(counts_df) > top_n_chart:
                        st.caption(f"Affichage des {top_n_chart} types d'objets les plus fréquents dans le graphique.")
                        counts_df_display = counts_df.head(top_n_chart)
                    else:
                        counts_df_display = counts_df

                    st.bar_chart(counts_df_display.set_index('Type d\'Objet'))
                else:
                    st.info("Impossible de générer le graphique de distribution: aucun type d'objet comptabilisable trouvé.")

            except Exception as e_chart:
                st.warning(f"Erreur lors de la génération du graphique des types d'objets : {e_chart}")
                logging.warning(f"Error generating object type chart: {e_chart}")

    except Exception as e_global:
        st.error(f"Une erreur globale est survenue lors du traitement du fichier '{uploaded_file.name if uploaded_file else 'inconnu'}': {e_global}. Cela peut être dû à un problème avec le fichier lui-même ou une erreur interne de l'application.")
        logging.error(f"Global error processing file {uploaded_file.name if uploaded_file else 'N/A'}: {e_global}", exc_info=True)

else:
    st.info("Veuillez téléverser un fichier IFC pour commencer l'analyse.")
    st.caption("Les formats supportés sont `.ifc`, `.ifczip`, `.ifcxml` (selon la configuration d'IfcOpenShell).")


# To run this Streamlit app:
# 1. Ensure your virtual environment (/tmp/ifc-visualizer-streamlit-venv) is activated.
#   `source /tmp/ifc-visualizer-streamlit-venv/bin/activate`
# 2. Navigate to the directory `/app/ifc-visualizer-streamlit/`.
#   `cd /app/ifc-visualizer-streamlit`
# 3. Run the command: `streamlit run streamlit_app.py`
