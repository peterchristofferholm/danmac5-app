import re

from dash import Dash, html, dcc, Input, Output, State
from dash.dash_table import DataTable
import dash_bootstrap_components as dbc

from src.backend import Danmac5DB
from src.formatter import formatter

########################################################################################

# connect to sqlite3 database
db = Danmac5DB("assets/data/danmac5.db")

# cached storage for current session
storage = dcc.Store(id="storage")

# initalize app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "DanMAC5"
server = app.server

########################################################################################
# navbar, search, logo

seach_box = dbc.Input(
    id="search",
    debounce=True,
    autoFocus=True,
    placeholder="Search for region or variants...",
    pattern="^(chr(\d{1,2}|[XY]):\d+-\d+|(rs(\d+)[;, ])*(rs\d+))$",
    list="query_suggestions",
    style={"width": "400px"},
)

search_bar = dbc.Row(
    children=[dbc.Col(seach_box), dbc.Col(dbc.Button("Query", color="primary"))],
    align="center",
    className="g-1 mt-2 mt-md-0",
)

search_suggestions = html.Datalist(
    id="query_suggestions",
    children=[html.Option(value="chr1:1002-10023"), html.Option(value="rs13;rs345")],
)

########################################################################################


@app.callback(Output("storage", "data"), Input("search", "value"))
def update_table(search_string):
    if not search_string:
        search_string = "BRCA2"

    if search_string.startswith("rs"):
        rsids = re.split("[;, ]+", search_string)
        data = db.search_rsid(rsids)

    elif search_string.startswith("chr"):
        query = re.search("^(chr(?:[XY]|\d+)):(\d+)-(\d+)$", search_string)
        chromosome = query.group(1)
        position = (int(query.group(2)), int(query.group(3)))
        data = db.search_pos(chromosome, position)

    else:
        genes = re.split("[;, ]+", search_string)
        data = db.search_gene(genes)

    return data


navigation_bar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row([html.Img(src="assets/logo.png", height="50px")]),
            search_bar,
            search_suggestions,
        ]
    )
)

###############################################################################
# datatable


@app.callback(Output("table", "data"), Input("storage", "data"))
def format_data(data):
    return formatter(data)


datatable = dbc.Row(
    [
        DataTable(
            id="table",
            # pagination setup
            page_action="native",
            page_current=0,
            page_size=20,
            # included columns
            columns=[
                {"id": "varID", "name": "variant"},
                {"id": "rsID", "name": "rsid"},
                {"id": "GENE", "name": "gene"},
                {"id": "GENE_FUNCTION", "name": "function"},
                {"id": "CLNSIG", "name": "clin. significance"},
                {"id": "MAC", "name": "allele count"},
            ],
            # styling
            cell_selectable=True,
            style_cell={
                "textAlign": "left",
                "textOverflow": "ellipsis",
                "overflow": "hidden",
                "maxWidth": 0,
            },
            style_cell_conditional=[
                {"if": {"column_id": "varID"}, "width": "20%"},
                {"if": {"column_id": "rsID"}, "width": "15%"},
            ],
            css=[{"selector": ".dash-spreadsheet td div", "rule": "margin: 0"}],
        )
    ],
    className="px-2 pt-3",
)

########################################################################################

modal = dbc.Modal(id="modal", size="xl", is_open=False)


@app.callback(
    Output("modal", "children"),
    [
        Input("table", "data"),
        Input("table", "active_cell"),
        Input("table", "page_size"),
        Input("table", "page_current"),
    ],
)
def set_content(data: list[dict], selected, page_size, page_current):
    if selected:
        idx = (page_size * page_current) + selected["row"]
        row = data[idx]

        return [
            dbc.ModalHeader(row.pop("varID")),
            dbc.ModalBody(
                dbc.ListGroup(
                    [dbc.ListGroupItem(f"{k}: {v}") for (k, v) in row.items()]
                )
            ),
        ]


@app.callback(
    Output("modal", "is_open"),
    Input("table", "active_cell"),
    State("modal", "is_open"),
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open


###############################################################################

app.layout = dbc.Container([navigation_bar, datatable, modal, storage])

if __name__ == "__main__":
    # app.run_server(debug=False, port=80, host="0.0.0.0")
    app.run_server(debug=True)
