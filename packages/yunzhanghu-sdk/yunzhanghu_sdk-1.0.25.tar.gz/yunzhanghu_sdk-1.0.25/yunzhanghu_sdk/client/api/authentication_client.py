"""用户信息验证"""

from .model.authentication import *
from ..base import BaseClient
from ...utils import Utils


class AuthenticationClient(BaseClient):
    """用户信息验证客户端"""

    def __init__(self, config):
        super().__init__(config)

    def bank_card_four_auth_verify(self, request: BankCardFourAuthVerifyRequest):
        """ 银行卡四要素鉴权请求（下发短信验证码）

        :type request: BankCardFourAuthVerifyRequest
        :param request: the BankCardFourAuthVerifyRequest request parameters class.

        :return: BankCardFourAuthVerifyResponse
        """
        return self._post(
            "/authentication/verify-request",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def bank_card_four_auth_confirm(self, request: BankCardFourAuthConfirmRequest):
        """ 银行卡四要素确认请求（上传短信验证码）

        :type request: BankCardFourAuthConfirmRequest
        :param request: the BankCardFourAuthConfirmRequest request parameters class.

        :return: BankCardFourAuthConfirmResponse
        """
        return self._post(
            "/authentication/verify-confirm",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def bank_card_four_verify(self, request: BankCardFourVerifyRequest):
        """ 银行卡四要素验证

        :type request: BankCardFourVerifyRequest
        :param request: the BankCardFourVerifyRequest request parameters class.

        :return: BankCardFourVerifyResponse
        """
        return self._post(
            "/authentication/verify-bankcard-four-factor",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def bank_card_three_verify(self, request: BankCardThreeVerifyRequest):
        """ 银行卡三要素验证

        :type request: BankCardThreeVerifyRequest
        :param request: the BankCardThreeVerifyRequest request parameters class.

        :return: BankCardThreeVerifyResponse
        """
        return self._post(
            "/authentication/verify-bankcard-three-factor",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def id_card_verify(self, request: IDCardVerifyRequest):
        """ 身份证实名验证

        :type request: IDCardVerifyRequest
        :param request: the IDCardVerifyRequest request parameters class.

        :return: IDCardVerifyResponse
        """
        return self._post(
            "/authentication/verify-id",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def user_exempted_info(self, request: UserExemptedInfoRequest):
        """ 上传非居民身份证验证名单信息

        :type request: UserExemptedInfoRequest
        :param request: the UserExemptedInfoRequest request parameters class.

        :return: UserExemptedInfoResponse
        """
        return self._post(
            "/api/payment/v1/user/exempted/info",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def user_white_check(self, request: UserWhiteCheckRequest):
        """ 查看用户是否在非居民身份证验证名单中

        :type request: UserWhiteCheckRequest
        :param request: the UserWhiteCheckRequest request parameters class.

        :return: UserWhiteCheckResponse
        """
        return self._post(
            "/api/payment/v1/user/white/check",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def get_bank_card_info(self, request: GetBankCardInfoRequest):
        """ 银行卡信息查询接口

        :type request: GetBankCardInfoRequest
        :param request: the GetBankCardInfoRequest request parameters class.

        :return: GetBankCardInfoResponse
        """
        return self._get(
            "/api/payment/v1/card",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )
