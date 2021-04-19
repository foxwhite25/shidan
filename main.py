from .lib import *
from datetime import datetime

qid_dict = {"今天是什么少女": 162207, "异世界转生": 587874, "性格": 567341, "马娘相性": 1059404, "卖萌": 360578, "热门测试": 000000}


@sv.on_message()
async def on_input_new(bot, ev):
    msg = ev.message.extract_plain_text()
    sender = ev.sender
    name = sender["card"] or sender["nickname"]
    for each, qid in qid_dict.items():
        if each in msg:
            break
    else:
        return
    if msg in qid_dict and msg != "热门测试":
        arr = []
        for i in ev.message:
            if i["type"] == "at" and i["data"]["qq"] != "all":
                arr.append(int(i["data"]["qq"]))
        gid = ev.group_id
        for uid in arr:
            info = await bot.get_group_member_info(group_id=gid, user_id=uid, no_cache=True)
            name = info["card"] or info["nickname"]
        text_list, b64s = get_data(qid_dict[msg], name)
        for each in b64s:
            text_list += f"[CQ:image,file={each}]\n"
        await bot.send(ev, str(text_list))
    elif msg[:4] == "热门测试":
        arr = []
        top_index = int(msg[4:]) if msg[4:] else 0
        for i in ev.message:
            if i["type"] == "at" and i["data"]["qq"] != "all":
                arr.append(int(i["data"]["qq"]))
        gid = ev.group_id
        for uid in arr:
            info = await bot.get_group_member_info(group_id=gid, user_id=uid, no_cache=True)
            name = info["card"] or info["nickname"]
        text_list, b64s = get_hot(top_index, name)
        for each in b64s:
            text_list += f"[CQ:image,file={each}]\n"
        await bot.send(ev, str(text_list))
