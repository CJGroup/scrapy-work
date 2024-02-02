import json
import os.path
import asyncio

from requests import get
from bs4 import BeautifulSoup

from scrapy_work.definition import get_character_definition


# 保存爬取到的数据到文件
def dump_to_file(obje):
    if not os.path.exists("data"):
        os.mkdir("data")
    json.dump(obje, open("data/bs.json", "w", encoding='utf-8'), ensure_ascii=False)


# 获取部首下的所有汉字
async def get_characters(bs):
    url = "https://www.zdic.net/zd/bs/bs?bs=" + bs
    soup = BeautifulSoup(get(url).text, "lxml")
    characters = {}
    print(bs)
    for a in soup.find_all("a"):
        if 'href' in a.attrs and a['href'].startswith("/hans/"):
            character = a.text if a.text else a['href'].split("/")[-1]
            url = a['href']
            characters[character] = character
    return characters


# 主函数
def main():
    url = "https://www.zdic.net/zd/bs/"
    loop = asyncio.get_event_loop()
    html = get(url).text
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find("div", class_="nr-box").find_all("table")
    bs_dict = {table.find(class_="bsyx").text: {pck.text: '' for pck in table.find_all(class_="pck")} for table in
               tables}
    bsul_tasks = []
    for bsyx, pck_dict in bs_dict.items():
        pck_tasks = []
        for pck in pck_dict:
            pck_tasks.append(get_characters(pck))
        bsul_tasks.append(asyncio.gather(*pck_tasks))
    bsul_results = loop.run_until_complete(asyncio.gather(*bsul_tasks))
    for i, bsul_result in enumerate(bsul_results):
        for j, characters in enumerate(bsul_result):
            bs_dict[list(bs_dict.keys())[i]][list(bs_dict[list(bs_dict.keys())[i]].keys())[j]] = characters

    dump_to_file(bs_dict)
