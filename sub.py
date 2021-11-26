import os

import pytz
import requests
from random import randint
from datetime import datetime

# 忽略网站的证书错误，这很不安全 :(
verify_cert = True

# 全局变量
# 读取环境变量中的登录信息
user = os.environ['SEP_USER_NAME']  # 学号
passwd = os.environ['SEP_PASSWD']  # SAU密码
xingming = os.environ['XINGMING']
telnum = os.environ['TELNUM']
xueyuan = os.environ['XUEYUAN']
sauid = os.environ['SAU_ID']
bot_token = os.environ['BOT_TOKEN']
chat_id = os.environ['CHAT_ID']


def login(s: requests.Session, username, password):
    payload = {
        "username": username,
        "password": password
    }
    r = s.post("https://ucapp.sau.edu.cn/wap/login/invalid", data=payload)
    if r.json().get('m') != "操作成功":
        print("登录失败，错误信息: ", r.text)
        return False
    else:
        print("登录成功")
        return True


def submit(s: requests.Session):
    new_daily = {
        'xingming': xingming,
        'xuehao': user,
        'shoujihao': telnum,
        'danweiyuanxi': xueyuan,
        'dangqiansuozaishengfen': "辽宁省",
        'dangqiansuozaichengshi': "沈阳市",
        'shifouyuhubeiwuhanrenyuanmiqie': "否",
        'shifoujiankangqingkuang': "是",
        'shifoujiechuguohubeihuoqitayou': "否",
        'fanhuididian': "",
        'shifouweigelirenyuan': "否",
        'shentishifouyoubushizhengzhuan': "否",
        'shifouyoufare': "否",
        'qitaxinxi': "",
        'tiwen': "36.{}".format(randint(0, 8)),
        'tiwen1': "36.{}".format(randint(0, 8)),
        'tiwen2': "36.{}".format(randint(0, 8)),
        'riqi': datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d"),
        'id': sauid}
    proxies = {"http": None, "https": None}
    r = s.post("https://app.sau.edu.cn/form/wap/default/save?formid=10", data=new_daily, proxies=proxies, verify=False)
    result = r.json()
    if result.get('m') == "操作成功":
        print("打卡成功")
        print(str(new_daily))
        send_telegram_message(bot_token, chat_id, make_msg(result.get('m'), new_daily))
        return True
    else:
        print("打卡失败，错误信息: ", r.json())
        return False


def make_msg(res, daily):
    msg = r'''**智慧沈航打卡结果**
    **{}**
    打卡时间：{}
    体温：{}-{}-{}
    '''.format(res, daily['riqi'], daily['tiwen'], daily['tiwen1'], daily['tiwen2'])
    return msg


def send_telegram_message(bot_token, chat_id, msg):
    """
    Telegram通知打卡结果
    python-telegram-bot 只支持 python 3.6或更高的版本
    此处使用时再导入以保证向后兼容 python 3.5；
    如果要使用 tg 消息通知，请使用 python 3.6或更高的版本
    """
    import telegram
    bot = telegram.Bot(token=bot_token)
    bot.send_message(chat_id=chat_id, text=msg, parse_mode="MarkdownV2")


def report(username, password):
    s = requests.Session()
    s.verify = verify_cert
    header = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10;  AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045136 Mobile Safari/537.36 wxwork/3.0.16 MicroMessenger/7.0.1 NetType/WIFI Language/zh"
    }
    s.headers.update(header)

    print(datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S %Z"))

    for i in range(1, 20):
        print("开始第{}次登录尝试".format(i))
        if login(s, username, password):
            print("{}::登录成功，开始打卡".format(
                datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S %Z")))
            break
    for i in range(1, 20):
        print("开始第{}次打卡尝试".format(i))
        if submit(s):
            print("{}::打卡成功，任务结束".format(
                datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S %Z")))
            break


if __name__ == "__main__":
    report(username=user, password=passwd)
