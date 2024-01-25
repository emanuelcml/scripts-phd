from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
from read_sim_data import DataProcessEVP

evp = DataProcessEVP('output_files_CPMD/biommr_cp_hidroxi.evp')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1(children='Dados de Energia Total', style={'textAlign': 'center'}),
    dcc.RangeSlider(min(evp.data['nfi']),
                    max(evp.data['nfi']),
                    step=1,
                    marks={i: str(i) for i in range(int(min(evp.data['nfi'])),
                    int(max(evp.data['nfi'])), 500)},
                    allowCross=False,
                    id='nfi-range-slider'),
    html.Div(id='output-container-range-slider'),
    dcc.Graph(id='graph-content')
])

@callback(
    Output('graph-content', 'figure'),
    Output('output-container-range-slider', 'children'),
    Input('nfi-range-slider', 'value')
)
def update_graph(value):
    if value is None:
        value = [int(min(evp.data['nfi'])), int(max(evp.data['nfi']))]

    texto_debug = 'Intervalo de passos de execução: "{}"'.format(value)
    dff = evp.data.iloc[value[0]:value[-1], :]
    return px.line(dff, x='nfi', y='etot'), texto_debug

if __name__ == '__main__':
    app.run(debug=True)