from src.backend import Danmac5DB
import os

db = Danmac5DB(os.getcwd() + "/data/danmac5.db")

def test_search_rsid1():
    res = db.search_rsid(["male", "all", "female"], ["rs371194064"])
    assert len(res) == 2

def test_search_rsid2():
    res = db.search_rsid(["male"], ["rs00000"])
    assert len(res) == 0

def test_search_pos():
    res = db.search_pos(["all"], "chrX", (1, 10100))
    assert len(res) == 7
