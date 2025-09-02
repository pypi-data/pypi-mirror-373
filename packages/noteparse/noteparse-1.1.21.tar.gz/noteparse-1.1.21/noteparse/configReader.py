import os
import configparser
from io import StringIO
from minio import Minio
from minio.error import S3Error
import traceback


_end_point = "uicfile.uniview.com"
_bucket_name = "uicpro"
_access_key = "uicpro"
_secret_key = "uicpropass123*"
# ossconfig地址
object_name = 'uic-config.ini'
download_path = 'uicfile.uniview.com/uicpro/uic-config.ini'
configPath = '/home'

def reSetConfigPath(path):
    global configPath
    configPath = path

# def readConfig(*keys,section):
#     readConfigFromOss(*keys,section)

# keys传入多个key,section传入对应的type
def readConfigWithPath(*keys,section):
    # windows环境文件放E盘根目录
    # linux环境文件放/root/.crawlab目录下
    if 'nt' == os.name:
        configPath = 'E:\\'
    else:
        configPath = '/root/.crawlab'
    # 使用 os.path.expanduser 获取当前用户的 home 目录
    home_dir = os.path.expanduser(configPath)

    # 构建完整路径到 .ini 文件
    ini_file_path = os.path.join(home_dir, 'uic_config.ini')

    # 初始化 ConfigParser
    config = configparser.ConfigParser()
    result = {}
    # 读取配置文件
    if os.path.exists(ini_file_path):
        config.read(ini_file_path)
        for key in keys:
            # 假设 [Credentials] 是 section 名称
            try:
                val = config.get(section, key)
                result[key] = val
            except configparser.NoSectionError as e:
                print("Error reading the file for key:",key, e)
    else:
        print(f"The file {ini_file_path} does not exist.")
    return result


def readConfig(*keys,section):

    try:
        # 初始化MinIO客户端
        client = Minio(
            endpoint=_end_point,
            access_key=_access_key,
            secret_key=_secret_key,
            secure=True
        )
    except Exception as create_err:
        raise Exception("创建MinIO客户端时出错:", create_err)

    try:
        result = client.get_object(_bucket_name, object_name, download_path)

        # 将文件内容转换为字符串形式
        file_content = result.read().decode('utf-8')
        
        # 使用StringIO将字符串转换为类似文件的对象
        config_data = StringIO(file_content)

        # 创建ConfigParser对象并读取配置数据
        config = configparser.ConfigParser()
        config.read_file(config_data)
        result = {}
        # 打印所有section名称
        for key in keys:
            # 假设 [Credentials] 是 section 名称
            try:
                val = config.get(section, key)
                result[key] = val
            except configparser.NoSectionError as e:
                print("Error reading the file for key:",key, e)

        return result

        # 示例：读取特定section下的键值对（假设有一个section叫'settings'）
        # if 'settings' in config:
        #     for key in config['settings']:
        #         print(f"{key} = {config['settings'][key]}")
    except S3Error as exc:
        raise Exception("从MinIO下载文件时出错:", exc)


# # 设定main函数,程序起点
# if __name__ == '__main__':
#     try:
#         # ossConfig = readConfigFromOss('end_point','bucket_name',section='ossConfig')
#         db_config = readConfig('host','port','user','password','db',section='dbConfig')
#         print('osscofnig',db_config)
        
#     except Exception as err:
#         print(f'任务执行失败',err)
#         traceback.print_exc()