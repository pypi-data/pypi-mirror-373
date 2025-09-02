import time
from django.http import JsonResponse
from .base_class import *
from .base_mode_class import ModeFunc

mode_pro = ModeFunc()


# django
class DjangoJike:
    # 配置
    @staticmethod
    def django_config():
        sc = 'status_code'  # 返回码
        msg = 'message'  # 返回消息

        return {
            "status_codes": {
                "code_200": {sc: 200, msg: '成功-200'},
                "code_400": {sc: 400, msg: '错误-400'},
                "code_500": {sc: 500, msg: '错误-500'},
                "code_xxx": {sc: 555, msg: '错误-xxx'},
                "code_token": {sc: 556, msg: '错误-token'},
                "code_method": {sc: 557, msg: '错误-method'},
            },
            "save_logs": 0,
            "save_logs_post": [
                '/',
                '/web/love/index',
                '/web/love/photo',
                '/test/test',
                '/test/logs',
            ],
            "save_logs_get": [
                '/',
                '/web/love/index',
                '/web/love/photo',
                '/test/test',
                '/test/logs',
            ],
        }

    # 存储日志
    @staticmethod
    def django_save_log(request, code=200):
        meta = request.META
        method = request.method
        form_data = request.POST
        user_ip = meta.get('HTTP_X_FORWARDED_FOR', '127.0.0.2')  # django版本不一样，参数不一样
        user_ua = meta.get('HTTP_USER_AGENT', '')
        user_path_info = meta.get('PATH_INFO', '')

        values = meta.items()
        info = []
        for k, v in values:
            info.append(f'{k}:{v}')

        # 排除一些请求
        for no_save in ['/static/', '/favicon.ico']:
            if no_save in user_path_info:
                return 0

        create_time = int(time.time())
        create_time_str = time.strftime("%Y-%m-%d %X", time.localtime(create_time))  # 2021-04-12 14:36:20
        save_table = config_dict['mysql_table']['fr1997']['django_logs']['name']
        mode_pro.mysql_db(method="ins", table=save_table, save_data={
            'code': code,
            'method': method,
            'form_data': form_data,
            'user_ua': user_ua,
            'user_ip': user_ip,
            'info': str(info),
            'user_path_info': user_path_info,
            'create_time': create_time,
            'create_time_str': create_time_str,
        }, conn_tp=5)
        return {
            'info': info,
            'user_ua': user_ua,
            'user_ip': user_ip,
            'user_path_info': user_path_info,
        }

    # 装饰器 请求限制
    def django_res_limit(self, func):
        """
            get 不验证token   post  需要验证
        """

        def wrapper(request):
            method = request.method
            form_data = request.POST
            url_path = str(request.path)
            # 存储日志(存储的是请求，不是结果)
            if method == 'GET' and url_path in self.django_config()['save_logs_get']:
                self.django_save_log(request)  # 存储django日志
            elif method == 'POST' and url_path in self.django_config()['save_logs_post']:
                self.django_save_log(request)  # 存储django日志

            # POST 要验证token
            try:
                if method == 'GET':
                    return func(request)
                elif method == 'POST':
                    token = form_data.get('token', '')  # 验证参数
                    if token == config_dict['token']['django'] or url_path in config_dict['django']['no_token_check']:
                        return func(request)
                    else:
                        django_code = "code_token"
                else:
                    django_code = "code_method"
            except Exception as E:
                print(E)
                django_code = "code_xxx"
            from django.http import JsonResponse  # 2.返回json对象
            ret = self.django_return(code=django_code)
            return JsonResponse(ret)

        return wrapper

    # 在你的django_class.py中添加
    def django_ip_limit(self, func):
        """IP白名单验证装饰器"""

        def wrapper(request):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            if ip not in mode_pro.ip_white_list():
                return RetJson.code500(msg=f'Prohibit requests :{ip}')

            # 将IP传递给后续处理
            request.client_ip = ip
            return func(request)

        return wrapper

    # django 返回配置
    def django_return(self, **kwargs):
        sc = 'status_code'  # 返回码
        msg = 'message'  # 返回消息
        code = kwargs.get('code')
        status_codes = self.django_config()['status_codes']
        return {
            sc: status_codes[code][sc],
            msg: status_codes[code][msg],
        }

    # 获取请求的ip 【1=正式】 【2=测试】
    def user_ip(self, request):
        if request.META.get('REMOTE_ADDR', None) == '1.14.10.13':
            return 1
        else:
            return 2


class RetJson:

    @classmethod
    def data_list(cls, data):
        if data is None:
            return []
        return data

    @classmethod
    def data_dict(cls, data):
        if data is None:
            return {}
        return data

    @classmethod
    def ret_json(cls, code, msg, data_list, data_dict, code_remark=None):
        data_list = cls.data_list(data_list)
        data_dict = cls.data_dict(data_dict)
        if code_remark:
            return JsonResponse({
                'code': code,
                'msg': msg,
                'code_remark': code_remark,
                'data_list': data_list,
                'data_dict': data_dict
            })
        return JsonResponse({
            'code': code,
            'msg': msg,
            'data_list': data_list,
            'data_dict': data_dict
        })

    @classmethod
    def code200(cls, msg='ok', data_list=None, data_dict=None):
        return cls.ret_json(200, msg, data_list, data_dict)

    @classmethod
    def code201(cls, msg='ok', data_list=None, data_dict=None):
        return cls.ret_json(201, msg, data_list, data_dict, 201)

    @classmethod
    def code202(cls, msg='ok', data_list=None, data_dict=None):
        return cls.ret_json(202, msg, data_list, data_dict, 202)

    @classmethod
    def code400(cls, msg='err', data_list=None, data_dict=None):
        return cls.ret_json(400, msg, data_list, data_dict)

    @classmethod
    def code404(cls, msg='err', data_list=None, data_dict=None):
        return cls.ret_json(404, msg, data_list, data_dict, 404)

    @classmethod
    def code500(cls, msg='err', data_list=None, data_dict=None):
        return cls.ret_json(500, msg, data_list, data_dict)

    @classmethod
    def code501(cls, msg='err', data_list=None, data_dict=None):
        return cls.ret_json(501, msg, data_list, data_dict, 501)

    @classmethod
    def code502(cls, msg='err', data_list=None, data_dict=None):
        return cls.ret_json(502, msg, data_list, data_dict, 502)
