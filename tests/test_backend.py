from src.backend import Danmac5DB
import os

db = Danmac5DB(os.getcwd() + "/data/danmac5.db")

def test_search_rsid1():
    res = db.search_rsid(["rs371194064"])
    assert len(res) == 1 and len(res[0]) == 8

def test_search_rsid2():
    res = db.search_rsid(["rs00000"])
    assert len(res) == 0

def test_search_rsid3():
    res = db.search_rsid(["rs144773400", "rs200690549", "rs199910572"])
    assert len(res) == 3

def test_search_pos():
    res = db.search_pos("chrX", (1, 10100))
    assert len(res) == 7
