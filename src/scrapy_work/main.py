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
    json.dump(obje, open("data/bs.json", "w", encoding='utf-8'), ensure_ascii=False, indent=4)


# 获取部首下的所有汉字
async def get_characters(bs, semaphere):
    logger = getLogger("bs-proc")
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler("out.log", encoding="utf-8"),
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
                        tasks.append(get_character_definition(a['href'], semaphere))
                results = await asyncio.gather(*tasks)
                i = 0
                for a in soup.find_all("a"):
                    if 'href' in a.attrs and a['href'].startswith("/hans/"):
                        character = a.text if a.text else a['href'].split("/")[-1]
                        characters[character] = results[i]
                        i += 1
    logger.info(f"finish getting characters of bs: {bs}")
    return characters


def process_bs(bs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)
    characters = loop.run_until_complete(get_characters(bs, asyncio.Semaphore(32)))
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
    url = "https://www.zdic.net/zd/bs/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find("div", class_="nr-box").find_all("table")
    bs_dict = {table.find(class_="bsyx").text: {pck.text: '' for pck in table.find_all(class_="pck")} for table in
               tables}
    bs_list = [pck for pck_dict in bs_dict.values() for pck in pck_dict]
    bs_bsyx_mapping = {bs: bsyx_count for bsyx_count, bs_dict_per_bsyx in bs_dict.items() for bs in
                       bs_dict_per_bsyx}
    with ThreadPoolExecutor(max_workers=4) as pool:
        bsul_results = list(pool.map(process_bs, bs_list))
    for bs, characters in zip(bs_list, bsul_results):
        stroke_count = bs_bsyx_mapping[bs]  # 获取当前部首对应的笔画数
        bs_dict[stroke_count][bs] = characters
    dump_to_file(bs_dict)
