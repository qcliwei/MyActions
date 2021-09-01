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
    'Cache-Control': 'no-cache'
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
        answers = '[{"optionId":"d3561819-cc60-41b7-884d-1ec3106141d6"}],"itemId":"b4c83fbe-8f77-4154-9f6a-dfa7444aa318"},{"text":"36.5","itemId":"fa13c111-bcf2-4a84-b70b-5a5d9772857c"},{"options":[{"optionId":"d8097d9556f442c0800dcec009da5cc6"}],"itemId":"22c650fd65e54c348fb0d8ce40fe0f5c"},{"options":[{"optionId":"cb07573c-56f0-4ae9-92db-7ed451e5df30"}],"itemId":"303ccb79-a60c-47ca-921b-275f6ced43a6"},{"files":[{"picHeight":1792,"picWidth":828,"url":"https:\/\/min.haizitong.com\/2\/ali\/i\/03bc31c43fd4458792550dc8065f7f80","type":"i"}],"itemId":"8c5284e0-4380-40b8-b031-38903aeac459"},{"options":[{"optionId":"3dae73e8e87c4196b151a891593c45c9"}],"itemId":"9bc3dbb0c378405e8f8529639c7942fb"},{"text":"李慰37.5柯文汇37.4 ","itemId":"b85ff1f8-e2c5-43a9-a7d4-c88effd19014"},{"options":[{"optionId":"5913424e-adf0-4a3e-8683-aa1f7d151543"}],"itemId":"7cc442c7-2349-4ba7-8233-9c43f922dc2c"},{"files":[{"picHeight":2339,"picWidth":1080,"url":"https:\/\/min.haizitong.com\/2\/ali\/i\/325d366ed4ad4651bd02687ed6baa473","type":"i"},{"picHeight":1792,"picWidth":828,"url":"https:\/\/min.haizitong.com\/2\/ali\/i\/e1b650793866421f81a5bce0cc03e429","type":"i"}],"itemId":"76674aa4-2ebe-4f4f-937a-383ef0b939fc"},{"options":[{"optionId":"27ea48201611412e93341b0e7f4e89e0"}],"itemId":"7f6dc20b5e6e4ffe86f1ba073f8e3d30"},{"files":[{"picHeight":788,"picWidth":1012,"url":"https:\/\/min.haizitong.com\/2\/ali\/i\/0f5cf6761f494feea4ced6834f06960d","type":"i"}],"itemId":"7dcfb064-5794-42db-a057-2a3bc542a648"}]'
        replyRequestData = {'answers': answers,
                            'who': '1',
                            'surveyId': rsurveyId}
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
