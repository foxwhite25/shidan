from hoshino import R, Service, priv, util
from .lib import *
from datetime import datetime

qid_dict = load_config()
date = False  # 是否令日期影响结果（测试结果每天不一样）

sv_help = '''
shindanmaker在线测试
[（@bot）测一测] 为自己进行测试 后接at可帮他人测试~
[看看测一测列表] 查看当前启用的测试列表
[添加测一测] 增加新的测一测关键词（管理限定）
'''.strip()

sv = Service("shindan", bundle="娱乐", help_=sv_help)


@sv.on_prefix("测一测")
async def on_input_new(bot, ev, ):
    msg = ev.message.extract_plain_text().strip()
    sender = ev.sender
    name = sender["card"] or sender["nickname"]
    if msg == '':
        await bot.send(ev, '请后接想测的测试名！使用[看看测一测列表]命令查看当前启用的测试列表~')
        return
    if msg in qid_dict and msg != "热门测试":
        name, rn = await get_name(bot, ev, name)
        text_list, b64s = await get_data(qid_dict[msg], rn)
        result = str(text_list.replace(rn, name))
        for each in b64s:
            result += f"[CQ:image,file={each}]\n"
        await bot.send(ev, result)
    elif msg[:4] == "热门测试":
        top_index = int(msg[4:]) if msg[4:] else 0
        name, rn = await get_name(bot, ev, name)
        text_list, b64s = await get_data(top_index, rn)
        result = str(text_list.replace(rn, name))
        for each in b64s:
            result += f"[CQ:image,file={each}]\n"
        await bot.send(ev, result)
    else:
        await bot.send(ev, '未找到该测试……使用[看看测一测列表]命令查看当前启用的测试列表~')


async def get_name(bot, ev, name):
    arr = []
    for i in ev.message:
        if i["type"] == "at" and i["data"]["qq"] != "all":
            arr.append(int(i["data"]["qq"]))
    gid = ev.group_id
    for uid in arr:
        info = await bot.get_group_member_info(group_id=gid, user_id=uid, no_cache=True)
        name = info["card"] or info["nickname"]
    if date:
        now = datetime.now()
        rn = name + str([now.year, now.month, now.day])
    else:
        rn = name
    return name, rn


@sv.on_keyword("测一测列表")
async def check_query_dict(bot, ev, ):
    msg = '当前测一测关键词列表：\n'
    for qid in qid_dict:
        msg = msg + f"{qid}：https://shindanmaker.com/{qid_dict[qid]}\n"
    msg = msg + '热门测试：默认当前最高热度测试。后接相应id可指定任意测试~'
    try:
        await bot.send(ev, msg)
    except:
        msg = msg.replace('https://shindanmaker.com/', '')
        await bot.send(ev, msg)


@sv.on_prefix('添加测一测')
async def add_query(bot, ev):
    global qid_dict
    msg = ev.message.extract_plain_text().strip()
    gid = ev.group_id
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, '此命令仅维护组可用，请联系维护组~')
        return
    msg.replace('：', ':')
    key = msg.split(':')[0]
    id = msg.split(':')[1]
    qid_dict[key] = id
    save_config(qid_dict)
    await bot.send(ev, f'已添加新测试关键词：\n{key}：qid={id}')
