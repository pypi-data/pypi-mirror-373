from dataclasses import dataclass
import requests


@dataclass
class AdminConfig:
    base_url: str
    username: str
    password: str


@dataclass
class JobInfoConfig:
    jobGroup: int
    jobDesc: str
    author: str
    scheduleType: str
    scheduleConf: str
    executorParam: str


def xxl_login(func):
    def wrapper(*args, **kwargs):
        adminConfig = kwargs.get('adminConfig')
        # 先登录获取cookies
        url = f"{adminConfig.base_url}/login"
        data = {
            'userName': adminConfig.username,
            'password': adminConfig.password
        }
        try:
            response = requests.post(url, data)
            cookies = response.cookies
            kwargs['cookies'] = cookies
        except Exception as e:
            print(e)
            raise Exception
        return func(*args, **kwargs)

    return wrapper


class Xxl:
    @xxl_login
    def create_task(self, adminConfig: AdminConfig, jobInfoConfig: JobInfoConfig, cookies):
        if not cookies:
            raise PermissionError
        scheduleType = jobInfoConfig.scheduleType
        jobStaticConfig = {
            "cronGen_display": jobInfoConfig.scheduleConf if scheduleType == 'CRON' else '',
            "schedule_conf_CRON": jobInfoConfig.scheduleConf if scheduleType == 'CRON' else '',
            "schedule_conf_FIX_RATE": "",
            "schedule_conf_FIX_DELAY": "",
            "glueType": "BEAN",
            "executorHandler": "httpJobHandler",  # 固定采用simple的http请求方式，避免侵入代码注册bean handler
            "executorRouteStrategy": "FIRST",
            "childJobId": "",
            "misfireStrategy": "DO_NOTHING",
            "executorBlockStrategy": "SERIAL_EXECUTION",
            "executorTimeout": "0",
            "executorFailRetryCount": "0",
            "glueRemark": "GLUE代码初始化",
            "glueSource": ""
        }
        try:
            response = requests.post(adminConfig.base_url + '/jobinfo/add', data={**jobInfoConfig.__dict__,
                                                                                  **jobStaticConfig},
                                     cookies=cookies)
            result = response.json()
            if result.get('code') != 200:
                raise SystemError
            jobId = int(result.get('content'))
            self.start(cookies, jobId, adminConfig.base_url)
            return jobId
        # 激活任务
        except Exception:
            raise Exception

    @staticmethod
    def start(cookies, jobId, baseUrl):
        try:
            response = requests.post(baseUrl + '/jobinfo/start', data={"id": jobId},
                                     cookies=cookies)
            result = response.json()
            if result.get('code') != 200:
                raise SystemError
        except Exception:
            raise Exception

    @staticmethod
    def stop(cookies, jobId, baseUrl):
        try:
            response = requests.post(baseUrl + '/jobinfo/stop', data={"id": jobId},
                                     cookies=cookies)
            result = response.json()
            if result.get('code') != 200:
                raise SystemError
        except Exception:
            raise Exception

    @xxl_login
    def remove_task(self, adminConfig: AdminConfig, jobId, cookies):
        if not cookies:
            raise PermissionError
        try:
            response = requests.post(adminConfig.base_url + '/jobinfo/remove', data={"id": jobId},
                                     cookies=cookies)
            result = response.json()
            if result.get('code') != 200:
                raise SystemError
        except Exception:
            raise Exception