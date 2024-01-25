from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
from read_sim_data import DataProcessEVP

evp = DataProcessEVP('output_files_CPMD/biommr_cp_hidroxi.evp')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1(children='Dados de Energia Total', style={'textAlign': 'center'}),
    dcc.Input(placeholder='Plotar a partir de ...',
              type='number', min=0, max= int(max(evp.data['nfi'])),
              id='input-nfi'),
    dcc.Graph(id='graph-content')
])

@callback(
    Output('graph-content', 'figure'),
    # Input('nfi-range-slider', 'value')
    Input('input-nfi', 'value')
)
def update_graph(value=0):
    if value is None:
        value = 0

    plot_range = list(map(float, range( value, int(max(evp.data.nfi)) )))
    dff = evp.data.iloc[plot_range, :]
    return px.line(dff, x='nfi', y='etot')

if __name__ == '__main__':
    app.run(debug=True)