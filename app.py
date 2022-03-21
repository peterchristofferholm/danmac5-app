import dash
from dash import Dash, html, dcc, Input, Output
from dash.dash_table import DataTable

import os
import pandas as pd

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

app = Dash(__name__)

pool = ThreadedConnectionPool(minconn=5, maxconn=20)

con = psycopg2.connect()
cur = con.cursor(
    cursor_factory=RealDictCursor, name=f"py-{os.getpid()}", scrollable=True
)
cur.itersize = 200

PAGE_SIZE = 10

app.layout = html.Div([
    html.Div([
        html.Label("Population"),
        dcc.RadioItems(
            ["all", "female", "male"], "all", id="btn-1"
        )
    ], style={"padding" : 10, "flex" : 1}),
    html.Br(),
    DataTable(
        id="datatable", page_current=0, page_size=PAGE_SIZE, page_action="custom"
    )
])


@app.callback(
    Output("datatable", "data"),
    Input("btn-1", "value"),
    Input("datatable", "page_current"),
    Input("datatable", "page_size")
)
def update_table(population, page_current, page_size):

    ctx = dash.callback_context

    if not ctx.triggered or ctx.triggered[0]["prop_id"] == "btn-1.value":
        cur.execute(sql.SQL("""
	    select chromosome, pos, ref, alt, info from {tbl}
	    """).format(
		tbl=sql.Identifier(f"sumstats_{population}")
	))

    cur.scroll(page_current*page_size, mode="absolute")
    return cur.fetchmany(page_size)


if __name__ == '__main__':
    app.run_server(debug=True)
