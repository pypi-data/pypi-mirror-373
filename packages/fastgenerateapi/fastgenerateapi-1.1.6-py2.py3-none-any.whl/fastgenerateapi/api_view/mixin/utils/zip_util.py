import io
import os
import zipfile
from typing import Union


class ZipUtil:

    @staticmethod
    def folder_to_zip(folder_path: str, zip_path: Union[str, io.BytesIO]):
        """
        把文件夹打包成zip
        :param folder_path: 文件夹路径
        :param zip_path: 打包后zip路径
        :return:
        """
        # 创建一个 ZIP 文件对象，使用 'w' 模式表示写入
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 遍历文件夹及其子文件夹
            for root, dirs, files in os.walk(folder_path):
                # 处理当前目录，将其添加到压缩包中，实现打包空文件夹
                relative_path = os.path.relpath(root, folder_path)
                if relative_path and relative_path != ".":
                    # 确保相对路径不是空字符串，避免将根目录重复添加
                    zip_info = zipfile.ZipInfo(relative_path + '/')
                    zipf.writestr(zip_info, '')
                # 处理文件
                for file in files:
                    # 获取文件的完整路径
                    file_path = os.path.join(root, file)
                    # 获取文件相对于文件夹的相对路径
                    relative_path = os.path.relpath(file_path, folder_path)
                    # 将文件添加到 ZIP 文件中
                    zipf.write(file_path, relative_path)

    @staticmethod
    def folder_to_zip_bytes_io(folder_path: str):
        """
        把文件夹打包zip后转换成io格式
        :param folder_path: 文件夹路径
        :return:
        """
        bytes_io = io.BytesIO()
        ZipUtil.folder_to_zip(folder_path, bytes_io)
        bytes_io.seek(0)
        return bytes_io




