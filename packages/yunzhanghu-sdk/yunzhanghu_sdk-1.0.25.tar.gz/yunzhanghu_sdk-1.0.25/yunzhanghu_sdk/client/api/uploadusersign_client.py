"""签约信息上传"""

from .model.uploadusersign import *
from ..base import BaseClient
from ...utils import Utils


class UploadUserSignServiceClient(BaseClient):
    """签约信息上传客户端"""

    def __init__(self, config):
        super().__init__(config)

    def upload_user_sign(self, request: UploadUserSignRequest):
        """ 用户签约信息上传

        :type request: UploadUserSignRequest
        :param request: the UploadUserSignRequest request parameters class.

        :return: UploadUserSignResponse
        """
        return self._post(
            "/api/payment/v1/sign/user",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def get_upload_user_sign_status(self, request: GetUploadUserSignStatusRequest):
        """ 获取用户签约状态

        :type request: GetUploadUserSignStatusRequest
        :param request: the GetUploadUserSignStatusRequest request parameters class.

        :return: GetUploadUserSignStatusResponse
        """
        return self._get(
            "/api/payment/v1/sign/user/status",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )
