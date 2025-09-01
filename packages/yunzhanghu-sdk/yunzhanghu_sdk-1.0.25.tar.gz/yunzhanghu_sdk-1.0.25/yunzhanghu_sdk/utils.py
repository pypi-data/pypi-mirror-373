class Utils(object):
    @staticmethod
    def copy_dict(res: dict):
        res = res.copy()
        del res["_BaseRequest__request_id"]
        return res
