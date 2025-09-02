# -*- coding: UTF-8 -*-
"""
@File    ：dingTalkMsgHelper.py
@Author  ：VerSion/08398
@Date    ：2023/12/08 11:28 
@Corp    ：Uniview
"""

import json
from datetime import datetime
from noteparse.configReader import readConfig

import requests

dingConf = readConfig('ding_url','app_key','app_secret','agent_id','rebot_code','user_id_license',section='dingTalkConfig')

def get_token():
    """
    获取钉钉接口token
    :return: token字符串
    """
    try:
        url = f"{dingConf['ding_url']}/gettoken?appkey={dingConf['app_key']}&appsecret={dingConf['app_secret']}"
        response = requests.get(url)
        result = json.loads(response.text)
        if result['errcode'] == 0:
            return result['access_token']
        else:
            raise Exception(result['errmsg'])
    except Exception as ex:
        raise Exception('获取token失败：' + str(ex))


def get_user_id(user_no):
    """
    根据工号查询员工的钉钉userid
    :param user_no:员工工号（带首字母，例如Z00001）
    :return:传入员工的钉钉userid
    """
    url = "https://dip.uniview.com/api/interface/query/getUserIdByUserNo"
    request_headers = {
        "license": dingConf['user_id_license']
    }
    request_body = {
        "userNo": user_no.upper()
    }

    try:
        response = requests.post(url, headers=request_headers, json=request_body)
        if response.status_code == 200:
            data = response.json()
            if data["isSuccess"]:
                rtn_list = data["rtnList"]
                if rtn_list and len(rtn_list) > 0:
                    return rtn_list[0]["USERID"]
                else:
                    raise Exception(f'员工 {user_no} 不存在')
            else:
                raise Exception(data["rtnMsg"])
        else:
            raise Exception('接口调用失败，失败代码 ' + str(response.status_code))
    except Exception as ex:
        raise Exception('获取userid失败：' + str(ex))


def send_dingwork_message(access_token, userid_list, content):
    """
    向用户发送钉钉消息
    :param access_token:钉钉接口token
    :param userid_list:用户的userid列表字符串，多个用户间用英文逗号隔开
    :param content:消息正文
    :return:是否发送成功
    """
    try:
        url = f"{dingConf['ding_url']}/topapi/message/corpconversation/asyncsend_v2?access_token={access_token}"
        request_headers = {
            'Content-Type': 'application/json'
        }
        request_body = {
            'agent_id': dingConf['agent_id'],
            'userid_list': userid_list,
            'msg': {
                'msgtype': 'text',
                'text': {
                    'content': content
                }
            }
        }

        response = requests.post(url, headers=request_headers, json=request_body)
        if response.status_code == 200:
            data = response.json()
            errcode = data['errcode']
            errmsg = data['errmsg']
            if errcode == 0:
                return True
            else:
                raise Exception(errmsg)
        else:
            raise Exception('接口调用失败，失败代码 ' + str(response.status_code))
    except Exception as ex:
        raise Exception('发送钉钉消息失败：' + str(ex))


def send_dingwork_card(access_token, userid_list, title, content, button_url, button_title="查看详情"):
    """
    向用户发送钉钉卡片消息
    :param access_token:钉钉接口token
    :param userid_list:用户的userid列表字符串，多个用户间用英文逗号隔开
    :param title: 消息标题
    :param content:消息正文（支持markdown语法）
    :param button_url: 下方跳转按钮的链接
    :param button_title: 下方跳转按钮的标题
    :return:是否发送成功
    """
    try:
        url = f"{dingConf['ding_url']}/topapi/message/corpconversation/asyncsend_v2?access_token={access_token}"
        request_headers = {
            'Content-Type': 'application/json'
        }
        request_body = {
            'agent_id': dingConf['agent_id'],
            'userid_list': userid_list,
            'msg': {
                'msgtype': 'action_card',
                'action_card': {
                    'title': title,
                    'markdown': content,
                    'single_title': button_title,
                    'single_url': button_url
                }
            }
        }

        response = requests.post(url, headers=request_headers, json=request_body)
        if response.status_code == 200:
            data = response.json()
            errcode = data['errcode']
            errmsg = data['errmsg']
            if errcode == 0:
                return True
            else:
                raise Exception(errmsg)
        else:
            raise Exception('接口调用失败，失败代码 ' + str(response.status_code))
    except Exception as ex:
        raise Exception('发送钉钉消息失败：' + str(ex))


def send_dingwork_card_by_robot(access_token, userid_list, title, content, button_url, button_title="查看详情"):
    """
    通过机器人向用户发送钉钉卡片消息
    :param access_token:钉钉接口token
    :param userid_list:用户的userid列表字符串，多个用户间用英文逗号隔开
    :param title: 消息标题
    :param content:消息正文（支持markdown语法）
    :param button_url: 下方跳转按钮的链接
    :param button_title: 下方跳转按钮的标题
    :return:是否发送成功
    """
    try:
        url = f'https://api.dingtalk.com/v1.0/robot/oToMessages/batchSend'
        request_headers = {
            'Content-Type': 'application/json',
            'x-acs-dingtalk-access-token': access_token
        }
        msg_param = {
            'title':title,
            'text':content,
            'singleTitle':button_title,
            'singleURL':button_url
        }
        request_body = {
            'robotCode': dingConf['rebot_code'],
            'userIds': userid_list,
            'msgKey': 'sampleActionCard',
            'msgParam':json.dumps(msg_param, ensure_ascii=False)
        }

        response = requests.post(url, headers=request_headers, json=request_body)
        if response.status_code == 200:
            return True
        else:
            err_obj = response.json()
            errcode = err_obj['code']
            errmsg = err_obj['message']
            raise Exception(f'接口调用失败，失败代码[{errcode}]：{errmsg}')
    except Exception as ex:
        raise Exception('机器人发送钉钉消息失败：' + str(ex))


def send_msg_to_employee(employee_list, content):
    """
    根据工号发送钉钉消息
    :param employee_list: 字符串数组，内容为员工带首字母的工号。例如：['Z00001','X00002']
    :param content:
    :return:
    """
    try:
        if not isinstance(employee_list, list) or not all(isinstance(e, str) for e in employee_list):
            raise TypeError("传入参数employee_list必须是字符串数组")
        userid_list = ",".join([get_user_id(employee) for employee in employee_list])
        token = get_token()
        now = datetime.now()
        formatted_time = now.strftime("[%Y-%m-%d %H:%M:%S]")
        content_with_time = content + " " + formatted_time
        return send_dingwork_message(token, userid_list, content_with_time)
    except Exception as ex:
        raise ex


def send_card_to_employee(employee_list, title, content, button_url, button_title="查看详情"):
    """
    根据工号发送钉钉卡片消息
    :param employee_list: 字符串数组，内容为员工带首字母的工号。例如：['Z00001','X00002']
    :param title: 消息标题
    :param content:消息正文（支持markdown语法）
    :param button_url: 下方跳转按钮的链接
    :param button_title: 下方跳转按钮的标题
    :return:是否发送成功
    """
    try:
        if not isinstance(employee_list, list) or not all(isinstance(e, str) for e in employee_list):
            raise TypeError("传入参数employee_list必须是字符串数组")
        userid_list = ",".join([get_user_id(employee) for employee in employee_list])
        token = get_token()
        now = datetime.now()
        formatted_time = now.strftime("[%Y-%m-%d %H:%M:%S]")
        content_with_time = content + "<br>" + formatted_time
        return send_dingwork_card(token, userid_list, title, content_with_time, button_url, button_title)
    except Exception as ex:
        raise ex

def send_card_to_employee_by_robot(employee_list, title, content, button_url, button_title="查看详情"):
    """
    根据工号通过机器人发送钉钉卡片消息
    :param employee_list: 字符串数组，内容为员工带首字母的工号。例如：['Z00001','X00002']
    :param title: 消息标题
    :param content:消息正文（支持markdown语法）
    :param button_url: 下方跳转按钮的链接
    :param button_title: 下方跳转按钮的标题
    :return:是否发送成功
    """
    try:
        if not isinstance(employee_list, list) or not all(isinstance(e, str) for e in employee_list):
            raise TypeError("传入参数employee_list必须是字符串数组")
        userid_list = [get_user_id(employee) for employee in employee_list]
        token = get_token()
        return send_dingwork_card_by_robot(token, userid_list, title, content, button_url, button_title)
    except Exception as ex:
        raise ex