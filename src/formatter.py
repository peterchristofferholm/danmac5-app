def _format(row):
    _row = {}
    _row["variant_id"] = "-".join((
        str(row.pop(k)) for k in ("chrom", "pos", "ref", "alt")))
    _row["rsid"] = row["id"] if row["id"] else "-"
    _row["all"] = row["all"]
    _row["female"] = row["female"]
    _row["male"] = row["male"]
    return _row

def formatter(data):
    return [_format(row) for row in data]
