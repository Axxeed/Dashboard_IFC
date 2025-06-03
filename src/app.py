import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import base64
import io
import os
import pandas as pd # For easier table manipulation later if needed
import logging # For logging within callbacks

# ifc_parser.py is in the same directory (src)
import ifc_parser # Changed from relative to direct import

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True) # Suppress exceptions for now for dynamic layout parts
app.title = "IFC Data Visualizer"

# Configure basic logging for the app
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')


# Define a directory for uploads
UPLOAD_DIRECTORY = "/tmp/ifc_uploads"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Basic styling for components
styles = {
    'container': {
        'maxWidth': '960px',
        'margin': 'auto',
        'padding': '20px',
        'fontFamily': 'Arial, sans-serif'
    },
    'title': {
        'textAlign': 'center',
        'marginBottom': '30px'
    },
    'upload': {
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'padding': '20px',
        'marginBottom': '20px'
    },
    'dropdown': {
        'marginBottom': '20px'
    },
    'table': {
        'marginBottom': '20px'
    },
    'graph': {
        'height': '400px', # Placeholder height
        'border': '1px solid lightgrey'
    }
}

# Define the layout of the app
app.layout = html.Div(
    style=styles['container'],
    children=[
        dcc.Store(id='ifc-file-path-store'), # To store the path to the uploaded IFC file
        # dcc.Store(id='ifc-elements-store'), # To store current elements (optional, for optimization)

        html.H1(
            "IFC Data Visualizer",
            style=styles['title']
        ),

        dcc.Upload(
            id='upload-ifc-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select an IFC File')
            ]),
            style=styles['upload'],
            multiple=False  # Allow only single file upload
        ),

        html.Div(id='output-file-info', style={'marginBottom': '10px', 'minHeight': '20px'}),
        html.Div(id='output-error-message', style={'marginBottom': '10px', 'color': 'red', 'minHeight': '20px'}),

        dcc.Loading(
            id="loading-dropdown",
            type="circle", # or "default", "cube", "dot"
            children=[
                dcc.Dropdown(
                    id='object-type-dropdown',
                    placeholder="Select Object Type (e.g., IfcWall)",
                    style=styles['dropdown'],
                    options=[] # Options will be populated by a callback based on the uploaded IFC file
                )
            ]
        ),

        html.H3("Object Properties", style={'marginTop': '30px'}),
        dcc.Loading(
            id="loading-table",
            type="circle",
            children=[
                dash_table.DataTable(
                    id='properties-table',
                    columns=[], # Columns will be populated by a callback
                    data=[],
                    page_size=10,
                    style_table={'overflowX': 'auto', 'minWidth': '100%'},
                    style_cell={
                        'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                    }
                ),
                html.Div(id='table-loading-output', style={'marginTop': '10px', 'minHeight': '20px'}) # Can display text like "Displaying X elements"
            ]
        ),

        html.H3("3D Visualization (Placeholder)", style={'marginTop': '30px'}),
        dcc.Graph(
            id='ifc-visualizer-graph',
            style=styles['graph'],
            figure={ # Placeholder figure
                'layout': {
                    'title': '3D Model Placeholder',
                    'xaxis': {'visible': False},
                    'yaxis': {'visible': False},
                    'annotations': [{
                        'text': '3D visualization will appear here.',
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {'size': 16}
                    }]
                }
            }
        )
    ]
)

def parse_contents(contents, filename):
    """Helper function to parse uploaded file content and save it."""
    if not contents:
        return None, "No file content provided."

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    # Save the decoded file to a temporary path
    # This path will be stored and used by other callbacks
    temp_file_path = os.path.join(UPLOAD_DIRECTORY, filename)

    try:
        with open(temp_file_path, 'wb') as f:
            f.write(decoded)

        ifc_file = ifc_parser.load_ifc_file(temp_file_path)
        if not ifc_file:
            # Clean up the invalid file
            try:
                os.remove(temp_file_path)
                logging.info(f"Removed invalid uploaded file: {temp_file_path}")
            except OSError as e_rm:
                logging.error(f"Error removing invalid file {temp_file_path}: {e_rm}")
            return None, f"Error parsing IFC file: {filename}. The file was invalid and has been removed. Please ensure it is a valid IFC."

        return temp_file_path, None # Return path and no error
    except Exception as e:
        logging.error(f"Error processing uploaded file {filename}: {e}")
        return None, f"An error occurred while processing the file: {str(e)}"

@app.callback(
    [Output('ifc-file-path-store', 'data'),
     Output('output-file-info', 'children'),
     Output('object-type-dropdown', 'options'),
     Output('object-type-dropdown', 'value'), # Reset dropdown value
     Output('properties-table', 'data'), # Clear table
     Output('properties-table', 'columns'), # Clear table columns
     Output('output-error-message', 'children')],
    [Input('upload-ifc-data', 'contents')],
    [State('upload-ifc-data', 'filename')]
)
def update_on_upload(contents, filename):
    if contents is None:
        # No file uploaded yet, or upload component just initialized.
        # Using dash.no_update for outputs that shouldn't change.
        # Clear any previous error messages.
        return dash.no_update, "No file uploaded yet.", [], None, [], [], ""

    logging.info(f"File upload attempt: {filename}")

    temp_file_path, error_msg_from_parse = parse_contents(contents, filename)

    if error_msg_from_parse:
        logging.error(f"File processing error for {filename}: {error_msg_from_parse}")
        # Update output-file-info to be neutral, error message to output-error-message
        return (None, # Stored file path
                "File processing failed.", # output-file-info
                [], # Dropdown options
                None, # Dropdown value
                [], # Table data
                [], # Table columns
                f"Failed to process '{filename}': {error_msg_from_parse}") # output-error-message

    # File successfully parsed and saved by parse_contents
    # Re-load the IFC file to get the ifcopenshell file object for further processing
    ifc_file_obj = ifc_parser.load_ifc_file(temp_file_path)
    if not ifc_file_obj:
        # This case should ideally be caught by parse_contents, but as a safeguard:
        critical_error_msg = f"Critical error: Could not re-load IFC file '{filename}' after initial successful parse and save."
        logging.error(critical_error_msg)
        return (None,
                "File loading error after saving.",
                [], None, [], [],
                critical_error_msg)

    object_types = ifc_parser.get_object_types(ifc_file_obj)
    dropdown_options = [{'label': ot, 'value': ot} for ot in object_types]

    success_file_info = f"Successfully processed: {filename}"
    logging.info(success_file_info)

    return (temp_file_path,
            success_file_info, # output-file-info
            dropdown_options,
            None, # Reset dropdown selection
            [], # Clear table data
            [], # Clear table columns
            "") # Clear error message

# Callback to update properties table based on dropdown selection
@app.callback(
    [Output('properties-table', 'data'),
     Output('properties-table', 'columns'),
     Output('table-loading-output', 'children'),
     Output('output-error-message', 'children', allow_duplicate=True)], # Allow duplicate for error reporting
    [Input('object-type-dropdown', 'value')],
    [State('ifc-file-path-store', 'data')],
    prevent_initial_call=True # Important: do not run on startup
)
def update_properties_table(selected_object_type, stored_file_path):
    ctx = dash.callback_context
    if not ctx.triggered or not selected_object_type or not stored_file_path:
        return [], [], "Select an object type to see properties.", ""

    logging.info(f"Updating properties table for type '{selected_object_type}' from file '{stored_file_path}'")
    loading_msg = f"Loading properties for {selected_object_type}..."

    ifc_file = ifc_parser.load_ifc_file(stored_file_path)
    if not ifc_file:
        error_msg = "Error: Could not load stored IFC file. Please try uploading again."
        logging.error(error_msg + f" Path: {stored_file_path}")
        return [], [], "", error_msg

    elements = ifc_parser.get_elements_by_type(ifc_file, selected_object_type)
    if not elements:
        return [], [], f"No elements found for type {selected_object_type}.", ""

    all_props_list = []
    for elem in elements:
        props = ifc_parser.get_element_properties(elem)
        # Ensure all property values are simple types (str, number, bool) for Dash DataTable
        # Complex objects or nested dicts within property values need careful handling.
        # For now, we assume get_element_properties returns a flat dict with simple values,
        # or string representations for complex ones.
        flat_props = {}
        for key, value in props.items():
            if isinstance(value, dict): # If a pset value is a dict
                for sub_key, sub_value in value.items():
                    flat_props[f"{key}.{sub_key}"] = str(sub_value) if not isinstance(sub_value, (str, int, float, bool)) else sub_value
            else:
                flat_props[key] = str(value) if not isinstance(value, (str, int, float, bool)) else value
        all_props_list.append(flat_props)

    if not all_props_list:
        return [], [], f"No properties found for elements of type {selected_object_type}.", ""

    # Dynamically create columns based on all unique keys found in the properties
    # This handles cases where different elements of the same type might have different property sets
    all_keys = set()
    for props_dict in all_props_list:
        all_keys.update(props_dict.keys())

    # Ensure GlobalId and Name are first if they exist
    ordered_keys = []
    if 'GlobalId' in all_keys:
        ordered_keys.append('GlobalId')
        all_keys.remove('GlobalId')
    if 'Name' in all_keys:
        ordered_keys.append('Name')
        all_keys.remove('Name')
    if 'IfcType' in all_keys: # Should always be there from our parser
        ordered_keys.append('IfcType')
        all_keys.remove('IfcType')
    ordered_keys.extend(sorted(list(all_keys))) # Add remaining keys sorted

    columns = [{"name": key, "id": key} for key in ordered_keys]

    logging.info(f"Successfully prepared data for {len(all_props_list)} elements of type {selected_object_type}.")
    return all_props_list, columns, f"Displaying {len(all_props_list)} elements of type {selected_object_type}.", ""


@app.callback(
    Output('ifc-visualizer-graph', 'figure'),
    [Input('object-type-dropdown', 'value')], # Example: trigger on dropdown change
    [State('ifc-file-path-store', 'data')],
    prevent_initial_call=True
)
def update_graph_stub(selected_object_type, stored_file_path):
    logging.info(f"Graph stub update triggered: Type '{selected_object_type}', File: '{stored_file_path}'")

    title_text = '3D Model Placeholder'
    annotations_text = '3D visualization will appear here.'

    if stored_file_path and selected_object_type:
        title_text = f'Visualizing: {selected_object_type}'
        annotations_text = f'Graph for {selected_object_type} will appear here.'
    elif stored_file_path:
        title_text = 'IFC Model Loaded'
        annotations_text = 'Select an object type to visualize.'

    fig = {
        'layout': {
            'title': title_text,
            'xaxis': {'visible': False},
            'yaxis': {'visible': False},
            'annotations': [{
                'text': annotations_text,
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {'size': 16}
            }]
        }
    }
    return fig


if __name__ == '__main__':
    # app.run(debug=True) # Commented out again after final testing
    logging.info("src/app.py with file upload callback, properties table callback, and graph stub is defined.")
    logging.info("To run, uncomment app.run(debug=True) and execute `python src/app.py` from the `/app` directory with the venv activated.")
