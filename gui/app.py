import dash
from dash import html, dcc, dash_table, Output, Input, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import requests
import plotly.express as px

# Adresy backendów
CONTROLLER_API = "http://localhost:3001/api/games"
COLLECTOR_API = "http://localhost:3002/collect"

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Steam Games Dashboard"

def load_games():
    try:
        res = requests.get(CONTROLLER_API)
        res.raise_for_status()
        data = res.json()
        return pd.DataFrame(data)
    except Exception as e:
        print("Błąd pobierania danych:", e)
        return pd.DataFrame()

app.layout = dbc.Container([
    html.H1("Steam Games Dashboard", className="my-4 text-center"),

    dbc.Row([
        dbc.Button("🔄 Zbierz dane z kolektora", id="collect-button", color="primary", className="mb-3"),
        dbc.Button("🗑️ Usuń wszystkie gry", id="delete-button", color="danger", className="mb-3 ms-2"),
    ]),
    dbc.Alert(id="alert", is_open=False),
    dcc.Store(id='game-store'),
    dash_table.DataTable(
    id='games-table',
    columns=[
        {'name': 'Nazwa', 'id': 'name', 'presentation': 'markdown'},
        {'name': 'Gracze', 'id': 'players', 'type': 'numeric'},
        {'name': 'Cena (USD)', 'id': 'price', 'type': 'numeric'},
        {'name': 'Zniżka (%)', 'id': 'discount', 'type': 'numeric'}
    ],
    data=[],
    style_table={'overflowX': 'auto', 'maxHeight': '600px', 'overflowY': 'auto'},
    style_cell={
        'minWidth': '120px', 'width': '120px', 'maxWidth': '120px',
        'whiteSpace': 'normal', 'padding': '5px'
    },
    style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
    page_size=10,
    sort_action="native",
    fixed_rows={'headers': True}
    ),


    # Suwaki do filtrowania
    html.Div([
        html.Label("Minimalna liczba graczy:"),
        dcc.Slider(id='min-players', min=0, max=100_000_000, step=5_000_000, value=0,
                   marks={0: '0', 50_000_000: '50M', 100_000_000: '100M'}),

        html.Label("Maksymalna cena:"),
        dcc.Slider(id='max-price', min=0, max=100, step=1, value=100,
                   marks={0: '$0', 50: '$50', 100: '$100'}),
    ], style={'marginTop': 20, 'marginBottom': 20}),

    # Wykresy
    dcc.Graph(id='price-vs-players'),
    dcc.Graph(id='discount-histogram'),
], fluid=True)

@app.callback(
    Output("game-store", "data"),
    Output("games-table", "data"),
    Output("alert", "children"),
    Output("alert", "color"),
    Output("alert", "is_open"),
    Input("collect-button", "n_clicks"),
    Input("delete-button", "n_clicks"),
    prevent_initial_call=True
)
def update_table(collect_clicks, delete_clicks):
    ctx = callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    try:
        if trigger_id == 'collect-button':
            requests.post(COLLECTOR_API)
            df = load_games()
            return df.to_dict('records'), df.to_dict('records'), "Dane zostały zaktualizowane", "success", True

        elif trigger_id == 'delete-button':
            res = requests.delete(CONTROLLER_API)
            if res.status_code == 200:
                return [], [], "Wszystkie dane zostały usunięte", "warning", True
            else:
                return [], [], "Wszystkie dane zostały usunięte", "warning", True

    except Exception as e:
        return [], f"Błąd: {str(e)}", "danger", True


@app.callback(
    Output("price-vs-players", "figure"),
    Output("discount-histogram", "figure"),
    Input("game-store", "data"),
    Input("min-players", "value"),
    Input("max-price", "value")
)
def update_graphs(data, min_players, max_price):
    if not data:
        empty_fig = px.scatter(title="Brak danych")
        return empty_fig, empty_fig

    df = pd.DataFrame(data)
    filtered = df[(df['players'] >= min_players) & (df['price'] <= max_price)]

    fig1 = px.scatter(filtered, x='players', y='price', hover_data=['name'], title="Cena vs Liczba Graczy")
    fig2 = px.histogram(filtered, x='discount', nbins=10, title="Histogram Zniżek (%)")

    return fig1, fig2

if __name__ == "__main__":
    app.run(debug=True)
