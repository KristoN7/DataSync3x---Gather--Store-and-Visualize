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

    dbc.Button("🔄 Zbierz dane z kolektora", id="collect-button", color="primary", className="mb-3"),
    dbc.Alert(id="alert", is_open=False),

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
        dcc.Slider(id='min-players', min=0, max=1000000, step=50000, value=0,
                   marks={0: '0', 500000: '500k', 1000000: '1M'}),

        html.Label("Maksymalna cena:"),
        dcc.Slider(id='max-price', min=0, max=100, step=1, value=100,
                   marks={0: '$0', 50: '$50', 100: '$100'}),
    ], style={'marginTop': 20, 'marginBottom': 20}),

    # Wykresy
    dcc.Graph(id='price-vs-players'),
    dcc.Graph(id='discount-histogram'),
], fluid=True)

@app.callback(
    Output("games-table", "data"),
    Output("alert", "children"),
    Output("alert", "color"),
    Output("alert", "is_open"),
    Input("collect-button", "n_clicks"),
    Input("games-table", "id")
)
def update_table(n_clicks, table_id):
    ctx = callback_context
    if not ctx.triggered:
        # wywołanie na starcie - załaduj dane
        df = load_games()
        return df.to_dict('records'), "", "", False
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == 'collect-button':
            try:
                requests.post(COLLECTOR_API)
                df = load_games()
                if df.empty:
                    raise Exception("Brak danych z API")
                return df.to_dict('records'), "Dane zostały zaktualizowane", "success", True
            except Exception as e:
                return [], f"Błąd: {str(e)}", "danger", True
        else:
            df = load_games()
            return df.to_dict('records'), "", "", False

@app.callback(
    Output("price-vs-players", "figure"),
    Output("discount-histogram", "figure"),
    Input("min-players", "value"),
    Input("max-price", "value")
)
def update_graphs(min_players, max_price):
    df = load_games()
    if df.empty:
        empty_fig = px.scatter(title="Brak danych")
        return empty_fig, empty_fig

    filtered = df[(df['players'] >= min_players) & (df['price'] <= max_price)]

    fig1 = px.scatter(filtered, x='players', y='price', hover_data=['name'], title="Cena vs Liczba Graczy")
    fig2 = px.histogram(filtered, x='discount', nbins=10, title="Histogram Zniżek (%)")

    return fig1, fig2

if __name__ == "__main__":
    app.run(debug=True)
