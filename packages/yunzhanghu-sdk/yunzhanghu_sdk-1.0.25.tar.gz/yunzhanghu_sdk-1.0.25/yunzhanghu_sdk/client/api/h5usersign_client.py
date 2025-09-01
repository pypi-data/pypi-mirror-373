"""H5 签约"""

from .model.h5usersign import *
from ..base import BaseClient
from ...utils import Utils


class H5UserSignServiceClient(BaseClient):
    """H5 签约客户端"""

    def __init__(self, config):
        super().__init__(config)

    def h5_user_presign(self, request: H5UserPresignRequest):
        """ 预申请签约

        :type request: H5UserPresignRequest
        :param request: the H5UserPresignRequest request parameters class.

        :return: H5UserPresignResponse
        """
        return self._post(
            "/api/sdk/v1/presign",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def h5_user_sign(self, request: H5UserSignRequest):
        """ 申请签约

        :type request: H5UserSignRequest
        :param request: the H5UserSignRequest request parameters class.

        :return: H5UserSignResponse
        """
        return self._get(
            "/api/sdk/v1/sign/h5",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def get_h5_user_sign_status(self, request: GetH5UserSignStatusRequest):
        """ 获取用户签约状态

        :type request: GetH5UserSignStatusRequest
        :param request: the GetH5UserSignStatusRequest request parameters class.

        :return: GetH5UserSignStatusResponse
        """
        return self._get(
            "/api/sdk/v1/sign/user/status",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def h5_user_release(self, request: H5UserReleaseRequest):
        """ 用户解约（测试账号专用接口）

        :type request: H5UserReleaseRequest
        :param request: the H5UserReleaseRequest request parameters class.

        :return: H5UserReleaseResponse
        """
        return self._post(
            "/api/sdk/v1/sign/release",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )
