import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class Danmac5DB():

    def __init__(self, path : str) -> None:
        self.con = sqlite3.connect(path, check_same_thread=False)
        self.con.row_factory = dict_factory

    def search_rsid(self, rsids : list[str]) -> list[dict]:

        # dynamically add placeholders because sqlite3 lib sucks
        query = """
            select * from danmac5
             where id in ({xs})
             order by chrom, pos
            limit 5000
            """.format(
            xs = ", ".join("?" * len(rsids)),
        )
        cur = self.con.cursor()
        # bind parameters
        cur.execute(query, rsids)
        return cur.fetchall()

    def search_pos(
            self, chromosome : str, position : tuple[int, int]
        ) -> list[dict]:

        # prepare statement
        query = """
            select * from danmac5
             where chrom = ?
               and pos >= ?
               and pos <= ?
            order by chrom, pos
            limit 5000
            """
        cur = self.con.cursor()
        # bind parameters
        cur.execute(query, (chromosome, *position))
        return cur.fetchall()
