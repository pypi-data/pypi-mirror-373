"""自定义接口调用"""

from ..base import BaseClient
from ...utils import Utils

class CustomClient(BaseClient):
    def __init__(self, config):
        super().__init__(config)

    def do_request(self, url: str, method_type: str, request):
        """
        :type url: str
        :param url: 请求地址
        :type method_type: str
        :param method_type: 请求方式 GET/POST
        :type request: CustomRequest
        :param request: 请求参数

        :return: dict
        """
        if "GET" == method_type.upper():
            return self._get(url, request.request_id, Utils.copy_dict(request.__dict__))
        else:
            return self._post(url, request.request_id, Utils.copy_dict(request.__dict__))
