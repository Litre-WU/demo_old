import os
import asyncio
from sanic import Sanic, response
from sanic.exceptions import NotFound
from sanic_session import Session, InMemorySessionInterface
from sanic_jinja2 import SanicJinja2
import aiohttp
import requests
from lxml import etree
from random import randint
import time
import json
from user_agent import generate_user_agent
import concurrent.futures
import qrcode

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
douban50 = os.path.join(BASE_DIR, 'static/images/douban50/')
songfile = os.path.join(BASE_DIR, 'docs/songlist.json')
WX_QRCODE = os.path.join(BASE_DIR, 'static/images/qrcode/')

app = Sanic(__name__)
app.static('/static', './static')

session = Session(app, interface=InMemorySessionInterface())

jinja = SanicJinja2(app)


async def task_sleep(): await asyncio.sleep(randint(1, 2))


def ua():
    random_ip = '.'.join(str(randint(0, 255)) for _ in range(4))
    return {"User-Agent": generate_user_agent(), "X-FORWARDED-FOR": random_ip, "X-REAL-IP": random_ip,
            "CLIENT-IP": random_ip}


async def async_ua():
    ip = '.'.join(str(randint(0, 255)) for _ in range(4))
    return {"User-Agent": generate_user_agent(), "X-FORWARDED-FOR": ip, "X-REAL-IP": ip,
            "CLIENT-IP": ip}


@app.route('/')
@jinja.template('main.html')
async def index(request):
    myLoop = request.app.loop
    myLoop.create_task(task_sleep())
    return {"title": "首页", "url": "/music/"}


@app.route('/adage/')
async def adage(request):
    myLoop = request.app.loop
    myLoop.create_task(task_sleep())
    url = 'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php'
    params = {
        "from_mid": "1",
        "format": "json",
        "ie": "utf-8",
        "oe": "utf-8",
        "subtitle": "格言",
        "query": "格言",
        "rn": "8",
        "pn": str(randint(0, 95) * 8),
        "resource_id": "6844",
        "_": str(int(time.time() * 1000)),
    }
    headers = await async_ua()
    try:
        async with aiohttp.ClientSession() as client:
            async with client.get(url=url, params=params, headers=headers) as rs:
                if rs.status == 200:
                    info = json.loads(await rs.text())
                    data_list = []
                    for a in info["data"][0]["disp_data"]:
                        data = {
                            "adage": a["ename"],
                            "author": a["author"]
                        }
                        data_list.append(data)
                    result = {
                        "data": data_list
                    }
    except Exception as e:
        print(e)
        result = {
            "msg": "不好意思,出错了！",
            "data": [{
                "adage": "知识就是力量",
                "author": "培根"
            }]
        }
    return response.json(result)


@app.route('/movie/')
@jinja.template('movie.html')
async def movie(request):
    myLoop = request.app.loop
    myLoop.create_task(task_sleep())
    url = 'https://frodo.douban.com/api/v2/subject_collection/movie_hot_gaia/items'
    params = {
        "start": "NaN",
        "count": "50",
        "apiKey": "0ac44ae016490db2204ce0a042db2916"
    }
    headers = await async_ua()
    headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat",
        "content-type": "application/json",
        "Referer": "https://servicewechat.com/wx2f9b06c1de1ccfca/82/page-frame.html",
        "Accept-Encoding": "gzip, deflate, br"})
    try:
        async with aiohttp.ClientSession() as client:
            async with client.get(url=url, params=params, headers=headers) as rs:
                if rs.status == 200:
                    info = await rs.json()
                    # print(info)
                    result = {
                        'title': "电影",
                        'url': '/movie/search',
                        'results': info,
                    }
                    for m in info["subject_collection_items"]:
                        os.makedirs(douban50, exist_ok=True)
                        img_name = douban50 + f'{m["id"]}.png'
                        if os.path.exists(img_name):
                            continue
                        img_url = m["cover"]["url"]
                        async with client.get(url=img_url, headers=headers) as img:
                            if img.status == 200:
                                info = await img.read()
                                with open(img_name, "wb+") as f:
                                    f.write(info)
                    return result

    except Exception as e:
        print(e)
        result = {
            "code": 501,
            "msg": "当前访问过于频繁！",
            "result": []
        }
        return response.json(result)


source_list = ['http://www.leduozy.com', 'http://265zy.cc', 'http://123ku.com', 'https://wolongzy.net']
source_url = source_list[0]


@app.route('/movie/search')
@jinja.template('search.html')
async def search_movie(request):
    myLoop = request.app.loop
    myLoop.create_task(task_sleep())
    keyword = dict(request.args).get("keyword", "")[0]
    if not keyword:
        result = {
            "code": 401,
            "msg": "请输入关键字",
            "result": []
        }
        return response.json(result)
    context = {
        'title': "搜索",
        'url': '/movie/search',
    }
    headers = await async_ua()
    url = f'{source_url}/index.php'
    # url = f'{source_url}/search.html'
    params = {
        "m": "vod-search"
    }
    # params = {
    #     "searchword": keyword
    # }
    data = {
        "wd": keyword
    }
    try:
        async with aiohttp.ClientSession() as client:
            async with client.post(url=url, params=params, data=data, headers=headers) as rs:
                if rs.status == 200:
                    context.update({
                        "links": etree.HTML(await rs.text()).xpath('//td[@class="l"]/a/@href'),
                    })
    except Exception as exc:
        # context["msg"]=exc
        context = {
            "code": 402,
            "msg": "抱歉！暂时无法搜索",
            "result": []
        }
        return response.json(context)

    # 异步
    tasks = [asyncio.create_task(aparse(url, 60)) for url in context["links"]]
    context["data"] = await asyncio.gather(*tasks)
    # 多线程
    # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    #     future_to_url = {executor.submit(parse, url, 60): url for url in context["links"]}
    #     context["data"] = [future.result() for future in concurrent.futures.as_completed(future_to_url)]
    #     # for future in concurrent.futures.as_completed(future_to_url):
    #     #     # url = future_to_url[future]
    #     #     try:
    #     #         context["data"].append(future.result())
    #     #     except Exception as exc:
    #     #         pass
    #     # print(f'{url} genera=ed an exception: {exc}')
    # executor.shutdown()
    return context


async def aparse(url, timeout):
    url = f'{source_url}{url}'
    headers = await async_ua()
    async with aiohttp.ClientSession() as client:
        async with client.get(url=url, headers=headers, timeout=timeout) as rs:
            if rs.status == 200:
                html = etree.HTML(await rs.text())
                info = html.xpath('//div[@class="videoDetail"]/li//text()')
                info.pop(2)
                data = {
                    "name": html.xpath('//li[@class="sa"]/text()')[0].strip(),
                    "cover": html.xpath('//div[@class="videoPic"]/img/@src')[0],
                    "info": dict(zip(info[::2], info[1::2])),
                    "intro": html.xpath('//div[@class="contentNR"]//text()')[0].strip(),
                    "play": [x.split("$") for x in html.xpath('//li/input[@name="copy_sel"]/@value')],
                    # "play_info": play
                }
                # print(data)
                return data


def parse(url, timeout):
    url = f'{source_url}{url}'
    headers = ua()
    with requests.get(url=url, headers=headers, timeout=timeout) as rs:
        if rs.status_code == 200:
            html = etree.HTML(rs.text)
            info = html.xpath('//div[@class="videoDetail"]/li//text()')
            info.pop(2)
            data = {
                "name": html.xpath('//li[@class="sa"]/text()')[0].strip(),
                "cover": html.xpath('//div[@class="videoPic"]/img/@src')[0],
                "info": dict(zip(info[::2], info[1::2])),
                "intro": html.xpath('//div[@class="contentNR"]//text()')[0].strip(),
                "play": [x.split("$") for x in html.xpath('//li/input[@name="copy_sel"]/@value')],
                # "play_info": play
            }
            # print(data)
            return data


@app.route('/music/')
@jinja.template('music.html')
async def music(request):
    myLoop = request.app.loop
    myLoop.create_task(task_sleep())
    with open(songfile, 'rb+') as f:
        songlist = eval(f.read())
    if dict(request.args).get("keyword", ""):
        keyword = dict(request.args).get("keyword", "")[0]
    else:
        keyword = "周杰伦"
    url = 'http://121.37.209.113:8090/search'
    headers = await async_ua()
    params = {
        "keyword": keyword
    }
    result = {
        "title": "音乐",
        "url": "/music/",
        "songlist": songlist
    }
    try:
        async with aiohttp.ClientSession() as client:
            async with client.get(url=url, params=params, headers=headers) as rs:
                if rs.status == 200:
                    result["data"] = json.loads(await rs.text()).get("data")
                else:
                    result["msg"] == "暂时无法搜索！"
    except Exception as e:
        print(e)
        result = {
            "code": 402,
            "msg": "哎呀呀！出错了！",
            "result": []
        }
    return result


@app.route('/music/sort')
async def down_music(request):
    url = 'http://121.37.209.113:8090/song/find'
    singer = request.args.get("singer", "")
    song = request.args.get("song", "")
    tone = request.args.get("tone", "")
    params = {
        "keyword": f'{singer}+{song}'
    }
    headers = await async_ua()
    try:
        async with aiohttp.ClientSession() as client:
            async with client.get(url=url, params=params, headers=headers) as rs:
                if rs.status == 200:
                    # print(await rs.text())
                    data = json.loads(await rs.text()).get("data", "")
                    if data:
                        result = {
                            "result": data.get(tone, "")
                        }
    except Exception as e:
        print(e)
        result = {
            "code": 402,
            "msg": "哎呀呀！出错了！",
            "result": []
        }
    return response.json(result)


@app.route('/chat/')
@jinja.template('chat.html')
async def chat(request):
    return {"title": "聊天机器人"}


@app.websocket('/chat/msg/')
async def chat_msg(request, ws):
    while True:
        user_msg = await ws.recv()
        # print(f'Received: {user_msg}')
        params = {"key": "free", "appid": 0, "msg": user_msg}
        async with aiohttp.ClientSession() as client:
            async with client.get(url='http://api.qingyunke.com/api.php', params=params) as rs:
                if rs.status == 200:
                    chat_msg = json.loads(await rs.text())["content"]
                    # print(f'Sending: {chat_msg}')
                    await ws.send(chat_msg)


@app.route('/wxid/add')
@jinja.template('wxid_add.html')
async def wxid_add(request):
    if dict(request.args).get("keyword", ""):
        wxid = dict(request.args).get("keyword", "")[0]
        if wxid:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(f'weixin://contacts/profile/{wxid}')
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            os.makedirs(WX_QRCODE, exist_ok=True)
            img.save(f'{WX_QRCODE}{wxid}.png')
            # img.show()
            result = {
                'title': "wxid",
                'url': '/wxid/add',
                'wxid': wxid
            }
            return result
        else:
            result = {
                "code": 201,
                "title": "音乐",
                "url": "/music/",
                "msg": "请输入wxid",
                "result": []

            }
            return result


if __name__ == "__main__":
    app.error_handler.add(
        NotFound,
        lambda r, e: response.json({
            "code": 500,
            "msg": "有点儿小问题！",
            "result": []
        })
    )
    app.run(host="0.0.0.0", port=52)
