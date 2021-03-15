import requests
import os
import sys


def sign(user):
    url = "https://tc.vip.iqiyi.com/taskCenter/task/queryUserTask"
    params = {
        "P00001": user,
        "autoSign": "yes"
    }
    res = requests.get(url, params=params)
    if res.json()["code"] == "A00000":
        try:
            growth = res.json()[
                "data"]["signInfo"]["data"]["rewardMap"]["growth"]
            continueSignDaysSum = res.json(
            )["data"]["signInfo"]["data"]["continueSignDaysSum"]
            rewardDay = 7 if continueSignDaysSum % 28 <= 7 else (
                14 if continueSignDaysSum % 28 <= 14 else 28)
            roundDay: int = 28 if continueSignDaysSum % 28 == 0 else continueSignDaysSum % 28
            msg = f"+{growth}成长值\n连续签到：{continueSignDaysSum}天\n签到周期：{roundDay}天/{rewardDay}天"
        except:
            msg = res.json()["data"]["signInfo"]["msg"]
    else:
        msg = res.json()["msg"]
    return msg


def sendMsg(key, content):
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}"
    parmas = {
        'text': {'content': f'爱奇艺签到:\n{content}'},
        'msgtype': 'text'
    }
    headers = {
        "Content-Type": "application/json;charset=utf-8"
    }
    res = requests.post(url=url, json=parmas, headers=headers)
    print(res.text)


if __name__ == '__main__':
    P00001 = os.environ['P00001']
    SKEY = os.environ['SKEY']

    msg1 = sign(P00001)
    print(msg1)

    if len(sys.argv) > 1:
        if sys.argv[1] == '是':
            sendMsg(SKEY, msg1)
    else:
        sendMsg(SKEY, msg1)
