import requests
from datetime import datetime
import json

insertUrl = 'http://10.220.6.138/api/khgz/project'
insertTestUrl = 'http://10.220.6.63:8090/api/khgz/project'

def fetch_project_info(name,url,dataSource):
    try:
        repeatUrl = 'http://10.220.6.138/api/khgz/project/getRepeat'
        header = {
            'Content-Type': 'application/json'
        }
        param = {
            'name': name,
            'url': url,
            'dataSource': dataSource
        }
        response = requests.post(url=repeatUrl,headers=header,json=param)
        data = json.loads(response.text)['data']
        return data
    except Exception as e:
        print(datetime.now(),'数据获取失败',e)
        return False

def insertProject(param):
    try:
        # print('插入数据',param['name'])
        header = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url=insertUrl,headers=header,json=[param])
        code = json.loads(response.text)['code']
        if code == 0 :
            print(datetime.now(),'新增成功:',param.get('name'))
        else:
            msg = json.loads(response.text)['msg']
            print(datetime.now(),param.get('name'),'-新增失败:',msg)

    except Exception as e:
        print(datetime.now(),param.get('name'),'-数据新增异常错误:',e)