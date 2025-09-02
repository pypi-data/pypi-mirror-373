from typing import Optional


class SwaggerUtil:

    @staticmethod
    def swagger_to_js(swagger_json: Optional[dict]):
        """
        通过swagger文档自动生成js接口文件，方便前后端开发
        如果 swagger_json 为空，
        - 优先检查运行路径下的swagger.json文件
        - 其次检查 127.0.0.1:8000/openapi.json 接口
        :param swagger_json:
        :return:
        """
        # 参考go zero 生成js文件的样式
        
        return








