import json
import logging
import os.path
import asyncio
from logging import getLogger

import aiohttp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from bs4 import BeautifulSoup
from aiologger import Logger

from scrapy_work.definition import get_character_definition


# 保存爬取到的数据到文件
def dump_to_file(obje):
    if not os.path.exists("data"):
        os.mkdir("data")
    json.dump(obje, open("data/bs.json", "w", encoding='utf-8'), ensure_ascii=False)


# 获取部首下的所有汉字
async def get_characters(bs, semaphere):
    logger = getLogger("bs-proc")
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler("bs-proc.log", encoding="utf-8"),
                            logging.StreamHandler()])
    logger.info(f"start to get characters of bs: {bs}")
    url = f"https://www.zdic.net/zd/bs/bs?bs={bs}"
    characters = {}
    async with semaphere:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                text = await response.text()
                soup = BeautifulSoup(text, "lxml")
                tasks = []
                for a in soup.find_all("a"):
                    if 'href' in a.attrs and a['href'].startswith("/hans/"):
                        logger.info(f"start to get character definition: {a.text if a.text else a['href'].split('/')[-1]}")
                        tasks.append(get_character_definition(a['href'], semaphere))
                results = await asyncio.gather(*tasks)
                for i, a in enumerate(soup.find_all("a")):
                    if 'href' in a.attrs and a['href'].startswith("/hans/"):
                        character = a.text if a.text else a['href'].split("/")[-1]
                        characters[character] = results[i]
    return characters


def process_bs(bs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    characters = loop.run_until_complete(get_characters(bs, asyncio.Semaphore(64)))
    tasks = asyncio.all_tasks(loop)
    for task in tasks:
        try:
            task.cancel()
        except asyncio.CancelledError:
            pass
    loop.close()
    return characters


# 主函数
async def main():
    loop = asyncio.get_running_loop()
    semaphere = asyncio.Semaphore(64)
    url = "https://www.zdic.net/zd/bs/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find("div", class_="nr-box").find_all("table")
    bs_dict = {table.find(class_="bsyx").text: {pck.text: '' for pck in table.find_all(class_="pck")} for table in
               tables}
    bs_list = [pck for pck_dict in bs_dict.values() for pck in pck_dict]
    with ThreadPoolExecutor(max_workers=20) as pool:
        bsul_results = pool.map(process_bs, bs_list)
    for i, bsul_result in enumerate(bsul_results):
        for j, characters in enumerate(bsul_result):
            bs_dict[list(bs_dict.keys())[i]][list(bs_dict[list(bs_dict.keys())[i]].keys())[j]] = characters
    dump_to_file(bs_dict)
