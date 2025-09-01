"""API 签约"""

from .model.apiusersign import *
from ..base import BaseClient
from ...utils import Utils


class ApiUserSignServiceClient(BaseClient):
    """API 签约客户端"""

    def __init__(self, config):
        super().__init__(config)

    def api_use_sign_contract(self, request: ApiUseSignContractRequest):
        """ 获取协议预览 URL

        :type request: ApiUseSignContractRequest
        :param request: the ApiUseSignContractRequest request parameters class.

        :return: ApiUseSignContractResponse
        """
        return self._get(
            "/api/sign/v1/user/contract",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def api_user_sign_contract(self, request: ApiUserSignContractRequest):
        """ 获取协议预览 URL V2

        :type request: ApiUserSignContractRequest
        :param request: the ApiUserSignContractRequest request parameters class.

        :return: ApiUserSignContractResponse
        """
        return self._get(
            "/api/sign/v1/user/contract",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def api_user_sign(self, request: ApiUserSignRequest):
        """ 用户签约

        :type request: ApiUserSignRequest
        :param request: the ApiUserSignRequest request parameters class.

        :return: ApiUserSignResponse
        """
        return self._post(
            "/api/sign/v1/user/sign",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def get_api_user_sign_status(self, request: GetApiUserSignStatusRequest):
        """ 获取用户签约状态

        :type request: GetApiUserSignStatusRequest
        :param request: the GetApiUserSignStatusRequest request parameters class.

        :return: GetApiUserSignStatusResponse
        """
        return self._get(
            "/api/sign/v1/user/status",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def api_user_sign_release(self, request: ApiUserSignReleaseRequest):
        """ 用户解约（测试账号专用接口）

        :type request: ApiUserSignReleaseRequest
        :param request: the ApiUserSignReleaseRequest request parameters class.

        :return: ApiUserSignReleaseResponse
        """
        return self._post(
            "/api/sign/v1/user/release",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )
