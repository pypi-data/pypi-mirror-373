"""
author: tianxu

description:
  文件操作相关工具，比如创建文件等操作
"""
import os

def mkdir(path):
    """在指定位置创建文件夹

    Args:
      path: String，需要创建文件夹的位置

    Returns:
      bool: 如果文件夹已经存在，返回False。创建成功返回True

    Raises:
    """
    folder = os.path.exists(path)
    if(os.path.exists(path)):
        return False
    else: # 判断是否存在文件夹如果不存在则创建为文件夹
        try:
            os.makedirs(path) # makedirs 创建文件时如果路径不存在会创建这个路径
        except Exception as e:
            raise e
    return True
