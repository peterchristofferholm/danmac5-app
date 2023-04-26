def _format(row):
    out = {}
    out["varID"] = row["VARID"]
    out["rsID"] = row["RSID"]
    out["GENE"] = row["GENE"]

    out["CLNDISDB"] = "\n".join(row["CLNDISDB"].split(","))

    out["CLNALLELEID"] = row["CLNALLELEID"]
    out["CLNDN"] = row["CLNDN"]
    out["CLNSIG"] = row["CLNSIG"]
    out["GENE_FUNCTION"] = row["GENE_FUNCTION"]
    out["EXON_FUNCTION"] = row["EXON_FUNCTION"]
    out["AA_CHANGE"] = row["AA_CHANGE"]

    out["MAC"] = row["MAC_ALL"]

    # if rsid := row["id"]:
    #     _row["rsid"] = f"[{rsid}](https://www.ncbi.nlm.nih.gov/snp/{rsid})"
    # else:
    #     _row["rsid"] = "&mdash;"

    # _row["all"] = row["all"]
    # _row["female"] = row["female"]
    # _row["male"] = row["male"]
    return out


def formatter(data):
    return [_format(row) for row in data]
