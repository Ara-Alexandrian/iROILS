# Import required libraries
import dash
import pandas as pd
from dash import html, dash_table
from flask import Flask
from sqlalchemy import create_engine

# Initialize Flask app
server = Flask(__name__)

# Initialize Dash app
app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')

# Database connection parameters
db_params = {
    'dbname': 'iroils_db',
    'user': 'iroils_user',
    'password': '3Carrot^^^',
    'host': '192.168.1.8',
    'port': '5432'
}

# Function to fetch data from PostgreSQL
def fetch_data(query):
    engine = create_engine(f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}")
    df = pd.read_sql(query, engine)
    return df

# Example query to fetch data
query = "SELECT * FROM full_events;"

# Fetch data
df = fetch_data(query)

# Dash app layout with sidebar and DataTable
app.layout = html.Div([
    # Sidebar
    html.Div([
        html.Button("Open Selection", id="open-selection", n_clicks=0),
        html.Button("Filters", id="filters", n_clicks=0),
        html.Button("Mark for Review", id="mark-for-review", n_clicks=0)
    ], style={
        'position': 'fixed',  # Fixed position
        'top': 0,  # Align to the top of the viewport
        'left': 0,  # Align to the left of the viewport
        'background-color': '#333333',  # Dark charcoal background
        'width': '20%',  # Width of sidebar
        'height': '100vh',  # Full height of the viewport
        'display': 'flex',
        'flexDirection': 'column',
        'padding': '10px',
        'color': 'white'
    }),
    
    # Main content
    html.Div([
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            style_table={
                'maxWidth': '100%',
                'overflowX': 'auto'
            },
            style_cell={
                'whiteSpace': 'normal',
                'height': 'auto',
                'minWidth': 'fit-content',
                'maxWidth': '0',
                'textAlign': 'left'
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': 'narrative'},
                    'textAlign': 'left',
                    'width': '50%'
                }
            ]
        )
    ], style={
        'marginLeft': '20%',  # Add left margin equivalent to the width of the sidebar
        'width': '80%',  # Width of main content
        'float': 'right',
        'padding': '20px'
    })
], style={'display': 'flex', 'flexDirection': 'row'})


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
