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
reply_url = "https://hzt-app1.haizitong.com/2/s/survey/question/reply"

# VARIABLE NAME
DEVICE = 'c577e0b6a8b68bd0fbd43361ddd1dffa8e34e6395764c897c2471219eba8ceb2'
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
        logger.error("手机登录出错" + e)
    if 'errorCode' in response:
        logger.error("手机登录请求失败" + f"{response['data']['errorCode']}")
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
            logger.error("用户登录出错" + e)
        if 'errorCode' in response:
            logger.error("用户登录请求失败" + f"{response['data']['errorCode']}")
        else:
            return response['data']['token']
    else:
        logger.error('手机登录接口返回空')
        return


def reply(userToken):
    if userToken is not None:
        logger.info('开始提交答案请求')
        answers = '[{"options":[{"optionId":"d3561819-cc60-41b7-884d-1ec3106141d6"}],"itemId":"b4c83fbe-8f77-4154-9f6a-dfa7444aa318"},{"text":"36.5","itemId":"fa13c111-bcf2-4a84-b70b-5a5d9772857c"},{"options":[{"optionId":"d8097d9556f442c0800dcec009da5cc6"}],"itemId":"22c650fd65e54c348fb0d8ce40fe0f5c"},{"options":[{"optionId":"cb07573c-56f0-4ae9-92db-7ed451e5df30"}],"itemId":"303ccb79-a60c-47ca-921b-275f6ced43a6"},{"files":[{"picHeight":1316,"picWidth":794,"url":"http:\/\/min.haizitong.com\/2\/ali\/i\/3086ddf9565f4995b7bb9c203566fb4a","type":"i"}],"itemId":"8c5284e0-4380-40b8-b031-38903aeac459"},{"options":[{"optionId":"3dae73e8e87c4196b151a891593c45c9"}],"itemId":"9bc3dbb0c378405e8f8529639c7942fb"},{"text":"李慰37.2","itemId":"b85ff1f8-e2c5-43a9-a7d4-c88effd19014"},{"options":[{"optionId":"5913424e-adf0-4a3e-8683-aa1f7d151543"}],"itemId":"7cc442c7-2349-4ba7-8233-9c43f922dc2c"},{"files":[{"picHeight":1219,"picWidth":796,"url":"http:\/\/min.haizitong.com\/2\/ali\/i\/45420d840ed64851a6482756238fc8c7","type":"i"}],"itemId":"76674aa4-2ebe-4f4f-937a-383ef0b939fc"},{"files":[{"picHeight":788,"picWidth":1012,"url":"http:\/\/min.haizitong.com\/2\/ali\/i\/aa35461fbf924eaaa360f8a895d9568e","type":"i"}],"itemId":"7dcfb064-5794-42db-a057-2a3bc542a648"}]'
        replyRequestData = {'answers': answers,
                            'who': '1',
                            'surveyId': '5f3a5ac3d017dc0867d2b6fe'}
        try:
            response = session.post(url=reply_url, data=replyRequestData, auth=(USERID, userToken))
        except Exception as e:
            logger.error("提交答案出错" + e)
        if 'errorCode' in response:
            logger.error("提交答案请求失败" + f"{response['data']['errorCode']}")
        else:
            logger.info("打卡完成")
            sendMsg('打卡完成')
    return

def sendMsg(content):
    url = f"https://sctapi.ftqq.com/{SKEY}.send"
    parmas = {
        'desp': content,
        'title': '孩子通'
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    requests.post(url=url, data=parmas, headers=headers)


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
