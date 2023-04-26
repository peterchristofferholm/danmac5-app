import re

from dash import Dash, html, dcc, Input, Output, State, no_update
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
## navbar, search, logo ################################################################
########################################################################################

search_box = dbc.Input(
    id="search",
    debounce=True,
    autoFocus=True,
    placeholder="Search for range, gene, or rsID...",
    list="query_suggestions",
    style={"width": "400px"},
)

search_suggestions = html.Datalist(
    id="query_suggestions",
    children=[
        html.Option(value="chr1:1002-100023"),
        html.Option(value="rs13;rs345;rs28804817"),
        html.Option(value="BRCA2"),
    ],
)

search_bar = dbc.Row(
    children=[
        dbc.Col(search_box),
        dbc.Col(dbc.Button("Query", id="btn-query", color="primary")),
        dbc.Col(dbc.Button("About", id="btn-about", color="secondary")),
    ],
    align="center",
    className="g-1 mt-2 mt-md-0",
)

navigation_bar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavItem([html.Img(src="assets/logo.png", height="50px")]),
            dbc.NavItem(search_bar),
            search_suggestions,
        ]
    )
)

########################################################################################
## about page ##########################################################################
########################################################################################

about_modal = dbc.Modal(
    [
        dbc.ModalHeader("DanMAC5", class_name="fs-3 fw-bold"),
        dbc.ModalBody(
            [
                dcc.Markdown(
                    """
                    The sequencing of 8,671 (5,418 women) individuals from three
                    independent research projects aimed at assessing genetic risk
                    factors for cardiovascular, psychiatric, and headache disorders in
                    Danish individuals.  

                    DNA sequencing was performed at deCODE genetics
                    and processed independently using the same quality control pipeline.
                    The number of carriers presented is the sum of the number of
                    carriers in three cohorts. All allele counts below 5 five have been
                    merged and reported as “<5” to protect participant privacy and
                    enable population genetics.  The position are expressed according to
                    hg38 (Genome Reference Consortium Human Build 38).  The variant ID
                    is constructed with the following structure:
                    Chromosome-Hg38position-Reference-Alternative.  Further description
                    is given in: DanMAC5: A browser of aggregated sequence variants from
                    8,671 whole genome sequenced Danish individuals, BMC Genomic Data.

                    The full dataset is available for academic use for
                    bona fide researchers via
                    [EGAD00001009756](
                        https://identifiers.org/ega.dataset:EGAD00001009756
                    )
                    upon registration via the European Genome-phenome Archive,
                    providing clear terms and conditions for use of the full
                    dataset. 
                    Please refer to the 
                    [European Genome-phenome Archive](
                        https://ega-archive.org/access/data-access
                    )
                    for details on how to register. 
                    
                    Terms of Use: DanMAC5 is available for research purposes
                    only and is provided free of charge to the research
                    community. It is not intended for diagnostic or medical use,
                    and therefore cannot be used for such purposes.
                    """
                ),
            ]
        ),
        dbc.ModalFooter("2023"),
    ],
    centered=True,
    id="about-modal",
    size="l",
    is_open=False,
)


@app.callback(
    Output("about-modal", "is_open"),
    Input("btn-about", "n_clicks"),
    State("about-modal", "is_open"),
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open


########################################################################################
## datatable ###########################################################################
########################################################################################


@app.callback(
    Output("storage", "data"),
    Input("search", "value"),
)
def update_table(search_string):
    """Once a query is send, the backend gets queried to update the datatable.

    The search_string can be either an rsID, genomic range, or a gene name. If the query
    doesn't return anything, then an informativ message should be raised.
    """
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


@app.callback(
    [
        Output("table", "data"),
        Output("error-modal", "is_open"),
    ],
    Input("storage", "data"),
)
def format_data(data):
    if len(data) == 0:
        return [], True
    else:
        return formatter(data), False


error_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("No results!")),
        dbc.ModalBody(
            dcc.Markdown(
                """
                Query returned no results.

                Try searching by genomic ranges (e.g. 'chr22:1000-20000'),
                rsIDs (e.g. 'rs76545136;rs776864762'),
                or gene names (e.g. 'BRCA2')
                """
            )
        ),
    ],
    id="error-modal",
)


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
    className="px-0 pt-3",
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

app.layout = dbc.Container(
    [navigation_bar, datatable, about_modal, error_modal, modal, storage]
)

if __name__ == "__main__":
    app.run_server(debug=True)
