class ToolMixin:

    @staticmethod
    def reserve_dict(data: dict) -> dict:
        """
        字典key,value互转
        """
        result = {}
        for key, val in data.items():
            result[val] = key
        return result






