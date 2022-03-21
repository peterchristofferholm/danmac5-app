import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

cur = con.cursor(cursor_factory=RealDictCursor, name=f"py-{os.getpid()}", scrollable=True)
cur.itersize = 200

class Remote():
    def __init__(self):
        self.con = psycopg2.connect()

    def update_cursor(self, ):

    def construct_query(self, pop):
        query = sql.SQL(
            """
	    select chromosome, pos, ref, alt, info from {tbl}
	    """
        ).format(
            tbl=sql.Identifier(f"sumstats_{pop}")
        )
        return query







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
