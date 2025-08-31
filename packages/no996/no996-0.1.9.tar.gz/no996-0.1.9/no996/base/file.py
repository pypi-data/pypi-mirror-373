import os

import structlog

logger = structlog.get_logger(__name__)


class File(object):
    @staticmethod
    # 递归搜索指定文件夹下所有文件
    def walk(path, callback=None):
        file_list = []
        for root, dirs, files in os.walk(path):
            for file in files:
                abs_path = os.path.join(root, file)
                if callback:
                    abs_path = callback(abs_path)
                if abs_path:
                    file_list.append(abs_path)
        return file_list

    @staticmethod
    def remove_by_suffix(directory, suffix):
        for filename in os.listdir(directory):
            if filename.endswith(suffix):
                file_path = os.path.join(directory, filename)
                try:
                    os.remove(file_path)
                    # logger.info(f"已删除: {file_path}")
                except OSError as e:
                    logger.info(f"删除失败 {file_path}: {e}")
