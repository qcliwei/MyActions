import requests
import os
import sys


def sign():
    url = "https://community.iqiyi.com/openApi/score/add?agenttype=1&agentversion=0&appKey=basic_pca&appver=0&authCookie=b8idXVEm2OLrvyV8FClBZm1ERgrP6nCkT9AxyO80BFm1QAIZ05FpCREyVgdoVzoJsDfIx01&channelCode=sign_pcw&dfp=a083a25d5711d2425389af01bab7aad35aa905032ce121a4248b45d541a44088c1&scoreType=1&srcplatform=1&typeCode=point&userId=1571264382&user_agent=Mozilla/5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/97.0.4692.71%20Safari/537.36&verticalCode=iQIYI&sign=5c9f596788d9387a20fa43a8be7c64a5"
    res = requests.get(url)
    if res.json()["code"] == "A00000":
        try:
            growth = res.json()[
                "data"][0]
            quantity = growth["score"]
            continued = growth["continuousValue"]
            msg = f"+获得积分：{quantity}\n累计签到：{continued}天"
        except:
            msg = res.json()["message"]
    else:
        msg = res.json()["message"]
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
    SKEY = os.environ['SKEY']

    msg1 = sign()
    print(msg1)

    if len(sys.argv) > 1:
        if sys.argv[1] == '是':
            sendMsg(SKEY, msg1)
    else:
        sendMsg(SKEY, msg1)
