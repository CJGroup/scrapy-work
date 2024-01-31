import json
import os.path

from requests import get
from bs4 import BeautifulSoup


def dump_to_file(obje):
    if not os.path.exists("data"):
        os.mkdir("data")
    json.dump(obje, open("data/bs.json", "w"), ensure_ascii=False, indent=4)


def main():
    url = "https://www.zdic.net/zd/bs/"
    html = get(url).text
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find("div", class_="nr-box").find_all("table")
    bs_dict = {}
    for table in tables:
        bsyx = table.find(class_="bsyx").text
        bsul = []
        for pck in table.find_all(class_="pck"):
            bsul.append(pck.text)
        bs_dict[bsyx] = bsul
    dump_to_file(bs_dict)
