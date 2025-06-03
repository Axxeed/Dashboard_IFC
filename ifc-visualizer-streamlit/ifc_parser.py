import ifcopenshell
import ifcopenshell.util.element
import logging
import time # For timestamp in OwnerHistory
from ifcopenshell import guid # For creating GUIDs
import streamlit as st # Added for Streamlit caching decorators
import os # Added for __main__ block path joining

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

# --- Caching Configuration ---
IFC_HASH_FUNCS = {
    ifcopenshell.file: lambda _: id(_),
    ifcopenshell.entity_instance: lambda elem: elem.id()
}

# --- Decorated Functions ---

@st.cache_resource(show_spinner="Loading IFC file...")
def load_ifc_file(file_path: str) -> ifcopenshell.file | None:
    logging.info(f"CACHE MISS or RECALC: load_ifc_file('{file_path}')")
    try:
        ifc_file = ifcopenshell.open(file_path)
        logging.info(f"Successfully loaded IFC file: {file_path}")
        return ifc_file
    except Exception as e:
        logging.error(f"Error loading IFC file {file_path}: {e}")
        return None

@st.cache_data(show_spinner="Extracting object types...", hash_funcs=IFC_HASH_FUNCS)
def get_object_types(ifc_file: ifcopenshell.file) -> list[str]:
    logging.info(f"CACHE MISS or RECALC: get_object_types(ifc_file id: {id(ifc_file)})")
    if not ifc_file:
        logging.warning("IFC file object is None. Cannot get object types.")
        return []

    object_types = set()
    for element in ifc_file:
        try:
            object_types.add(element.is_a())
        except AttributeError:
            logging.debug(f"Skipping non-entity or item with no is_a() method: {type(element)}")
            continue

    sorted_types = sorted(list(object_types))
    logging.info(f"Found {len(sorted_types)} unique object types.")
    return sorted_types

@st.cache_resource(show_spinner="Fetching elements by type...", hash_funcs=IFC_HASH_FUNCS)
def get_elements_by_type(ifc_file: ifcopenshell.file, object_type: str) -> list:
    logging.info(f"CACHE MISS or RECALC: get_elements_by_type(ifc_file id: {id(ifc_file)}, type: '{object_type}')")
    if not ifc_file:
        logging.warning(f"IFC file object is None. Cannot get elements for type {object_type}.")
        return []

    try:
        elements = ifc_file.by_type(object_type)
        logging.info(f"Found {len(elements)} elements of type {object_type}.")
        return elements
    except RuntimeError as e:
        logging.warning(f"Error retrieving elements for type {object_type}: {e}. This might be an invalid IFC type.")
        return []

@st.cache_data(show_spinner="Extracting element properties...", hash_funcs=IFC_HASH_FUNCS)
def get_element_properties(element: ifcopenshell.entity_instance) -> dict:
    logging.info(f"CACHE MISS or RECALC: get_element_properties(element id: {element.id() if element else 'None'})")
    if not element:
        logging.warning("Element is None. Cannot get properties.")
        return {}

    properties = {}
    try:
        properties['GlobalId'] = element.GlobalId
        properties['Name'] = element.Name if hasattr(element, 'Name') and element.Name else ''
        properties['IfcType'] = element.is_a()
        properties['StepId'] = element.id()

        # Corrected: Removed include_quantity_sets=True
        psets = ifcopenshell.util.element.get_psets(element)
        for pset_name, pset_props in psets.items():
            flat_pset_props = {}
            for prop_name, prop_value in pset_props.items():
                if hasattr(prop_value, 'wrappedValue'):
                    flat_pset_props[prop_name] = prop_value.wrappedValue
                elif isinstance(prop_value, ifcopenshell.entity_instance):
                    flat_pset_props[prop_name] = f"{prop_value.is_a()}(#{prop_value.id()})"
                else:
                    flat_pset_props[prop_name] = prop_value
            properties[pset_name] = flat_pset_props

    except Exception as e:
        logging.error(f"Error retrieving properties for element #{element.id() if element else 'unknown'}: {e}")
        if not properties.get('GlobalId'):
             return {'Error': str(e), 'StepId': element.id() if element else 0}

    if not properties.get('GlobalId') and 'Error' not in properties:
        logging.warning(f"No substantial properties found for element {element.id() if element else 'Unknown ID'}")
        return {'Info': 'No substantial properties found for this element.', 'StepId': element.id() if element else 0}

    return properties

if __name__ == '__main__':
    logging.info("Starting IFC Parser module example usage (simulating Streamlit caching with prints)...")

    module_dir = os.path.dirname(__file__) if '__file__' in locals() else '.'
    test_file_path = os.path.join(module_dir, "streamlit_parser_test.ifc")

    logging.info(f"Looking for/creating test IFC file at: {os.path.abspath(test_file_path)}")

    if not os.path.exists(test_file_path):
        logging.info(f"Test file {test_file_path} not found. Creating a dummy IFC file for basic testing.")
        try:
            dummy_ifc = ifcopenshell.file(schema="IFC2X3")
            owner_history_list = dummy_ifc.by_type("IfcOwnerHistory")
            owner_history = owner_history_list[0] if owner_history_list else None
            if not owner_history:
                person = dummy_ifc.createIfcPerson()
                organization = dummy_ifc.createIfcOrganization()
                person_and_organization = dummy_ifc.createIfcPersonAndOrganization(person, organization, None)
                application = dummy_ifc.createIfcApplication(organization, "N/A", "IfcOpenShell_Py_Test", "IFCOS_Test")
                owner_history = dummy_ifc.createIfcOwnerHistory(
                    OwningUser=person_and_organization, OwningApplication=application,
                    ChangeAction="ADDED", CreationDate=int(time.time())
                )

            project = dummy_ifc.createIfcProject(guid.new(), OwnerHistory=owner_history, Name="Test Project")
            dummy_ifc.createIfcSite(guid.new(), OwnerHistory=owner_history, Name="Test Site")
            dummy_ifc.createIfcBuilding(guid.new(), OwnerHistory=owner_history, Name="Test Building")
            wall = dummy_ifc.createIfcWall(guid.new(), OwnerHistory=owner_history, Name="Test Wall")
            prop_values = [dummy_ifc.createIfcPropertySingleValue("DummyProperty", None, dummy_ifc.createIfcText("DummyValue"), None)]
            pset = dummy_ifc.createIfcPropertySet(guid.new(), owner_history, "Pset_WallCommon", None, prop_values)
            dummy_ifc.createIfcRelDefinesByProperties(guid.new(), owner_history, None, None, [wall], pset)
            dummy_ifc.write(test_file_path)
            logging.info(f"Dummy IFC file created at {test_file_path}")
        except Exception as e:
            logging.error(f"Failed to create dummy IFC file for testing: {e}")
            ifcopenshell.file = None # type: ignore

    if os.path.exists(test_file_path):
        print("\n--- Simulating First Run ---")
        start_time_run1 = time.perf_counter()
        ifc_file_run1 = load_ifc_file(test_file_path)
        print(f"load_ifc_file (1st) took {time.perf_counter() - start_time_run1:.4f}s")

        if ifc_file_run1:
            obj_types_run1 = get_object_types(ifc_file_run1)
            print(f"get_object_types (1st) found: {obj_types_run1[:5] if obj_types_run1 else 'None'}...")

            if "IfcWall" in obj_types_run1:
                walls_run1 = get_elements_by_type(ifc_file_run1, "IfcWall")
                print(f"get_elements_by_type('IfcWall') (1st) found {len(walls_run1)} walls.")
                if walls_run1:
                    props_run1 = get_element_properties(walls_run1[0])
                    print(f"get_element_properties(wall) (1st) props: {list(props_run1.keys())[:5] if props_run1 else 'None'}...")

            print("\n--- Simulating Second Run (expecting CACHE MISS logs again as Streamlit context is absent) ---")
            start_time_run2 = time.perf_counter()
            ifc_file_run2 = load_ifc_file(test_file_path)
            print(f"load_ifc_file (2nd) took {time.perf_counter() - start_time_run2:.4f}s")

            if ifc_file_run2:
                obj_types_run2 = get_object_types(ifc_file_run2)
                print(f"get_object_types (2nd) found: {obj_types_run2[:5] if obj_types_run2 else 'None'}...")

                if "IfcWall" in obj_types_run2:
                    walls_run2 = get_elements_by_type(ifc_file_run2, "IfcWall")
                    print(f"get_elements_by_type('IfcWall') (2nd) found {len(walls_run2)} walls.")
                    if walls_run2:
                        props_run2 = get_element_properties(walls_run2[0])
                        print(f"get_element_properties(wall) (2nd) props: {list(props_run2.keys())[:5] if props_run2 else 'None'}...")
        else:
            logging.error("Failed to load IFC file for testing, cannot proceed with caching simulation.")
    else:
        logging.error(f"Test file {test_file_path} does not exist. Cannot run simulation.")

    logging.info("IFC Parser module example usage finished.")
