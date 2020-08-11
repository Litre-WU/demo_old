import requests

url = 'http://game.91muzhi.com/mobile3/user/mobileDoLogin'
# url = 'http://gm.91muzhi.com:8080/sdk/FindPsw'

headers = {
    "Accept-Encoding": "gzip, deflate",
    "Referer": "http://game.91muzhi.com/m/html/login.html",
    # "Referer": "http://game.91muzhi.com/m/html/retrievePsd.html",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
}

data = {
    "name": "19965412404",
    "pwd": ""
}
# data = str({"phoneNum": "19965412404"})

with requests.post(url=url, data=data, headers=headers) as rs:
    if rs.status_code == 200:
        info = rs.json()
        if info["msg"] == "密码错误":
            print("yes")
        else:
            print(info["msg"])

# {"result":"success"}
# {"total":0,"rows":null,"ver":0,"ret":false,"msg":"密码错误","errcode":"","curPage":0,"token":null}
# {'total': 0, 'rows': None, 'ver': 0, 'ret': False, 'msg': '账号不存在，请确认是否输入正确账号。', 'errcode': '', 'curPage': 0, 'token': None}