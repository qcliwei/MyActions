# -*- coding:utf-8 -*-
import requests
import logging
import base64
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API_URL
account_login_url = "https://hzt-app1.haizitong.com/2/org/account/login"
user_login_url = "https://hzt-app1.haizitong.com/2/org/mobile/user/login"
reply_url = "https://hzt-app2.haizitong.com/2/s/survey/question/reply"

# VARIABLE NAME
DEVICE = os.environ['DEVICE']
USERID = os.environ['USERID']
PASSWD = os.environ['PASSWD']
SKEY = os.environ['SKEY']

HEADERS = {
    'pkg': 'hztJia/1/6.1.3.1328',
    'User-Agent': 'haizitongJia/6.1.3 (iPhone; iOS 14.4; Scale/2.00)'
}

session = requests.Session()


def mobileLogin():
    logging.info("开始登录请求")
    loginRequestData = {
        'apnType': 16,
        'device': DEVICE,
        'passwd': PASSWD,
        'loginName': 15002173163
    }
    try:
        response = session.post(url=account_login_url, data=loginRequestData, headers=HEADERS).json()
    except Exception as e:
        logger.error("手机登录出错" + str(e))
    else:
        if 'errorCode' in response['data']:
            logger.error("手机登录请求失败" + f"{response['data']}")
        else:
            return response['data']


def userLogin(mobileLoginData):
    if mobileLoginData is not None:
        logging.info("开始刷新token请求")
        auth = get_basic_auth_str(mobileLoginData['accountId'], mobileLoginData['token'])
        userLoginRequestData = {
            'device': DEVICE,
            'userId': USERID,
            'authorization': auth
        }
        try:
            response = session.post(url=user_login_url, data=userLoginRequestData).json()
        except Exception as e:
            logger.error("用户登录出错" + str(e))
        else:
            if 'errorCode' in response['data']:
                logger.error("用户登录请求失败" + f"{response['data']}")
            else:
                return response['data']['token']
    else:
        logger.error('手机登录接口返回空')
        return


def reply(userToken):
    if userToken is not None:
        logger.info('开始提交答案请求')
        answers = '[{"options":[{"optionId":"568ace52-38c9-4312-80ad-7ce3ecc4b09b"}],"itemId":"1445cb71-8b3a-4995-8cb1-f13bf6fb0f20"},{"options":[{"optionId":"e09d9680-98e5-43b2-a59a-b7e4cfdf6f0e"}],"itemId":"9dd3337a-10ca-4f96-96b2-484f2b3da52d"},{"options":[{"optionId":"6bdd4bb4-de08-4455-8be8-6121aac81b2c"}],"itemId":"dee0523d-e4ea-47e2-886e-c8321296f092"},{"options":[{"optionId":"4a834e27-571a-463c-ac86-7e300d65ddef"}],"itemId":"96e92454-a36d-469c-88bd-05e6d1a154de"},{"files":[{"picHeight":1316,"picWidth":794,"url":"https:\/\/min.haizitong.com\/2\/ali\/i\/0087c2cf18c346308636756879ba7e07","type":"i"}],"itemId":"a6781f9f32284a1dac65900c309cc2e9"}]'
        replyRequestData = {'answers': answers,
                            'who': '1',
                            'surveyId': '5f3a5ac3d017dc0867d2b6fe'}
        try:
            response = session.post(url=reply_url, data=replyRequestData, auth=(USERID, userToken)).json()
        except Exception as e:
            logger.error("提交答案出错" + str(e))
        else:
            if 'errorCode' in response['data']:
                logger.error("提交答案请求失败" + f"{response['data']}")
            else:
                logger.info("打卡完成")
                sendMsg('打卡完成')
    return


def sendMsg(content):
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={SKEY}"
    parmas = {
        'text': {'content': f'孩子通签到:\n{content}'},
        'msgtype': 'text'
    }
    headers = {
        "Content-Type": "application/json;charset=utf-8"
    }
    r = requests.post(url=url, json=parmas, headers=headers)
    logger.info(f"推送返回={r.text}")


def get_basic_auth_str(username, password):
    temp_str = username + ':' + password
    # 转成bytes string
    bytesString = temp_str.encode(encoding="utf-8")
    # base64 编码
    encodestr = base64.b64encode(bytesString)
    return 'Basic ' + encodestr.decode()


if __name__ == '__main__':
    mLogin = mobileLogin()
    uLogin = userLogin(mLogin)
    reply(uLogin)
