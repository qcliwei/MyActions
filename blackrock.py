import requests
from bs4 import BeautifulSoup
import os

SKEY = os.environ['SKEY']


def query():
    response = requests.get(url='https://www.blackrock.com/cn/products/230010/bgf-world-technology-fund-a2-usd')
    soup = BeautifulSoup(response.text, features='html.parser')
    priceContent = soup.find_all('span', 'header-nav-data')

    nowContent = soup.find_all('span', 'header-nav-label navAmount')

    nowText = nowContent[0].text.replace('\n', '')
    price = priceContent[0].text.replace('\n', '').replace('美元', '')

    up = priceContent[1].text.replace('\n', '')
    buyPrice = 80.27
    profit = f'{(float(price) - buyPrice) * 100 / buyPrice}'
    proportion = str(profit)[:5] + '%'

    message = f'{nowText}:{price},\n今日变动:{up},\n成本:{buyPrice},持仓盈亏:{proportion}'
    print(f'{message}')
    sendMsg(message)


def sendMsg(content):
    url = f"https://sctapi.ftqq.com/{SKEY}.send"
    parmas = {
        'desp': content,
        'title': '贝莱德世界科技基金A2'
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    r = requests.post(url=url, data=parmas, headers=headers)
    print(f"推送返回={r.text}")


if __name__ == '__main__':
    query()
