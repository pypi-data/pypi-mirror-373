"""用户信息收集"""

from .model.usercollect import *
from ..base import BaseClient
from ...utils import Utils

class UserCollectServiceClient(BaseClient):
    """用户信息收集客户端"""

    def __init__(self, config):
        super().__init__(config)

    def get_user_collect_phone_status(self, request: GetUserCollectPhoneStatusRequest):
        """ 查询手机号码绑定状态

        :type request: GetUserCollectPhoneStatusRequest
        :param request: the GetUserCollectPhoneStatusRequest request parameters class.

        :return: GetUserCollectPhoneStatusResponse
        """
        return self._get(
            "/api/user/v1/collect/phone/status",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def get_user_collect_phone_url(self, request: GetUserCollectPhoneUrlRequest):
        """ 获取收集手机号码页面

        :type request: GetUserCollectPhoneUrlRequest
        :param request: the GetUserCollectPhoneUrlRequest request parameters class.

        :return: GetUserCollectPhoneUrlResponse
        """
        return self._get(
            "/api/user/v1/collect/phone/url",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )
