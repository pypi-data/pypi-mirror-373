"""个人所得税申报明细表"""

from ...base import BaseRequest


class GetTaxFileRequest(BaseRequest):
    """
    下载个人所得税申报明细表请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type ent_id: string
    :param ent_id: 平台企业签约主体

    :type year_month: string
    :param year_month: 所属期
    """
    def __init__(
        self,
        dealer_id = None,
        ent_id = None,
        year_month = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.ent_id = ent_id
        self.year_month = year_month


class GetTaxFileResponse(BaseRequest):
    """
    下载个人所得税申报明细表返回-响应

    :type file_info: list
    :param file_info: 文件详情
    """
    def __init__(
        self,
        file_info = None
    ):
        super().__init__()
        self.file_info = file_info


class FileInfo(BaseRequest):
    """
    报税文件详情-响应

    :type name: string
    :param name: 文件名称

    :type url: string
    :param url: 下载文件临时 URL

    :type pwd: string
    :param pwd: 文件解压缩密码
    """
    def __init__(
        self,
        name = None,
        url = None,
        pwd = None
    ):
        super().__init__()
        self.name = name
        self.url = url
        self.pwd = pwd


class GetUserCrossRequest(BaseRequest):
    """
    查询纳税人是否为跨集团用户请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type year: string
    :param year: 年份

    :type id_card: string
    :param id_card: 身份证号码

    :type ent_id: string
    :param ent_id: 平台企业签约主体
    """
    def __init__(
        self,
        dealer_id = None,
        year = None,
        id_card = None,
        ent_id = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.year = year
        self.id_card = id_card
        self.ent_id = ent_id


class GetUserCrossResponse(BaseRequest):
    """
    查询纳税人是否为跨集团用户返回-响应

    :type is_cross: bool
    :param is_cross: 跨集团标识
    """
    def __init__(
        self,
        is_cross = None
    ):
        super().__init__()
        self.is_cross = is_cross
