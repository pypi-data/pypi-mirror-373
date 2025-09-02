import requests


class WeiXinAuto:

    def __init__(self, **kwargs):
        host = kwargs.get('host', '')
        wx_port = kwargs.get('wx_port', 30001)
        self.base_url = f'http://{host}:{wx_port}/'
        self.headers = {"content-type": "application/json"}

        # 本人 wxid_ebbhdhy9megw22
        self.user_info_v1 = {
            'wxid_cb9xe21jsshf22': {
                'name': '高阳小号',
                'wxid_id': 'wxid_cb9xe21jsshf22',
                'wxid': 'Fr1996forever2',
            },
        }
        self.ai_chat_keyword = ['懒阳阳', '懒洋洋', '懒羊羊', 'lly']

    @staticmethod
    def ret_json(code=200, msg=None, data=None):
        return {'code': code, 'msg': msg, 'data': data}

    def req(self, method='post', url=None, from_data=None):
        # res = requests.post(url=url, headers=self.headers, json={"wxid": wxid, "msg": msg})
        res = requests.post(url=url, headers=self.headers, json=from_data, timeout=5)
        if res.status_code == 200:
            return self.ret_json(200, 'ok', res.json())
        return self.ret_json(500, '错误')

    # 个人 个人信息详情
    def get_self_login_info(self):
        url = f"{self.base_url}GetSelfLoginInfo"
        res_data = self.req(url=url)
        return res_data
