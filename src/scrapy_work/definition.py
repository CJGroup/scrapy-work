import aiohttp
from bs4 import BeautifulSoup, NavigableString


def extract_text_without_tags(element):
    texts = []
    for child in element.descendants:
        if isinstance(child, NavigableString):
            texts.append(str(child).strip())
    return ' '.join(texts)


async def get_character_definition(url, semaphere):
    url = "https://www.zdic.net" + url
    definition = {}
    async with semaphere:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                text = await response.text()
                soup = BeautifulSoup(text, "lxml")
                if len(soup.find_all("div", attrs={"data-type-block": "基本解释"})) > 0:
                    div = soup.find("div", attrs={"data-type-block": "基本解释"})
                    content = div.find("div", class_="content")
                    definition["basic"] = extract_text_without_tags(content).strip("《汉典》")

                if len(soup.find_all("div", attrs={"data-type-block": "详细解释"})) > 0:
                    outer_div = soup.find("div", attrs={"data-type-block": "详细解释"})
                    content = outer_div.find("div", class_="content")
                    definition["detail"] = extract_text_without_tags(content).strip("《汉典》")

                if len(soup.find_all("div", attrs={"data-type-block": "康熙字典"})) > 0:
                    outer_div = soup.find("div", attrs={"data-type-block": "康熙字典"})
                    content = outer_div.find("div", class_="content")
                    definition["kangxi"] = extract_text_without_tags(content).strip("《汉典》")

                if len(soup.find_all("div", attrs={"data-type-block": "说文解字"})) > 0:
                    outer_div = soup.find("div", attrs={"data-type-block": "说文解字"})
                    content = outer_div.find("div", class_="content")
                    definition["shuowen"] = extract_text_without_tags(content).strip("《汉典》")
    return definition
