import asyncio
from collections import Generator
from typing import List, Callable, Dict
import bs4
from hoshino import aiorequests as requests
# import aiorequests as requests
import os
import json

from requests.structures import CaseInsensitiveDict
from bs4 import BeautifulSoup, NavigableString, Tag
from urllib.parse import urlencode

cmds: Dict[str, Callable] = {}

configpath = os.path.join(os.path.dirname(__file__), 'config.json')


def save_config(config: dict):
    try:
        with open(configpath, 'w', encoding='utf8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as ex:
        print(ex)
        return False


def load_config():
    try:
        with open(configpath, 'r', encoding='utf8') as f:
            config = json.load(f)
            return config
    except:
        return {}


async def get_data(qid, name):
    curl = "https://shindanmaker.com/790697"
    r = await requests.get(url=curl)
    _session = r.cookies["_session"]
    bs = BeautifulSoup(await r.content, "lxml")
    _token = bs.find("input", {"name": "_token"})["value"]
    dat = {"_token": _token, "name": name, "hiddenName": name}
    data = urlencode(dat)
    headers = CaseInsensitiveDict()
    headers[
        "accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    headers["accept-encoding"] = "gzip, deflate, br"
    headers["accept-language"] = "zh-CN,zh;q=0.9"
    headers["cache-control"] = "max-age=0"
    headers[
        "cookie"] = f'XSRF-TOKEN=eyJpdiI6InVzeTcxTVVWSGdSV0FZWlhYcHJ2dnc9PSIsInZhbHVlIjoiTlNjcU1PSGNsQW45UzZkdFFMOTNvUlNRUnA2RDZJTVE5WFBtenpzVUNvck5pbEJuU2JDQ3dmT1FxUWhSbFBYbStGekUyMkJOWkd2ZUl3OE5oZzZkL05QRi9va3VQT2IveEh4TkhZckhUM3dqOEF5Tm9XOHNxUkllQUs5MzY2Tk8iLCJtYWMiOiJiMTU1Yzg5ZjRhNmJhOGY1NmQwNjk3NjU0YTY1Zjg3M2FjMTA4N2JmMTIxNjllNTQ5NzMyMGI2ZGRlMDhjY2Y2In0%3D; _session={_session}; _ga=GA1.2.1909781615.1623072110; _gid=GA1.2.430553544.1623072110; _gat_UA-19089743-2=1; _gat_UA-19089743-3=1; trc_cookie_storage=taboola%2520global%253Auser-id%3Dcd0cb1ff-0f1f-40a3-a822-34776946f0c7-tuct7a540db; _cc_id=1d7df23098ca447f1626f1eb6565a938; panoramaId_expiry=1623676919500; panoramaId=924346e1a38521439fd01667f35e4945a702e31f147ee20eac516d362b81d68f'
    headers["origin"] = "https://shindanmaker.com"
    headers["referer"] = f"https://shindanmaker.com/a/{qid}"
    headers[
        "user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    url = f"https://shindanmaker.com/{qid}"
    resp = await requests.post(url, headers=headers, data=data, timeout=10)
    soup = BeautifulSoup(await resp.content, "html.parser")
    soup = soup.find("div", {"name": "shindanResultBlock"})
    tags = soup.findAll("img")
    text = get_text(soup).replace("\n\n\n", "\n").replace('診断結果', '診断結果\n')
    imgs = set(tag["src"] for tag in tags)
    img_list = []
    for each in imgs:
        img_list.append(each.replace("data:image/jpeg;base64,", "base64://"))
    return text, img_list


async def get_hot(top_index=0, name=""):
    # https://shindanmaker.com/list
    if top_index < 29:
        headers = {
            "cookie": "_ga=GA1.2.440539836.1618304269; trc_cookie_storage=taboola%20global%3Auser-id=93ee8d5f-c5f4-48c6-924e-77da1e414e4a-tuct648ba0b; dui=eyJpdiI6IlhzQjJ1WnVoVkNFZ1Y1OXBKNlg2WVE9PSIsInZhbHVlIjoiVVhtZ1NTZWYxV2sxaC9aVmRncXNuREo1NTlteGNtVnZGQ1cyNFY4OHcxNldudWV5ZlZBbHJLL2pZZkk3aVQ0dTJ0djl2a0ROSW5jc1NBMXVHUHphejdxVld3bnNvQmw4bTkwMmJxK0VhQ01FT3ArV1ZEUGdqdWNlMW83VGlKa29QT2JjRVZzaXhhT2hiN3ViZHpMTkd3PT0iLCJtYWMiOiI5YzliZTlhMTk3NmE5YjMxMDc4NjNhNWZkZmQ4ZGEzYTg3ZDNmMzUzOGJhOGFmYWJiMmVlZjFiZDZiNjliOWM0In0=; _session=Xx4quie6qLKs5fady8KHb1QEDQ4EB1E2njevwZm7; _gid=GA1.2.1163823230.1618686436; dsr=eyJpdiI6Ijk2ZUNsVzR0czNqVjAwZ0gwRW8wZEE9PSIsInZhbHVlIjoiRGtiQng4MXBLdzRBbWltZWkrWW9hYXdERkZ1cmJNVThzSzFXcTU5Y1pDNjBqREpnamx5MzdydFhNUkhOWXNyTWRqc2psVmVmL0YvYm1EOWR5TWswVnc9PSIsIm1hYyI6ImIzYjczMWEyNTRmMTBjYWVjN2JlM2NiOGI2MDAxMjA0NGZjNzFjNmJiNTU1NGFlYzY5ZjRmMDcyMmY0NzI2M2YifQ==; name=eyJpdiI6IkFBMnE1cTkva1NrV3dxSEJSeE9tblE9PSIsInZhbHVlIjoiYmRlV1Npamh4RnkyRWdDYUhCN3ZFWHVVYUFRQXZBMEVYK1dTRzhBWmwzMWgzT2JodkdnQ3pPK0pxSDZIZXB1MUhHSi9mTXFzTVJFRS9Faks2UEwrSmc9PSIsIm1hYyI6IjhlNDk0NjI4MWEyMjFiNjhmYTQ5YzkzZDU0MDc4OTE0YTI4MTllZTg3NTA3NzA3NDBhOTVkZWVlNjcxN2Q2MGMifQ==; __gads=ID=daef441bdb6bf998:T=1618690556:S=ALNI_MY5PC9DMGtCGddfsjZmX-qQwnJo7Q; XSRF-TOKEN=eyJpdiI6IjFTdDZ6YzN5UWlYeVlBZHBNbHVpM0E9PSIsInZhbHVlIjoiU01rd2tHSnJRUkVtL2NGa1ZOYVN4c0U5bEVNNmw4TjFzd2VmQ09CNTVySE91RXFhSWhiWnRldE5vMThReFIzbytVQ0djUXBPZjRGeCtqRVlEam5JZmpRN0t3bDFVL3IzR3pGK3crM3JVOGZsdW1KckZOdEFTTS9BNDE4QSs4c3giLCJtYWMiOiJhMGZjMTQyNWIxMGI5NzUxODcwZTFkMmQ5MDIyNzc2OTY3YWI3MmE4NGFkNjg4YWYwYWIwMGNjN2JlNzQ3YjZkIn0=",
        }
        resp = await requests.get(url="https://shindanmaker.com/list", headers=headers)
        soup = bs4.BeautifulSoup(await resp.text, "html.parser")
        hot = soup.find_all("div", {"class": "shindanLink"})[top_index]
        title = hot.text
        reply = f"当前热门测试：{title}\n"
        text, img_list = await get_data(hot["href"].removeprefix("https://shindanmaker.com/"), name)
    else:
        reply = ""
        text, img_list = await get_data(top_index, name)
    return reply + text, img_list


def process_text_list(text, name):
    temp = ""
    for each in text:
        if each != name:
            temp += each + "\n"
        else:
            temp += each
    return temp


def get_text(tag: bs4.Tag) -> str:
    _inline_elements = {
        "a",
        "span",
        "em",
        "strong",
        "u",
        "i",
        "font",
        "mark",
        "label",
        "s",
        "sub",
        "sup",
        "tt",
        "bdo",
        "button",
        "cite",
        "del",
        "b",
        "a",
        "font",
    }

    def _get_text(tag: bs4.Tag) -> Generator:

        for child in tag.children:
            if type(child) is Tag:
                # if the tag is a block type tag then yield new lines before after
                is_block_element = child.name not in _inline_elements
                if is_block_element:
                    yield "\n"
                yield from ["\n"] if child.name == "br" else _get_text(child)
                if is_block_element:
                    yield "\n"
            elif type(child) is NavigableString:
                yield child.string

    return "".join(_get_text(tag))
