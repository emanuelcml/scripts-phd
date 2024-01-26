from dash import Dash, html, dcc, callback, Output, Input, State

import plotly.express as px
import io
import base64

from dash.exceptions import PreventUpdate

from read_sim_data import DataProcessEVP

# evp = DataProcessEVP('output_files_CPMD/biommr_cp_hidroxi.evp')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1(children='Dados da Simulação', style={'textAlign': 'center'}),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Arraste e solte ou ',
            html.A('Selecione o arquivo', style={'font-weight': 'bold'})
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
    html.Div([
        dcc.Loading(dcc.Store(id='store-session', storage_type='session'))
    ], style={'padding': '20px'}),
    html.Div(id='output-container-upload'),
    dcc.Dropdown(id='dropdown-column-data'),
    dcc.RangeSlider(allowCross=False, step=1,
                    id='nfi-range-slider'),
    dcc.Graph(id='graph-content')
])


def parse_content(content):
    content_type, content_string = content.split(',')

    decoded = base64.b64decode(content_string)
    raw_data = None

    try:
        raw_data = io.StringIO(decoded.decode('utf-8'))

        return raw_data
    except Exception as e:
        print(e)
        return raw_data


@callback(
    Output('store-session', 'data'),
    Output('output-container-upload', 'children'),
    Output('dropdown-column-data', 'options'),
    Output('dropdown-column-data', 'value'),
    Output('nfi-range-slider', 'min'),
    Output('nfi-range-slider', 'max'),
    Output('nfi-range-slider', 'marks'),
    Output('graph-content', 'figure', allow_duplicate=True),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    prevent_initial_call=True
)
def load_data(content, fname):
    status_upload = ['Arquivo carregado: {}'.format(fname if fname is not None else 'Não há')]

    if content is None:
        # return status_upload, [''], '', 0, 0, {}, None
        raise PreventUpdate

    raw_data = parse_content(content)
    evp = DataProcessEVP(raw_data=raw_data)

    dropdown_options = evp.data.columns.unique()
    dropdown_value = 'etot'
    slider_min = min(evp.data['nfi'])
    slider_max = max(evp.data['nfi'])
    steps_range = (slider_max - slider_min) / 10
    slider_marks = {i: str(i) for i in range(int(min(evp.data['nfi'])), int(max(evp.data['nfi'])), int(steps_range))}

    return (evp.data.to_dict(), status_upload, dropdown_options, dropdown_value,
            slider_min, slider_max, slider_marks, px.line(evp.data, x='nfi', y='etot'))


@callback(
    Output('graph-content', 'figure'),

    Input('nfi-range-slider', 'value'),
    Input('dropdown-column-data', 'value'),

    State('store-session', 'data'),

    prevent_initial_call=True
)
def update_graph(range_slider, drop_value, data):
    import pandas as pd
    df = pd.DataFrame().from_dict(data)

    if range_slider is None:
        range_slider = [min(df.nfi), max(df.nfi)]

    dff = df.iloc[range_slider[0]:range_slider[-1], :]

    return px.line(dff, x='nfi', y=drop_value)


if __name__ == '__main__':
    app.run(debug=True)
