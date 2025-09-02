import os.path
import time
from typing import Optional, List


class FileUtil:

    @staticmethod
    def get_sub_file_names(file_num: int, base_dir: Optional[str] = "./temp", dir_name: Optional[str] = None, file_name: Optional[str] = None) -> List[str]:
        """
        功能用于多个文件打包在压缩包中下载
        在指定或时间戳文件夹下，根据文件数量生成对应文件名
        :param base_dir: 基础路径
        :param file_num: 子文件数量
        :param dir_name: 文件夹名称，可以忽略
        :param file_name: 文件夹名称，建议填写，方便区分
        :return: 文件名列表
        """
        if not base_dir:
            base_dir = "./temp"
        if not dir_name:
            dir_name = str(int(time.time()*1000))
        dir_path = os.path.join(base_dir, dir_name)
        if os.path.exists(dir_path):
            dir_path = os.path.join(base_dir, str(int(time.time()*1000)))
        os.makedirs(dir_path, exist_ok=True)
        file_name_list = []
        for i in range(1, file_num+1):
            file_name_list.append(os.path.join(dir_path, (file_name or "") +"_"+str(i)))
        return file_name_list
