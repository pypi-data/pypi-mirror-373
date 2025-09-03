import noteparse.proxyHelper as proxyHelper
import requests,time,re
from datetime import datetime
import json
import urllib3
from urllib.parse import urlencode
import ssl
import traceback
from noteparse.configReader import readConfig

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

originHeader = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        
    }

proxyConf = readConfig('minute_url','minute_user','minute_pwd','daily_url','daily_user','daily_pwd',section='proxyConfig')
minute_user = proxyConf['minute_user']
minute_pwd = proxyConf['minute_pwd']
minute_url = proxyConf['minute_url']
daily_url = proxyConf['daily_url']
daily_user = proxyConf['daily_user']
daily_pwd = proxyConf['daily_pwd']
def request_get(url,headers=originHeader):
    try:
        proxy_info = proxyHelper.get_singleton()
        proxies = {
            'http': f'http://{minute_user}:{minute_pwd}@{str(proxy_info["ip"])}:{str(proxy_info["port"])}',
            'https': f'http://{minute_user}:{minute_pwd}@{str(proxy_info["ip"])}:{str(proxy_info["port"])}'
        }
       
        response = requests.get(url=url,verify=False,proxies=proxies,timeout=30,headers=headers)
        return response
    except Exception as request_err:
        print(datetime.now(),'get请求失败,2s后重试',url,request_err)
        if 'Unable to connect to proxy' in str(request_err):
            proxyHelper.reflash_singleton()
        time.sleep(2)
        return request_get(url)
        # else:
        #     return None

def request_post_urlencode(url,param,headers=originHeader):
    try:
        proxy_info = proxyHelper.get_singleton()
        proxies = {
            'http': f'http://{minute_user}:{minute_pwd}@{proxy_info["ip"]}:{str(proxy_info["port"])}',
            'https': f'http://{minute_user}:{minute_pwd}@{proxy_info["ip"]}:{str(proxy_info["port"])}'
        }
        response = requests.post(url=url,data=param,headers=headers,verify=False,proxies=proxies,timeout=30)
        return response
    except Exception as request_err:
        print('post请求失败',url,param,request_err)
        traceback.print_exc()
        if 'Remote end closed connection without response' in str(request_err) or 'timed out' in str(request_err) or 'Unable to connect to proxy' in str(request_err):
            proxyHelper.reflash_singleton()
        time.sleep(5)
        return request_post_urlencode(url,param)
    
def request_post_json(url,param,headers=originHeader):
    try:
        headers['Content-Type'] = 'application/json;charset=UTF-8'
        proxy_info = proxyHelper.get_singleton()
        proxies = {
            'http': f'http://{minute_user}:{minute_pwd}@{proxy_info["ip"]}:{str(proxy_info["port"])}',
            'https': f'http://{minute_user}:{minute_pwd}@{proxy_info["ip"]}:{str(proxy_info["port"])}'
        }
        response = requests.post(url=url,data=json.dumps(param),headers=headers,verify=False,proxies=proxies,timeout=30)
        return response
    except Exception as request_err:
        print('post请求失败',url,param,request_err)
        if 'Remote end closed connection without response' in str(request_err) or 'timed out' in str(request_err) or 'Unable to connect to proxy' in str(request_err):
            proxyHelper.reflash_singleton()
        time.sleep(5)
        return request_post_json(url,param)

def initCtx():
    ctx = ssl.create_default_context()
    ctx.set_ciphers('AES128-SHA')
    return ctx


timeout = urllib3.Timeout(connect=30,read=30)
httpInston = None

def refreshHttp():
    print(datetime.now(),'刷新代理IP')
    global httpInston
    proxy_info = proxyHelper.get_singleton()
    # # 设置代理信息，这里以HTTP代理为例，如果是HTTPS代理，则将'http'改为'https'
    proxy_url = f'http://{minute_user}:{minute_pwd}@{proxy_info["ip"]}:{str(proxy_info["port"])}'
    ctx = initCtx()
    httpInston = urllib3.ProxyManager(proxy_url,ssl_context=ctx)

# 自定义加密套件的post请求
def request_urllib3_get(url,header=originHeader):
    global httpInston
    if httpInston:
        try:
            # 发送 POST 请求
            response = httpInston.request(
                'GET',
                url,
                headers=header,
                timeout=timeout
            )
            # 打印响应内容
            result = response.data.decode('utf-8')
            return result
        except Exception as e:
            print(datetime.now(),'请求发送失败,刷新代理5S后重试',e)
            refreshHttp()
            time.sleep(5)
            return request_urllib3_get(url,header)
    else:
        refreshHttp()
        return request_urllib3_get(url,header)
    

# 自定义加密套件的post请求
def request_urllib3_post(url,param,header=originHeader):
    global httpInston
    if httpInston:
        try:
            # 发送 POST 请求
            response = httpInston.request(
                'POST',
                url,
                headers=header,
                timeout=timeout,
                body=param,
                
            )
            # 打印响应内容
            result = response.data.decode('utf-8')
            return result
        except Exception as e:
            print(datetime.now(),'请求发送失败,刷新代理5S后重试',e)
            refreshHttp()
            time.sleep(5)
            return request_urllib3_post(url,param,header)
    else:
        refreshHttp()
        return request_urllib3_post(url,param,header)

#自定义加密套件请求，支持返回响应头
def request_urllib3_get_with_headers(url, header=originHeader):
    """
    发送GET请求并返回响应内容和header
    :param url: 请求URL
    :param header: 请求头
    :return: 包含响应内容和header的字典
    """
    global httpInston
    if httpInston:
        try:
            response = httpInston.request(
                'GET',
                url,
                headers=header,
                timeout=timeout
            )
            return {
                'content': response.data.decode('utf-8'),
                'headers': dict(response.headers)
            }
        except Exception as e:
            print(datetime.now(), '请求发送失败,刷新代理5S后重试', e)
            refreshHttp()
            time.sleep(5)
            return request_urllib3_get_with_headers(url, header)
    else:
        refreshHttp()
        return request_urllib3_get_with_headers(url, header)

    
# 设定main函数,程序起点
if __name__ == '__main__':
    try:
        a = f'http://{minute_user}:{minute_pwd}@'
        print(a)
    except Exception as err:
        print(f'任务执行失败',err)