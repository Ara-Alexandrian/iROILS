# Import required libraries
from flask import Flask
import dash
from dash import html, dcc
import plotly.graph_objs as go
import psycopg2
import pandas as pd

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
    conn = psycopg2.connect(**db_params)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Example query (modify as needed)
query = "SELECT * FROM full_events LIMIT 5;"

# Dash layout
app.layout = html.Div([
    dcc.Graph(id='example-graph'),
    # Add more components as needed
])

# Dash callback (example)
@app.callback(
    dash.dependencies.Output('example-graph', 'figure'),
    [dash.dependencies.Input('your-input-component', 'value')]
)
def update_graph(input_value):
    # Fetch data based on the input or other triggers
    df = fetch_data(query)
    return {
        'data': [go.Scatter(
            x=df['x_column'],
            y=df['y_column'],
            mode='markers'
        )],
        'layout': go.Layout(
            title='Your Graph Title',
            xaxis={'title': 'X Axis'},
            yaxis={'title': 'Y Axis'}
        )
    }

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)


