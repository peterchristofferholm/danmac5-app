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

    def search_rsid(
            self, strata : list[str], rsids : list[str]
        ) -> list[dict]:

        # dynamically add placeholders because sqlite3 lib sucks
        query = """
            select * from danmac5
             where strata in ({x1})
               and id in ({x2})
            order by chrom, pos, strata
            limit 5000
            """.format(
            x1 = ", ".join("?" * len(strata)),
            x2 = ", ".join("?" * len(rsids)),
        )
        cur = self.con.cursor()
        # bind parameters
        cur.execute(query, strata + rsids)
        return cur.fetchall()

    def search_pos(
            self, strata : list[str], chromosome : str,
            position : tuple[int, int]
        ) -> list[dict]:

        # dynamically add placeholders
        query = """
            select * from danmac5
             where strata in ({x1})
               and chrom = ?
               and pos >= ?
               and pos <= ?
            order by chrom, pos, strata
            limit 5000
            """.format(
            x1 = ", ".join("?" * len(strata))
        )

        cur = self.con.cursor()
        # bind parameters
        cur.execute(query, (*strata, chromosome, *position))
        return cur.fetchall()
