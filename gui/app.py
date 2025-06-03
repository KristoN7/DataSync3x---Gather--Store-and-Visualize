import dash
from dash import html, dcc, dash_table, Output, Input, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import requests
import plotly.graph_objects as go
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
    
    html.Div([
        dbc.Row([
            dbc.Col([
                html.Label("Model płatności:"),
                dcc.Dropdown(
                    id='payment-filter',
                    options=[
                        {"label": "Wszystkie", "value": "all"},
                        {"label": "Free", "value": "Free"},
                        {"label": "Paid", "value": "Paid"}
                    ],
                    value='all',
                    clearable=False
                )
            ]),
            dbc.Col([
                html.Label("Zniżka aktywna:"),
                dcc.Dropdown(
                    id='sale-filter',
                    options=[
                        {"label": "Wszystkie", "value": "all"},
                        {"label": "Tak", "value": "Tak"},
                        {"label": "Nie", "value": "Nie"}
                    ],
                    value='all',
                    clearable=False
                )
            ]),
        ])
    ], style={"marginBottom": 20}),

    html.Label("Kategoria gry (na podstawie recenzji i popularności):"),
    dcc.Dropdown(
        id="category-dropdown",
        options=[
            {"label": "Wszystkie", "value": "all"},
            {"label": "Popularna", "value": "Popularna"},
            {"label": "Dobra", "value": "Dobra"},
            {"label": "Średnia", "value": "Średnia"},
            {"label": "Słaba", "value": "Słaba"},
        ],
        value="all",
        clearable=False,
        style={"marginBottom": "20px"}
    ),

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

    html.Div([
        html.Label("Minimalna liczba graczy:"),
        dcc.Slider(id='min-players', min=0, max=100_000_000, step=5_000_000, value=0,
                   marks={0: '0', 50_000_000: '50M', 100_000_000: '100M'}),

        html.Label("Maksymalna cena:"),
        dcc.Slider(id='max-price', min=0, max=100, step=1, value=100,
                   marks={0: '$0', 50: '$50', 100: '$100'}),
    ], style={'marginTop': 20, 'marginBottom': 20}),

    dcc.Graph(id='price-vs-players'),
    dcc.Graph(id='discount-histogram'),
], fluid=True)

@app.callback(
    Output("games-table", "data"),
    Output("price-vs-players", "figure"),
    Output("discount-histogram", "figure"),
    Output("alert", "children"),
    Output("alert", "color"),
    Output("alert", "is_open"),
    Input("collect-button", "n_clicks"),
    Input("delete-button", "n_clicks"),
    Input("min-players", "value"),
    Input("max-price", "value"),
    Input("payment-filter", "value"),
    Input("sale-filter", "value"),
    Input("category-dropdown", "value"),
    prevent_initial_call=True
)
def update_dashboard(n_collect, n_delete, min_players, max_price, payment_filter, sale_filter, category_value):
    ctx = callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    try:
        if trigger == "collect-button":
            requests.post(COLLECTOR_API)
            alert_msg = "Dane zostały zaktualizowane"
            alert_color = "success"
        elif trigger == "delete-button":
            res = requests.delete(CONTROLLER_API)
            print(f"DELETE status: {res.status_code}, body: {res.text}")
            if res.status_code in [200, 204]:
                empty_fig = go.Figure(layout_title_text="Brak danych")
                return [], empty_fig, empty_fig, "Wszystkie dane zostały usunięte", "warning", True
            else:
                raise Exception("Błąd podczas usuwania danych")
        else:
            alert_msg = ""
            alert_color = ""

        df = load_games()
        if 'category' not in df.columns:
            raise Exception("Brakuje kolumny 'category' w danych")
        if df.empty:
            empty_fig = go.Figure(layout_title_text="Brak danych")
            return [], empty_fig, empty_fig, "Brak danych do wyświetlenia", "warning", True

        # Filtrowanie
        filtered = df[
            (df['players'] >= min_players) &
            (df['price'] <= max_price)
        ]
        if payment_filter != "all":
            filtered = filtered[filtered["paymentModel"] == payment_filter]
        if sale_filter != "all":
            filtered = filtered[filtered["onSale"] == sale_filter]
        if category_value != "all" and "category" in filtered.columns:
            filtered = filtered[filtered["category"] == category_value]
        
        fig1 = px.scatter(filtered, x="players", y="price", hover_data=["name"], title="Cena vs Liczba Graczy")
        fig2 = px.histogram(filtered, x="discount", nbins=10, title="Histogram Zniżek (%)")

        return filtered.to_dict("records"), fig1, fig2, alert_msg, alert_color, bool(alert_msg)

    except Exception as e:
        empty_fig = go.Figure(layout_title_text="Błąd")
        return [], empty_fig, empty_fig, f"Błąd: {str(e)}", "danger", True

if __name__ == "__main__":
    app.run(debug=True)
