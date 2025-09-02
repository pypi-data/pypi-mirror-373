# -*- coding: UTF-8 -*-
"""
@File    ：ossHelper.py
@Author  ：VerSion/08398
@Date    ：2024/04/29 14:41 
@Corp    ：Uniview
"""
from minio import Minio
from minio.error import S3Error
import time
import random
import string
from noteparse.configReader import readConfig

ossConf = readConfig('end_point','bucket_name','access_key','secret_key',section='ossConfig')

def generate_snowflake_id():
    """
    生成雪花id
    :return: 雪花id
    """
    snowflake_id = ''
    # 获取当前时间戳
    timestamp = str(int(time.time() * 1000))
    # 生成随机字母和数字
    characters = string.ascii_letters + string.digits
    for _ in range(2):
        snowflake_id += random.choice(characters)
    snowflake_id += timestamp[-10:]
    for _ in range(2):
        snowflake_id += random.choice(characters)
    return snowflake_id

def upload_file_to_minio(file_path, object_name):
    try:
        # 初始化MinIO客户端
        client = Minio(
            endpoint=ossConf['end_point'],
            access_key=ossConf['access_key'],
            secret_key=ossConf['secret_key'],
            secure=True
        )
    except Exception as create_err:
        raise Exception("创建MinIO客户端时出错:", create_err)

    # 上传文件
    try:
        client.fput_object(ossConf['bucket_name'], object_name, file_path)
        print(f"文件 '{file_path}' 已成功上传至MinIO桶")
        return f"{ossConf['end_point']}/{ossConf['bucket_name']}/{object_name}"
    except S3Error as exc:
        raise Exception("文件上传至MinIO时发生异常:", exc)


def download_file_from_minio(object_name, download_path):
    try:
        # 初始化MinIO客户端
        client = Minio(
            endpoint=ossConf['end_point'],
            access_key=ossConf['access_key'],
            secret_key=ossConf['secret_key'],
            secure=True
        )
    except Exception as create_err:
        raise Exception("创建MinIO客户端时出错:", create_err)

    try:
        client.fget_object(ossConf['bucket_name'], object_name, download_path)
        print(f"文件 '{object_name}' 已从MinIO下载到本地 '{download_path}")
    except S3Error as exc:
        raise Exception("从MinIO下载文件时出错:", exc)
    


        

