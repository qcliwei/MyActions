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
        replyRequestData = 'answers=[{"options":[{"optionId":"98b7bc4a2aa445e2aa5150b6b0f0b6a0"}],"itemId":"24c607196bcb4fe192686ed1066c772d"},{"text":"36.4","itemId":"b59abaa4d82d4dea8917397a123a10dc"},{"options":[{"optionId":"1d1c3be515eb4efe8c03b81687d4b468"}],"itemId":"545a657079b54deba3bd08d8ece54412"},{"options":[{"optionId":"4c8c4fde2b9540dfb0f5637abdf7d584"}],"itemId":"9cb91b0034df4beca7d6581cfd8cbf79"},{"files":[{"picHeight":2532,"picWidth":1170,"url":"https:\/\/min.haizitong.com\/2\/ali\/i\/e6f2791f9fb1443ba057b2909cc171ba733113","type":"i"}],"itemId":"ae05b41629d5430090f0b068f6ed4084"},{"options":[{"optionId":"8ad9cc9c340e44ef814d81a230696f38"}],"itemId":"e139b9c506304670a6dcce18b4b77d23"},{"text":"李慰37.5柯文汇37.4 ","itemId":"beebea22904d42f68b60468673674f4b"},{"options":[{"optionId":"26d3109e5d3c4ab3bb7aa7a1f0dd00d3"}],"itemId":"5b7c475be42943bca66c385713c455d5"},{"files":[{"picHeight":1792,"picWidth":828,"url":"https:\/\/min.haizitong.com\/2\/ali\/i\/92955f60b5414bdb846ba7b7bb38a749104917","type":"i"},{"picHeight":2532,"picWidth":1170,"url":"https:\/\/min.haizitong.com\/2\/ali\/i\/9d81c4d6dfd146ba8705bdcf3ec1de0b250888","type":"i"}],"itemId":"1f41561d961a40df896598be4ac8c0f6"},{"options":[{"optionId":"a53a623f8935401b88303bb8716f53e4"}],"itemId":"4a4d52bf230644d9b0cbd90fa3eff7bd"},{"options":[{"optionId":"9fa0dc45eefd4e5bbbdfb5d432d43029"}],"itemId":"a7ae4a1bf55942a08bfc8070e252d1dd"},{"options":[{"optionId":"e92e56564dc14cde8dcf4744abec6273"}],"itemId":"ccd17564cd3842829634692e3c95de82"}]&signUrl=https://min.haizitong.com/2/ali/i/3df3ee59952041019d79d5124e01bfc7062591&surveyId=6246d406022435797799109d&who=1'
        try:
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
