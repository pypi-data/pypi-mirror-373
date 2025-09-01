import platform
import uuid
import requests

from .. import __version__
from ..message import *


class BaseClient(object):
    def __init__(self, config):
        """
        :type config: Config
        :param config: 配置信息

        """

        sign_type = config.sign_type

        self.__des3key = config.des3key
        self.__app_key = config.app_key

        self.__encrypt = None
        if sign_type == "sha256":
            self.__encrypt = HmacSigner(config.app_key)
        if sign_type == "rsa":
            self.__encrypt = RSASigner(config.app_key, config.yzh_public_key, config.dealer_private_key)

        self.__dealer_id = config.dealer_id
        self.__base_url = config.host
        self.__timeout = config.timeout

    def __header(self, request_id):
        if type(request_id) is not str or request_id == "":
            request_id = str(int(time.time()))
        return {
            "dealer-id": self.__dealer_id,
            "request-id": request_id,
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "yunzhanghu-sdk-python/%s/%s" % (
                __version__, platform.python_version()),
        }

    def __request(self, method, url, **kwargs):
        data = kwargs.get("data", None)
        param = kwargs.get("param", None)
        headers = self.__header(kwargs["request_id"])
        return self.__handle_resp(
            data, param, headers,
            requests.request(method=method,
                             url=self.__base_url + url,
                             headers=headers,
                             data=ReqMessage(self.__encrypt, data, self.__des3key).pack(),
                             params=ReqMessage(self.__encrypt, param, self.__des3key).pack(),
                             timeout=self.__timeout))

    def _post(self, url, request_id, data):
        kwargs = {"data": data, "request_id": request_id}
        return self.__request(method="POST", url=url, **kwargs)

    def _get(self, url, request_id, param):
        kwargs = {"param": param, "request_id": request_id}
        return self.__request(method="GET", url=url, **kwargs)

    def __handle_resp(self, req_data, req_param, headers, resp):
        if resp is None:
            raise ValueError("resp is None")

        resp.raise_for_status()
        return RespMessage(self.__des3key, resp.text, req_data,
                           req_param, headers).decrypt()


class BaseRequest(object):
    def __init__(self):
        self.__request_id = uuid.uuid1()

    @property
    def request_id(self):
        """ Get 请求 ID

        :return: str, dealer_id
        """
        if self.__request_id is None or self.__request_id == "":
            self.__request_id = uuid.uuid1()
        return self.__request_id.__str__()

    @request_id.setter
    def request_id(self, request_id):
        """ Set 请求 ID

        :type request_id: str
        :param request_id: 请求 ID
        """
        self.__request_id = request_id

    def __str__(self):
        res = self.__dict__.copy()
        del res["_BaseRequest__request_id"]
        return f"{self.__class__.__name__}({', '.join(f'{key}={getattr(self, key)}' for key in res.keys())})"
