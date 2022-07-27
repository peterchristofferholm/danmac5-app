import dash
from dash import Dash, html, dcc, Input, Output
from dash.dash_table import DataTable

import dash_bootstrap_components as dbc

import os
import re

from src.backend import Danmac5DB
from src.formatter import formatter

###############################################################################

# connect to sqlite3 database
db = Danmac5DB("assets/data/danmac5.db")

# cached storage for current session
storage = dcc.Store(id="storage")

# initalize app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

###############################################################################
# navbar, search, logo

search_bar = dbc.Row(
    children=[
        dbc.Col(
            dbc.Input(id="search",
                debounce=True, autoFocus=True,
                placeholder="Search for region or variants...",
                pattern="^(chr(\d{1,2}|[XY]):\d+-\d+|(rs(\d+)[;, ])*(rs\d+))$",
                list="query_suggestions",
                style={"width" : "400px"}
            ),
        ),
        dbc.Col(
            dbc.Button("Query", color="primary"),
        ),
    ],
    align="center",
    className="g-1 mt-2 mt-md-0"
)

search_suggestions = html.Datalist(id="query_suggestions", children=[
    html.Option(value="chr1:1002-10023"),
    html.Option(value="rs13;rs345")
])


@app.callback(
    Output("storage", "data"), Input("search", "value")
)
def update_table(search_string):

    if not search_string:
        search_string = "chr1:1000-10900"

    if search_string.startswith("rs"):
        rsids = re.split("[;, ]+", search_string)
        data = db.search_rsid(rsids)

    if search_string.startswith("chr"):
        query = re.search("^(chr(?:[XY]|\d+)):(\d+)-(\d+)$", search_string)
        chromosome = query.group(1)
        position = (int(query.group(2)), int(query.group(3)))
        data = db.search_pos(chromosome, position)

    return data


navigation_bar = dbc.Navbar(
    dbc.Container([
        dbc.Row([html.Img(src="assets/logo.png", height="50px")]),
        search_bar, search_suggestions
    ])
)


###############################################################################
# datatable

@app.callback(
    Output("table", "data"),
    Input("storage", "data")
)
def format_data(data):
    return formatter(data)

datatable = dbc.Row(
    [
        DataTable(
            id="table",

            # pagination setup
            page_action="native", page_current=0, page_size=15,
            cell_selectable=False,

            style_cell={
                "textAlign" : "left",
            },

            style_cell_conditional=[
                { "if" : {"column_id" : ["variant_id", "rsid"]},
                    "width" : "35%", "minWidth" : "35%", "maxWidth" : 0,
                    "textOverflow" : "ellipsis", "overflow" : "hidden",
                }
            ]
        )
    ],
    className="px-2 pt-3"
)

###############################################################################

app.layout = dbc.Container([
    navigation_bar,
    datatable,
    storage
])

if __name__ == "__main__":
    app.run_server(debug=True, port=80, host="0.0.0.0")
