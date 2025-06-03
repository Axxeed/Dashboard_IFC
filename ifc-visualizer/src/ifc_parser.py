import ifcopenshell
import ifcopenshell.util.element
import logging
import time # For timestamp in OwnerHistory
from ifcopenshell import guid # For creating GUIDs

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_ifc_file(file_path: str) -> ifcopenshell.file | None:
    """
    Loads an IFC file from the given file path.

    Args:
        file_path: The path to the IFC file.

    Returns:
        An ifcopenshell.file object if successful, None otherwise.
    """
    try:
        ifc_file = ifcopenshell.open(file_path)
        logging.info(f"Successfully loaded IFC file: {file_path}")
        return ifc_file
    except Exception as e:
        logging.error(f"Error loading IFC file {file_path}: {e}")
        return None

def get_object_types(ifc_file: ifcopenshell.file) -> list[str]:
    """
    Retrieves a list of unique object types from the IFC file.

    Args:
        ifc_file: An ifcopenshell.file object.

    Returns:
        A list of unique object type strings (e.g., "IfcWall", "IfcDoor").
    """
    if not ifc_file:
        logging.warning("IFC file object is None. Cannot get object types.")
        return []

    object_types = set()
    for element in ifc_file: # Iterate through all entities
        object_types.add(element.is_a())

    sorted_types = sorted(list(object_types))
    logging.info(f"Found {len(sorted_types)} unique object types.")
    return sorted_types

def get_elements_by_type(ifc_file: ifcopenshell.file, object_type: str) -> list:
    """
    Retrieves all elements of a specific type from the IFC file.

    Args:
        ifc_file: An ifcopenshell.file object.
        object_type: The type of object to retrieve (e.g., "IfcWall").

    Returns:
        A list of IFC element objects of the specified type.
    """
    if not ifc_file:
        logging.warning(f"IFC file object is None. Cannot get elements for type {object_type}.")
        return []

    try:
        elements = ifc_file.by_type(object_type)
        logging.info(f"Found {len(elements)} elements of type {object_type}.")
        return elements
    except RuntimeError as e:
        # This typically happens if object_type is not a valid IFC type in the schema
        logging.warning(f"Error retrieving elements for type {object_type}: {e}. This might be an invalid IFC type.")
        return []

def get_element_properties(element) -> dict:
    """
    Retrieves the properties of a given IFC element.
    This includes GlobalId, Name, and all properties in its property sets.

    Args:
        element: An IFC element object.

    Returns:
        A dictionary of the element's properties.
    """
    if not element:
        logging.warning("Element is None. Cannot get properties.")
        return {}

    properties = {}
    try:
        properties['GlobalId'] = element.GlobalId
        properties['Name'] = element.Name if hasattr(element, 'Name') and element.Name else ''
        properties['IfcType'] = element.is_a()

        # Get properties from property sets
        psets = ifcopenshell.util.element.get_psets(element)
        for pset_name, pset_props in psets.items():
            properties[pset_name] = pset_props

        logging.info(f"Retrieved properties for element {element.GlobalId if hasattr(element, 'GlobalId') else 'Unknown ID'}")
    except Exception as e:
        logging.error(f"Error retrieving properties for element: {e}")
        # Return whatever was gathered so far, or an empty dict if critical info failed
        if not properties.get('GlobalId'): # If we couldn't even get GlobalId, it's problematic
             return {'Error': str(e)}

    if not properties: # If after all attempts, properties is still empty
        logging.warning(f"No properties found for element {element.GlobalId if hasattr(element, 'GlobalId') else 'Unknown ID'}")
        return {'Info': 'No properties found for this element.'}

    return properties

if __name__ == '__main__':
    # Example Usage (requires an IFC file for testing)
    # This section is for direct testing of the parser.

    logging.info("Starting IFC Parser module example usage...")

    # This path assumes the script is run from /app directory
    # and test.ifc will be created/looked for in /app/test.ifc
    test_file_path = "test.ifc"

    try:
        with open(test_file_path, 'r') as f:
            logging.info(f"Using existing test file: {test_file_path}")
    except FileNotFoundError:
        logging.info(f"Test file {test_file_path} not found. Creating a dummy IFC file for basic testing.")
        dummy_ifc = ifcopenshell.file(schema="IFC2X3")

        owner_history = dummy_ifc.by_type("IfcOwnerHistory")
        if not owner_history:
            person = dummy_ifc.createIfcPerson()
            organization = dummy_ifc.createIfcOrganization()
            person_and_organization = dummy_ifc.createIfcPersonAndOrganization(person, organization, None)
            application = dummy_ifc.createIfcApplication(organization, "N/A", "IfcOpenShell_Py", "IFCOS_Py")
            owner_history = dummy_ifc.createIfcOwnerHistory(
                OwningUser=person_and_organization,
                OwningApplication=application,
                ChangeAction="ADDED",
                CreationDate=int(time.time())
            )
        else:
            owner_history = owner_history[0]

        project = dummy_ifc.createIfcProject(guid.new(), OwnerHistory=owner_history, Name="Test Project")
        site = dummy_ifc.createIfcSite(guid.new(), OwnerHistory=owner_history, Name="Test Site")
        building = dummy_ifc.createIfcBuilding(guid.new(), OwnerHistory=owner_history, Name="Test Building")
        wall = dummy_ifc.createIfcWall(guid.new(), OwnerHistory=owner_history, Name="Test Wall")
        prop_values = [
            dummy_ifc.createIfcPropertySingleValue("DummyProperty", None, dummy_ifc.createIfcText("DummyValue"), None)
        ]
        pset = dummy_ifc.createIfcPropertySet(guid.new(), owner_history, "Pset_WallCommon", None, prop_values)
        dummy_ifc.createIfcRelDefinesByProperties(guid.new(), owner_history, None, None, [wall], pset)

        dummy_ifc.write(test_file_path)
        logging.info(f"Dummy IFC file created at {test_file_path}")

    ifc_file_object = load_ifc_file(test_file_path)

    if ifc_file_object:
        logging.info("-" * 30)
        object_types = get_object_types(ifc_file_object)
        logging.info(f"Unique Object Types: {object_types}")

        if "IfcWall" in object_types:
            logging.info("-" * 30)
            walls = get_elements_by_type(ifc_file_object, "IfcWall")
            if walls:
                logging.info(f"Properties for the first wall ({walls[0].GlobalId if walls else 'N/A'}):")
                wall_props = get_element_properties(walls[0])
                for key, value in wall_props.items():
                    logging.info(f"  {key}: {value}")
            else:
                logging.info("No IfcWall elements found to display properties.")
        else:
            logging.info("No IfcWall type found in the IFC file to test get_elements_by_type and get_element_properties further.")

        logging.info("-" * 30)
        non_existent_elements = get_elements_by_type(ifc_file_object, "IfcNonExistentType")
        logging.info(f"Elements of IfcNonExistentType (should be 0): {len(non_existent_elements)}")

        if "IfcProject" in object_types:
             logging.info("-" * 30)
             # Corrected function name from get_elements__by_type to get_elements_by_type
             project_elements = get_elements_by_type(ifc_file_object, "IfcProject")
             if project_elements:
                  project_props = get_element_properties(project_elements[0])
                  logging.info(f"Properties for IfcProject ({project_elements[0].GlobalId}):")
                  for key, value in project_props.items():
                       logging.info(f"  {key}: {value}")
             else:
                  logging.info("No IfcProject element found.")

        logging.info("-" * 30)
        logging.info("IFC Parser module example usage finished.")
    else:
        logging.error("Failed to load IFC file for example usage.")
