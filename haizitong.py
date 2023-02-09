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
task_list_url = "https://hzt-app1.haizitong.com/2/s/jia/task/list"
reply_url = "https://hzt-app1.haizitong.com/2/s/survey/question/reply"

# VARIABLE NAME
DEVICE = os.environ['DEVICE']
USERID = os.environ['USERID']
PASSWD = os.environ['PASSWD']
SKEY = os.environ['SKEY']

HEADERS = {
    'pkg': 'hztJia/1/6.1.3.1328',
    'User-Agent': 'haizitongJia/6.1.3 (iPhone; iOS 14.4; Scale/2.00)',
    'Cache-Control': 'no-cache',
    'Content-Type': 'application/x-www-form-urlencoded'
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


def reply(userToken, rsurveyId):
    if rsurveyId is None:
        logger.error('没有获取任务surveyId')
        return
    if userToken is not None:
        logger.info('开始提交答案请求')
        replyRequestData = 'answers=[{"options":[{"optionId":"98b7bc4a2aa445e2aa5150b6b0f0b6a0"}],"itemId":"24c607196bcb4fe192686ed1066c772d"},{"text":"36.7","itemId":"b59abaa4d82d4dea8917397a123a10dc"},{"files":[{"picHeight":788,"picWidth":1012,"url":"https:\/\/min.haizitong.com\/2\/ali\/i\/8e3fe302c6164fb38e4d41bbeb188b14594566","type":"i"}],"itemId":"92d41c9854c041e59e76f69d888ac4be"}]&surveyId=63e435d22c87ad4f048f5090&who=1'        try:
        response = session.post(url=reply_url, data=replyRequestData.encode('utf-8'), auth=(USERID, userToken),
                                    headers=HEADERS).json()
        except Exception as e:
            logger.error("提交答案出错" + str(e))
        else:
            if 'errorCode' in response['data']:
                logger.error("提交答案请求失败" + f"{response['data']}")
                sendMsg(f"{response['data']}")
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


def getQuestionID(userToken) -> str:
    logger.info('开始获取打卡任务列表')
    try:
        response = session.get(url=task_list_url, auth=(USERID, userToken), headers=HEADERS).json()
    except Exception as e:
        logger.error("获取任务列表失败" + str(e))
    else:
        if 'errorCode' in response['data']:
            logger.error("获取任务列表失败" + f"{response['data']}")
        else:
            model = response['data']
            for item in model:
                if item['status'] == 1:
                    return item['dataId']


if __name__ == '__main__':
    mLogin = mobileLogin()
    uLogin = userLogin(mLogin)
    # surveyId = getQuestionID(uLogin)
    reply(uLogin, '612c4f2f991fb72d5456a1cb')
