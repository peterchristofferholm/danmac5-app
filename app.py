import dash
from dash import Dash, html, dcc, Input, Output
from dash.dash_table import DataTable

import os
import re

from src.backend import Danmac5DB

###############################################################################

# connect to sqlite3 database
db = Danmac5DB("data/danmac5.db")

app = Dash(__name__)

app.layout = html.Div([
    html.H1("DanMAC5"),
    html.Div([
        # search bar
        dcc.Input(
            id="searchbar",
            debounce=True,
            pattern="^(chr(\d{1,2}|[XY]):\d+-\d+|(rs(\d+)[;, ])*(rs\d+))$",
            placeholder="region (chr1:1002-10023) or rsIDs (rs13;rs345)",
            spellCheck="false",
            size="40"),

        # select male/female
        dcc.Checklist(
            id="strata",
            options={"male" : "♂", "female" : "♀"},
            value=["male", "female"])

        ], style={
            "padding" : 20, "gap" : 20, "display" : "flex"
        }
    ),
    html.Br(),
    DataTable(
        id="datatable",
        page_action="native",
        page_current=0,
        page_size=10
    )
])


@app.callback(
    Output("datatable", "data"),
    Input("searchbar", "value"),
    Input("strata", "value")
)
def update_table(search_string, strata):

    strata = ["all"] + strata

    if not search_string:
        search_string = "chr1:1-10500"

    if search_string.startswith("rs"):
        rsids = re.split("[;, ]+", search_string)
        data = db.search_rsid(strata, rsids)

    if search_string.startswith("chr"):
        query = re.search("^(chr(?:[XY]|\d+)):(\d+)-(\d+)$", search_string)
        chromosome = query.group(1)
        position = (int(query.group(2)), int(query.group(3)))
        data = db.search_pos(strata, chromosome, position)

    return data


if __name__ == '__main__':
    app.run_server(debug=True)
