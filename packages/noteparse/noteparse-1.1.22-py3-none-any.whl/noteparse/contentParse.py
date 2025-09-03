from datetime import datetime
import re
import requests
import json
from bs4 import BeautifulSoup
import traceback
import noteparse.dbHelper as dbHelper
from zhipuai import ZhipuAI,core
from noteparse.configReader import readConfig
import random
import PyPDF2
from urllib.parse import urlparse, parse_qs
from noteparse import requestHelper,ossHelper
import os
import time
# 金额正则
pattern = r'(\d+\.?\d*\s*(亿元|万元|元))'
phoneRe = r'^[-0-9、]+$'
# 项目编号正则
proejctNumPattern = r'(?:编号|代码|编码|标号)：([A-Za-z0-9-]+)'
# 字段对应关键字的set，有另外的直接加
keySet = {
    'bidUnit' : [
    '采购人：','转让方名称：',
    '比选人：','项目招标单位：',
    '发布单位：','项目委托单位：',
    '单位名称：','流标机构：',
    '招标人：',
    '招募人：',
    '业主单位：',
    '建设单位：',
    '项目单位：',
    '项目业主名称：',
    '法人单位：','招标人名称：','联系人（采购人）：','采购单位：','建设单位(招标人)：','建设单位(或招标人)：','招标（采购）人名称：','项目法人或招标人名称（盖章）：','招标人（盖章）：'
    ],
    'proxyUnit' : ['采购代理机构：','代理机构：','招标代理机构：','招募代理机构：','招标机构：','招标代理名称：','招标代理机构名称：',
                   '联系人（代理机构）：','招标代理：','代理全称：','比选代理机构：'],
    'contact' :  ['联系人：','项目法人：','申请人：',],
    'address' : ['地址：','建设地点：','项目所在地：'],
    'phone' : ['联系方式：','电话：','联系电话：'],
    'publishTime' : ['发布时间：','发布日期：','成交时间：'],
    'winBidUnit': ['成交供应商：','中标人：','中标人名称：','中标候选人名称：','供应商名称：','中标候选人单位名称：','中标单位：','中标单位名称：','中标供应商名称：','供应商：',
                   '中标（成交）单位名称：','第一中标（成交）候选人名称：','投标人：','投标人名称：','定标/成交结果：','供应商（乙方）：','受让方名称：'],
    'bidAmount': ['预算金额：','预算金额（元）：'],
    'winBidAmount': ['成交金额/成交下浮率：','中标价（费率或单价等）：','中标总价（元）/费率：','中标金额：','中标（成交）金额：','中标金额：',
                     '预期中标价/元：','成交金额：','投标价格：','中标标价：','中标价格：'],
    'bidContact': ['招标人联系人：','采购经办人：','采购负责人：','负责人：'],
    'bidPhone': ['招标人联系方式：','采购人联系方式：','招标人联系电话：','采购人联系电话：','采购人电话：'],
    'proxyContact': ['招标代理联系人：','代理机构经办人：'],
    'proxyPhone': ['招标代理联系方式：','代理机构电话：']
}
# zhiPuConf = readConfig('api_key',section='zhiPuAI')
# client = ZhipuAI(api_key=zhiPuConf['api_key']) # 填写您自己的APIKey
zhiPuConf = readConfig('api_key',section='zhiPuAI')
confs = zhiPuConf['api_key'].split('|')
length = len(confs)
randomNum = random.randint(0,length-1)
apiKey = confs[randomNum]
client = ZhipuAI(api_key=apiKey) # 填写您自己的APIKey


def clean_html(html_content):
    # 解析HTML内容
    soup = BeautifulSoup(html_content, 'html.parser')

    # 去除<script>和<style>标签及其内容
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()

    # 去除所有标签中的style属性
    for tag in soup.find_all(True):
        tag.attrs = {}
    # 或者使用正则表达式去除所有空白字符
    cleaned_html = re.sub(r'\s+', ' ', str(soup))    
    # 返回清理后的HTML字符串
    return cleaned_html

def parseHtmlByZhipu(htmlStr):
    try:
        global client
        print(datetime.now(),'开始请求质谱AI解析HTML文本')
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {
                    "role": "system",
                    "content": """你是一个HTML文本解析专家，专注与从html文本中提取出需要的字段信息，需要的字段和json的key对应信息如下[招标单位-bidUnit,招标单位联系人-bidContact,招标单位联系电话-bidPhone,
                    招标金额-bidAmount,招标代理单位-proxyUnit,招标代理单位联系人-proxyContact,招标代理单位联系人电话-proxyPhone,中标单位-winBidUnit,中标单位联系人-winBidContact,中标单位联系人电话-winBidPhone
                    ,中标金额-winBidAmount,项目编号-projectNum,公告发布时间-publishTime,投标截止时间-bidDdlTime,地址-address,省份-province,市-city,区-area]。结果用json数据返回，json的key全都取英文字段值，json数据
                    不要有额外的描述，如果没有对应字段信息，则字段值为空字符串。时间格式设为YYYY-MM-DD hh:mm:ss。特别注意判断金额单位，如果是元 直接返回数值 如果是万元或亿元，则在金额后面增加单位“万元”或“亿元”。如果金额是
                    中文大写，则转换成数字。注意，金额小于千亿都属于正常范围。注意，招标金额按优先程度取用顺序为 1、投标限价/2 标段合同估算价、3总投资额、4总金额、5起始价。如果文中没能提取出省市区名称，则另外再通过招标单位名称或项
                    目名称等其他信息重新分析一次,至少要保证省的名称提取正确。注意，中标单位指合同乙方、中标候选人、中标单位、供应商等。项目名称HTML文本如下:"""
                },
                {
                    "role": "user",
                    "content": htmlStr
                }
            ],
            top_p= 0,
            temperature= 0,
            max_tokens=3072,
            tools = [{"type":"web_search","web_search":{"search_result":True}}],
            stream=False,
            timeout=120
        )
        answerStr = response.choices[0].message.content
        print(datetime.now(),'质谱AI响应结果:',answerStr)
        result = json.loads(answerStr.replace('```','').replace('json',''))
        return result
    except core._errors.APITimeoutError:
        print(datetime.now(),'请求质谱AI解析HTML超时,15S后重试')
        time.sleep(15)
        return parseHtmlByZhipu(htmlStr)

    except Exception:
        print(datetime.now(),'请求质谱AI异常,解析失败')
        return None

def parseContent(htmlStr,noteInfo):
    print(datetime.now(),'开始解析公告文本',noteInfo['name'],noteInfo['url'])
    cleanHtmlStr = clean_html(htmlStr)
    result = parseHtmlByZhipu(cleanHtmlStr)
    if result == None:
        noteInfo['content'] = htmlStr
        return noteInfo
    if 'bidUnit' in result and result['bidUnit'] != '':
        noteInfo['bidUnit'] = result['bidUnit']
    if 'bidContact' in result and result['bidContact'] != '':
        noteInfo['bidContact'] = result['bidContact']
    if 'bidPhone' in result and result['bidPhone'] != '':
        # 手机号正则校验
        bidPhone = result['bidPhone']
        if re.match(phoneRe,bidPhone):
            noteInfo['bidPhone'] = bidPhone
        else:
            print(datetime.now(),f'bidPhone校验失败:{bidPhone}')
    if 'bidAmount' in result and result['bidAmount'] != '':
        bidAmountStr = result['bidAmount']
        # 去除123,123,12中的,
        bidAmountStr = bidAmountStr.replace(',','').replace('人民币','')
        try:
            if '万元' in bidAmountStr:
                bidAmountStr = bidAmountStr.replace('万元','')
                bidAmount = float(bidAmountStr) * 10000
            elif '亿元' in bidAmountStr:
                bidAmountStr = bidAmountStr.replace('亿元','')
                bidAmount = float(bidAmountStr) * 100000000
            elif '元' in bidAmountStr:
                bidAmountStr = bidAmountStr.replace('元','')
                bidAmount = float(bidAmountStr)
            else:
                bidAmount = float(bidAmountStr)
            
            if bidAmount > 100000000000:
                bidAmount = bidAmount / 10000

            noteInfo['bidAmount'] = bidAmount

        except Exception as parse_amount_err:
            print(datetime.now(),f'转换招标金额为float类型失败:{bidAmountStr}')
    if 'proxyUnit' in result and result['proxyUnit'] != '':
        noteInfo['proxyUnit'] = result['proxyUnit']
    if 'proxyContact' in result and result['proxyContact'] != '':
        noteInfo['proxyContact'] = result['proxyContact']
    if 'proxyPhone' in result and result['proxyPhone'] != '':
        # 手机号正则校验
        proxyPhone = result['proxyPhone']
        if re.match(phoneRe,proxyPhone):
            noteInfo['proxyPhone'] = proxyPhone
        else:
            print(datetime.now(),f'proxyPhone校验失败:{proxyPhone}')
    if noteInfo['noticeType'] == 1:
        # 如果是中标公告添加中标信息
        if 'winBidUnit' in result and result['winBidUnit'] != '':
            noteInfo['winBidUnit'] = result['winBidUnit']
        if 'winBidContact' in result and result['winBidContact'] != '':
            noteInfo['winBidContact'] = result['winBidContact']
        if 'winBidPhone' in result and result['winBidPhone'] != '':
            # 手机号正则校验
            winBidPhone = result['winBidPhone']
            if re.match(phoneRe,winBidPhone):
                noteInfo['winBidPhone'] = winBidPhone
            else:
                print(datetime.now(),f'winBidPhone校验失败:{winBidPhone}')
        if 'winBidAmount' in result and result['winBidAmount'] != '':
            winBidAmountStr = result['winBidAmount']
            # 去除123,123,12中的,
            winBidAmountStr = winBidAmountStr.replace(',','').replace('人民币','')
            try:
                if '万元' in winBidAmountStr:
                    winBidAmountStr = winBidAmountStr.replace('万元','')
                    winBidAmount = float(winBidAmountStr) * 10000
                elif '亿元' in winBidAmountStr:
                    winBidAmountStr = winBidAmountStr.replace('亿元','')
                    winBidAmount = float(winBidAmountStr) * 100000000
                elif '元' in winBidAmountStr:
                    winBidAmountStr = winBidAmountStr.replace('元','')
                    winBidAmount = float(winBidAmountStr)
                else:
                    winBidAmount = float(winBidAmountStr)
                # 超过千亿的项目默认不存在,除以10000
                if winBidAmount > 100000000000:
                    winBidAmount = winBidAmount / 10000
                
                noteInfo['winBidAmount'] = winBidAmount
            except Exception as parse_amount_err:
                print(datetime.now(),f'转换中标金额为float类型失败:{winBidAmountStr}')
    if 'projectNum' in result and result['projectNum'] != '':
        noteInfo['projectNum'] = result['projectNum']
    if 'bidDdlTime' in result and result['bidDdlTime'] != '':
        bidDdlTime = result['bidDdlTime']
        try:
            bidDdlDate = datetime.strptime(bidDdlTime,'%Y-%m-%d %H:%M:%S')
            noteInfo['bidDdlTime'] = bidDdlDate.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            try:
                bidDdlDate = datetime.strptime(bidDdlTime,'%Y-%m-%d')
                noteInfo['bidDdlTime'] = bidDdlDate.strftime('%Y-%m-%d %H:%M:%S')
            except Exception as parse_bidddl_err:
                print(datetime.now(),f'投标截止时间提取错误:{bidDdlTime}')
    if 'address' in result and result['address'] != '':
        noteInfo['address'] = result['address']
    
    provinceName = ''
    cityName = ''
    areaName = ''
    if 'area' in result and result['area'] != '':
        area = result['area']
        if '无' != area and '市辖区' != area:
            # noteInfo = parseCityId(area,noteInfo)
            areaName = area
    if 'city' in result and result['city'] != '':
        city = result['city']
        # noteInfo = parseCityId(city,noteInfo)
        cityName = city
    if 'province' in result  and result['province'] != '':
        province = result['province']
        # noteInfo = parseCityId(province,noteInfo)
        provinceName = province
    noteInfo = parseCityInfo(provinceName,cityName,areaName,noteInfo)
    
    if '元' in cleanHtmlStr:
        # 只要包含万元都重新解析一下,如果重新解析的金额大于原金额,则使用新答案
        # 最后验证金额是否正常
        if noteInfo['noticeType'] == 0 and ('bidAmount' not in noteInfo or noteInfo['bidAmount'] < 10000):
            noteInfo = getAmountZhipu(cleanHtmlStr,noteInfo)
        elif noteInfo['noticeType'] == 1 and ('winBidAmount' not in noteInfo or noteInfo['winBidAmount'] < 10000):
            noteInfo = getAmountZhipu(cleanHtmlStr,noteInfo)
    # if result['preWinBidList'] != None:
    #     noteInfo['preWinBidList'] = result['preWinBidList']
    # if result['evaluationList'] != None:
    #     noteInfo['evaluationList'] = result['evaluationList']
    
    print(datetime.now(),'---解析完毕,noteInfo=',noteInfo)
    noteInfo['content'] = htmlStr
    return noteInfo

def parseCityInfo(provinceName,cityName,areaName,noteInfo):
    cityInfo = dbHelper.queryCityInfoTotal(provinceName,cityName,areaName,noteInfo)
    if cityInfo == None:
        print(datetime.now(),f'{provinceName}-{cityName}-{areaName}无法定位城市信息')
        return noteInfo
    if 'provinceId' not in noteInfo:
        noteInfo['provinceId'] = cityInfo['provinceid']
    if 'cityId' not in noteInfo:
        noteInfo['cityId'] = cityInfo['cityid']
    if 'areaId' not in noteInfo:
        noteInfo['areaId'] = cityInfo['areaid']
    return noteInfo


# content--正文html; noteInfo--调接口的入参对象，其他如name、publishTime字段可以解析前就设定好noteInfo对象，以下解析是往里面加的
def parseContent2(content,noteInfo):
    contentDiv = BeautifulSoup(content,'html.parser')
    screenStr = []
    # 第一种是最普通的p标签分行
    pList = contentDiv.find_all('p')
    # print('--------len(plist)',pList)
    if pList and len(pList)>1:
        for p in pList:
            # 如果有br,每个br间隔都是一行
            contains_br = any(child.name == 'br' for child in p.children)
            if contains_br:
                text_and_tag = p.contents
                current_paragraph = ''
                for item in text_and_tag:
                    # 如果是string,进行拼接
                    if isinstance(item,str):
                        current_paragraph += item
                    # 如果是br换行,则停止拼接,将内容存入screenStr
                    elif item.name == 'br':
                        screenStr.append(current_paragraph.strip())
                        current_paragraph = ''
                    # 不是br也不是string,则就是一个元素,存入元素的字符串
                    else:
                        screenStr.append(item.text)
                if current_paragraph:
                    screenStr.append(current_paragraph.strip())
            # 如果一行多个信息,多是用空格分割,如:联系人：黄工/汪工 联系电话：0572-********
            elif  ' ' in p.text and p.text.count('：')>1:
                strList = p.text.split(' ')
                screenStr.extend(strList)
            elif u'\xa0' in p.text and p.text.count('：')>1:
                strList = p.text.split(u'\xa0')
                screenStr.extend(strList)                
            else:
                screenStr.append(p.text)
    # 如果没有P标签，或者p标签只有一个，尝试获取span标签，这类的公告可能用span标签取代p标签，但是span标签较细小，多是包在div、p标签内，所以不单独处理，否则screenStr内容会非常混乱，解析准确度更差
    else:
        spanList = contentDiv.find_all('span')
        for span in spanList:
            if ' ' in span.text and span.text.count('：')>1:
                strList = span.text.split(' ')
                screenStr.extend(strList)
            else:
                screenStr.append(span.text)
    try:
        # 第二种是table表格格式,按th和td的数量匹配分段的规则,进行标题和内容拼接
        tableList = contentDiv.find_all('table')
        for table in tableList:
            if table:
                trList = table.find_all('tr')
                if trList:
                    if len(trList) == 2:
                        # 先查看标题是不是用th标签
                        thList = trList[0].find_all('th')
                        tdList = trList[1].find_all('td')
                        if len(thList) == len(tdList):
                            # 只有两个tr,一个tr全是th,另一个全是td,则是成排的
                            for index,th in enumerate(thList):
                                screenStr.append(th.text+'：'+tdList[index].text)
                        elif len(thList) == 0:
                            # 如果没有th标签，查看第一个tr内是不是也是用的td标签
                            firstTdList = trList[0].find_all('td')
                            if len(firstTdList) == len(tdList):
                                for index,firstTd in enumerate(firstTdList):
                                    screenStr.append(firstTd.text+'：'+tdList[index].text)
                    for index,tr in enumerate(trList):
                        tdList = tr.find_all('td')
                        thList = tr.find_all('th')
                        # 表格里只有td标签的，一般是双数，一个标签td对一个值td
                        if len(thList)==0 and len(tdList) > 0:
                            if len(tdList) == 1:
                                screenStr.append(tdList[0].text)
                            elif len(tdList) % 2 == 0:
                                for i in range(0,int(len(tdList)),2) :
                                    if '：' in tdList[i].text:
                                        screenStr.append(tdList[i].text + tdList[i+1].text )
                                    elif ':' in tdList[i].text:
                                        screenStr.append(tdList[i].text.replace(':','：') + tdList[i+1].text )
                                    else:
                                        screenStr.append(tdList[i].text + '：' +tdList[i+1].text )    
                        # 表格里一个th和一个td的，一般是一个th标签对一个td标签
                        elif len(thList) == 1 and len(tdList) == 1:
                                if '：' in thList[0].text:
                                    screenStr.append(thList[0].text + tdList[0].text )
                                elif ':' in thList[0].text:
                                    screenStr.append(thList[0].text.replace(':','：') + tdList[0].text )
                                else:
                                    screenStr.append(thList[0].text + '：' +tdList[0].text )
                        elif len(tdList) == 0 and len(thList)>0:
                            if index < len(trList)-1:
                                nextThList = trList[index+1].find_all('th')
                                for index2,th in enumerate(thList):
                                    if '中标候选人名称' == th.text or '投标报价（元）' == th.text:
                                        screenStr.append(th.text+'：'+nextThList[index2].text)
    except Exception as parse_table_err:
        print(datetime.now(),'解析表格异常',parse_table_err)
    
                            
    
    # 第三种是div标签分段的,目前抽样到有br标签分行
    # if len(pList) == 0:
    divList = contentDiv.find_all('div')
    for divItem in divList:
        # 如果有br,每个br间隔都是一行
        contains_br = any(child.name == 'br' for child in divItem.children)
        if contains_br:
            text_and_tag = divItem.contents
            current_paragraph = ''
            for item in text_and_tag:
                if isinstance(item,str):
                    current_paragraph += item
                elif item.name == 'br':
                    screenStr.append(current_paragraph.strip())
                    current_paragraph = ''
                # 第四种是只有span标签的，这类的因为span标签太细小，大多都会包在div标签、p标签内，所以这类公告不单独分析，否则文本列表会非常混乱
                elif item.name == 'span':
                    screenStr.append(item.text.strip())
                    current_paragraph = ''
            if current_paragraph:
                screenStr.append(current_paragraph.strip())
        # 没有Br的，只保存只有一个：的段落，有些公告内使用div标签分行
        else:
            if divItem.text.count('：') == 1:
                screenStr.append(divItem.text)
    noteInfo = parseScreen(screenStr,noteInfo)

    noteInfo['content'] = content

    return noteInfo


def parseScreen(screenStr,noteInfo):
    amountStr = ''
    ddlTimeStr = ''
    for pStr in screenStr:
        text = re.sub('\s+','',pStr.replace(u'\xa0','').strip().replace('\n','').replace(':','：'))
        # print('======text:',text)
        projectNum = re.search(proejctNumPattern,text)
        if 'projectNum' not in noteInfo and projectNum:
            noteInfo['projectNum'] = projectNum.group(1)
        # 直接把包含元的内容全给GPT,让GPT识别
        if '元' in text:
            amountStr += text
            amountStr += ';'
        if '截止时间' in text:
            ddlTimeStr += text            
        # 如果文本中包含多个:,则不处理,因为无法判断需要的内容在第几个分号分割
        if text.count('：') > 1:
            continue
        # 因为有很多会有1.2采购人:xxx这种格式,所以只能用in,不能用startwith
        # 匹配上其中一个关键字之后就不用继续匹配了，优化效率
        hasMatched = False
        for keyword, field in keySet.items():
            if hasMatched:
                break
            for key in field:
                if key in text:
                    val = text.split('：')[1]
                    # 所有字段长度理论上都是大于1的，正好可以用来处理单位名称：空这类的情况
                    if val and len(val)>1:
                        if keyword == 'bidUnit' and 'bidUnit' not in noteInfo:
                            print('--------match bidunit-----',val)
                            noteInfo['bidUnit'] = val
                            hasMatched = True
                            break
                        elif keyword == 'proxyUnit' and '公章' not in val:
                            noteInfo['proxyUnit'] = val
                            hasMatched = True
                            break
                        elif keyword == 'winBidUnit' and 'winBidUnit' not in noteInfo:
                            noteInfo['winBidUnit'] = val
                            hasMatched = True
                            break
                        elif keyword == 'bidContact' and 'bidContact' not in noteInfo:
                            noteInfo['bidContact'] = val
                            hasMatched = True
                            break
                        elif keyword == 'bidPhone' and 'bidPhone' not in noteInfo:
                            noteInfo['bidPhone'] = val
                            hasMatched = True
                            break
                        elif keyword == 'proxyContact' and 'proxyContact' not in noteInfo:
                            noteInfo['proxyContact'] = val
                            hasMatched = True
                            break
                        elif keyword == 'proxyPhone' and 'proxyPhone' not in noteInfo:
                            noteInfo['proxyPhone'] = val
                            hasMatched = True
                            break
                        elif keyword == 'address' and 'address' not in noteInfo:
                            noteInfo['address'] = val
                            hasMatched = True
                            break
                        elif keyword == 'contact':
                            if 'bidContact' not in noteInfo:
                                noteInfo['bidContact'] = val
                            elif 'proxyContact' not in noteInfo:
                                noteInfo['proxyContact'] = val
                            
                            hasMatched = True
                            break
                        
                        elif keyword == 'phone':
                            phone = val.replace('拨打','')
                            if len(phone) > 25:
                                print(datetime.now(),'电话获取错误跳过',phone)
                                continue
                            if 'bidPhone' not in noteInfo:
                                noteInfo['bidPhone'] = phone
                            elif 'proxyPhone' not in noteInfo:
                                noteInfo['proxyPhone'] = phone                                       
                            hasMatched = True
                            break
                        elif keyword == 'winBidAmount':
                            try:
                                winBidAmount = val.replace(',','')
                                if winBidAmount.endswith('万元'):
                                    amount = float(winBidAmount.replace('万元','')) * 10000
                                    if amount > 100000000000:
                                        amount = amount / 10000   
                                    noteInfo['winBidAmount'] = amount
                                elif winBidAmount.endswith('亿元'):
                                    amount = float(winBidAmount.replace('亿元','')) * 100000000
                                    if amount > 100000000000:
                                        amount = amount / 10000   
                                    noteInfo['winBidAmount'] = amount
                                elif winBidAmount.endswith('元'):
                                    amount = float(winBidAmount.replace('元',''))
                                    if amount > 100000000000:
                                        amount = amount / 10000
                                    noteInfo['winBidAmount'] = amount
                                else:
                                    amount = float(amount)
                                    if amount > 100000000000:
                                        amount = amount / 10000
                                    noteInfo['winBidAmount'] = amount
                            except Exception as parse_amount_err:
                                print(datetime.now(),'中标金额转换失败',winBidAmount,parse_amount_err)
                        elif keyword == 'bidAmount':
                            match = re.search(pattern, val.replace(',',''))
                            if match: 
                                tender_number = match.group(1)
                                if '万' in tender_number:
                                    amountstr = tender_number.replace('万','').replace('元','')
                                    amount = float(amountstr) * 10000
                                    if amount > 100000000000:
                                        amount = amount / 10000
                                    noteInfo['bidAmount'] = amount
                                elif '亿' in tender_number:
                                    amountstr = tender_number.replace('亿','').replace('元','')
                                    amount = float(amountstr) * 100000000
                                    if amount > 100000000000:
                                        amount = amount / 10000
                                    noteInfo['bidAmount'] = amount
                                elif '元' in tender_number:
                                    amount = float(tender_number.replace('元',''))
                                    if amount > 100000000000:
                                        amount = amount / 10000
                                    noteInfo['bidAmount'] = amount
                                else:
                                    amount = float(amount)
                                    if amount > 100000000000:
                                        amount = amount / 10000
                                    noteInfo['bidAmount'] = amount
        # 名称这个词太宽泛,所以用startswith,以上词相对精准,可以用in匹配
        if text.startswith('名称：') or text.startswith('单位名称：'):
            if 'bidUnit' not in noteInfo:
                noteInfo['bidUnit'] = text.split('：')[1]
            elif 'proxyUnit' not in noteInfo:
                noteInfo['proxyUnit'] = text.split('：')[1]
        elif text.startswith('发布时间：') or text.startswith('发布日期：'):
            publishTime = parsePublishTime(text.split('：')[1])
            if 'publishTime' not in noteInfo:
                noteInfo['publishTime'] = publishTime

    if amountStr != '':
        # 最多传1000字
        if 'bidAmount' not in noteInfo and noteInfo['noticeType'] != 1:
            amount = getAmount(amountStr[:1000])
            print(datetime.now(),'amount',amount)
            if amount != None:
                # 中国省级GDP在1-10万亿，单个项目超过1000亿基本没有。基本就是错的
                if amount > 100000000000:
                    amount = amount / 10000                
                noteInfo['bidAmount'] = amount
        elif 'winBidAmount' not in noteInfo and noteInfo['noticeType'] == 1:
            amount = getAmount(amountStr[:1000])
            print(datetime.now(),'amount',amount)
            if amount != None:
                # 中国省级GDP在1-10万亿，单个项目超过1000亿基本没有。基本就是错的
                if amount > 100000000000:
                    amount = amount / 10000                
                noteInfo['winBidAmount'] = amount 

    if ddlTimeStr != '':
        ddlDate = getBidDdlTime(ddlTimeStr)
        if ddlDate != None:
            noteInfo['bidDdlTime'] = ddlDate.strftime('%Y-%m-%d %H:%M:%S')                                
    # noteInfo['content'] = ''
    # 尝试获取地市信息，如果报错，不影响其他字段插入
    try:
        if 'cityId' not in noteInfo and 'address' in noteInfo:
            # 优先使用招标单位地址查询公告所属地市
            noteInfo = parseCityId(noteInfo['address'],noteInfo) 
        # 如果通过公告名称无法提取地市名称，则通过项目名称查询
        if 'cityId' not in noteInfo:
            noteInfo = parseCityId(noteInfo['name'],noteInfo)
        # 如果通过招标单位地址无法提取地市名称，则通过采购单位名称查询
        if 'cityId' not in noteInfo and 'bidUnit' in noteInfo:
            noteInfo = parseCityId(noteInfo['bidUnit'],noteInfo)
    except Exception as get_city_info_err:
        print(datetime.now(),'通过文本查询地市信息异常',get_city_info_err)
                  
    print(datetime.now(),'----noteInfo:',noteInfo)  
    print(datetime.now(),'----解析完毕---')
    return noteInfo


def parseAreaName(areaName,noteInfo):
    cityInfoList = dbHelper.queryCityInfoByArea(areaName)
    print(datetime.now(),'查询到公告所属省市区为',cityInfoList)
    if len(cityInfoList)>0:
        cityInfo = cityInfoList[0]


def parseCityId(cityParseStr,noteInfo):
    cityName = getCityInfo(cityParseStr)
    if cityName and cityName not in ['无','市辖区']:
        # 如果有指定省份,则直接带省份信息查
        # 如果不带省份信息,则直接查询
        if 'provinceId' in noteInfo:
            cityInfoList = dbHelper.queryCityInProvince(cityName,noteInfo['provinceId'])
            print(datetime.now(),'查询到公告所属省市区为',cityInfoList)
            if len(cityInfoList)>0:
                cityInfo = cityInfoList[0]
                if '' != cityInfo[0]:
                    noteInfo['areaId'] = cityInfo[0]
                if '' != cityInfo[2]:
                    noteInfo['cityId'] = cityInfo[2]
        else:
            cityInfoList = dbHelper.queryCityInfo(cityName)
            print(datetime.now(),'查询到公告所属省市区为',cityInfoList)
            if len(cityInfoList)>0:
                cityInfo = cityInfoList[0]
                if '' != cityInfo[4]:
                    # # 如果noteInfo已经定位了省份，则验证省份ID是否正确，正确则添加cityId或areaId,如果不正确，则地区匹配错误不作更新
                    # if 'provinceId' in noteInfo:
                    #     if noteInfo['provinceId'] == cityInfo[4]:
                    #         if '' != cityInfo[0]:
                    #             noteInfo['areaId'] = cityInfo[0]
                    #         if '' != cityInfo[2]:
                    #             noteInfo['cityId'] = cityInfo[2]
                    #     else:
                    #         print(datetime.now(),'获取到地市信息与当前provinceId不符，数据抛弃')
                    # else:
                    # 如果noteInfo没有定位省份，则直接添加provinceId，cityId和areaId
                    noteInfo['provinceId'] = cityInfo[4]
                    if '' != cityInfo[0]:
                        noteInfo['areaId'] = cityInfo[0]
                    if '' != cityInfo[2]:
                        noteInfo['cityId'] = cityInfo[2]
    return noteInfo

def getBidDdlTime(ddlTimeStr):
    try:
        global client
        print(datetime.now(),'请求GPT解析截止时间:',ddlTimeStr)
        # client = ZhipuAI(api_key="9ece6c42cdca139afa262b16c93814d5.qVKFvLXWFfwuaHgp") # 填写您自己的APIKey
        response = client.chat.completions.create(
            model="glm-4-flash",  # 填写需要调用的模型编码
            messages=[
                {"role": "system", "content": "# 角色：您是项目信息提取专家，专注于从项目公告的片段中提取投标文件的截止时间等## 技能：截止时间提取## 约束条件###1、时间来自用户输入原文###2、仅保留一个结果###3、结果按截止时间：XXXX-XX-XX XX:XX:XX的格式返回，且不要有其他描述，只显示一个截止时间即可###4、若结果没有秒数，则默认补充秒数为00###5、输出结果之前验算一下约束条件### 示例互动流程- **用户询问**：凡有意参加投标者，请于2024年10月16日00时00分至2024年10月23日23时59分（北京时间，下同），登录全国公共资源交易平台，通过数字证书免费下载招标文件（含招标文件的澄清、修改，通知等内容）。6.1 投标文件递交的截止时间（投标截止时间，下同）为2024年11月6日9时30分，投标人应在截止时间前通过登录全国- **处理步骤**：  1. 按分号；分割用户输入的内容  2. 遍历每一段内容并理解用户输入  3. 拆分出各个金额及金额对应的意思 4. 按照截止时间：XXXX-XX-XX XX:XX:XX的格式设定输出结果 -**输出结果案例**：截止时间：2024-11-06 09:30:00 "},
                {"role": "user", "content": "请提取下文中的截止时间，只需回答截止时间即可，不要有其他描述，文本如下：%s" % (ddlTimeStr)}
            ],
        )
        resContent = response.choices[0].message.content
        print(datetime.now(),'GPT解析截止时间结果:',resContent)

        if '：' in resContent:
            ddlRes = resContent.split('：')[1]
            ddlTime = datetime.strptime(ddlRes,'%Y-%m-%d %H:%M:%S')
        else:
            ddlTime = datetime.strptime(resContent,'%Y-%m-%d %H:%M:%S')
        return ddlTime
    except Exception as parse_ddl_err:
        print(datetime.now(),'GPT解析截止时间错误:',parse_ddl_err)
        return None
    
def getAmountZhipu(htmlStr,noteInfo):
    try:
        print(datetime.now(),'金额异常,继续提取金额')
        global client
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {
                    "role": "system",
                    "content": f"你是一个金额提取专家，专门从html文本中提取所需的项目招标金额、中标金额。结果用json数据返回。招标金额字段用bidAmount，中标金额字段用winBidAmount。特别注意html中使用table表格显示时，金额的单位可能会在表格的某个th或td标签中。若单位是万元或亿元，请携带在响应结果中。HTML文本如下：" 
                },
                {
                    "role": "user",
                    "content": htmlStr
                }
            ],
            top_p= 0,
            temperature= 0,
            max_tokens=3072,
            tools = [{"type":"web_search","web_search":{"search_result":True}}],
            stream=False,
            # response_format={"type":"json_object"}
            timeout=120

        )
        
        answerStr = response.choices[0].message.content
        print(datetime.now(),'GPT金额提取结果:',answerStr)
        result = json.loads(answerStr.replace('```','').replace('json',''))
        if 'bidAmount' in result and result['bidAmount'] != '' and result['bidAmount'] != None:
            bidAmountStr = result['bidAmount']
            # 去除123,123,12中的,
            bidAmountStr = bidAmountStr.replace(',','')
            try:
                if '万元' in bidAmountStr:
                    bidAmountStr = bidAmountStr.replace('万元','')
                    bidAmount = float(bidAmountStr) * 10000
                elif '亿元' in bidAmountStr:
                    bidAmountStr = bidAmountStr.replace('亿元','')
                    bidAmount = float(bidAmountStr) * 100000000
                elif '元' in bidAmountStr:
                    bidAmountStr = bidAmountStr.replace('元','')
                    bidAmount = float(bidAmountStr)
                else:
                    bidAmount = float(bidAmountStr)
                
                if bidAmount > 100000000000:
                    bidAmount = bidAmount / 10000

                noteInfo['bidAmount'] = bidAmount

            except Exception as parse_amount_err:
                print(datetime.now(),f'转换招标金额为float类型失败:{bidAmountStr}')
        
        if noteInfo['noticeType'] == 1:
            if 'winBidAmount' in result and result['winBidAmount'] != '' and result['winBidAmount'] != None:
                winBidAmountStr = result['winBidAmount']
                # 去除123,123,12中的,
                winBidAmountStr = winBidAmountStr.replace(',','')
                try:
                    if '万元' in winBidAmountStr:
                        winBidAmountStr = winBidAmountStr.replace('万元','')
                        winBidAmount = float(winBidAmountStr) * 10000
                    elif '亿元' in winBidAmountStr:
                        winBidAmountStr = winBidAmountStr.replace('亿元','')
                        winBidAmount = float(winBidAmountStr) * 100000000
                    elif '元' in winBidAmountStr:
                        winBidAmountStr = winBidAmountStr.replace('元','')
                        winBidAmount = float(winBidAmountStr)
                    else:
                        winBidAmount = float(winBidAmountStr)
                    # 超过千亿的项目默认不存在,除以10000
                    if winBidAmount > 100000000000:
                        winBidAmount = winBidAmount / 10000
                    
                    noteInfo['winBidAmount'] = winBidAmount
                except Exception as parse_amount_err:
                    print(datetime.now(),f'转换中标金额为float类型失败:{winBidAmountStr}')
        return noteInfo
    except core._errors.APITimeoutError:
        print(datetime.now(),'请求质谱AI解析金额超时,15S后重试')
        return getAmount(htmlStr,noteInfo)

    except Exception as get_amount_err:
        print(datetime.now(),'质谱AI解析金额失败',get_amount_err)
        return noteInfo
    # client = ZhipuAI(api_key="9ece6c42cdca139afa262b16c93814d5.qVKFvLXWFfwuaHgp") # 填写您自己的APIKey


def getAmount(amountStr):
    try:
        global client
        print(datetime.now(),'请求GPT获取金额:',amountStr)
        response = client.chat.completions.create(
            model="glm-4-flash",  # 填写需要调用的模型编码
            messages=[
                {"role": "system", "content": "# 角色：您是项目金额提取专家，专注于从项目公告的片段中提取项目金额等## 技能：项目金额提取## 约束条件###1、所有项目金额全部来自用户输入原文###2、所有金额转换为XXX元###3、仅保留一个结果###4、缴纳材料费、注册资本不是招标金额###5、预算金额，中标金额，招标金额，合同金额，项目投资，施工合同估算价，工程造价这些词都是项目金额，如果没有这些描述，取意思最相近的金额。如果确实无法匹配项目金额，返回项目金额：0元###6、如果有多个金额都是项目金额的描述，取金额最大的一个数字返回###7、结果按项目金额：XXX元的格式返回，且不要有其他描述，只显示一个项目金额：xx元即可###8、输出结果之前验算一下约束条件### 示例互动流程- **用户询问**：预算金额（万元）：233.0000000；最高限价（如有）：2350000.00元；售价：0元- **处理步骤**：  1. 按分号；分割用户输入的内容  2. 遍历每一段内容并理解用户输入  3. 拆分出各个金额及金额对应的意思  4. 分辨拆分出的金额哪一个才是公告的项目金额，如果金额单位是万元，则直接返回万元单位的结果，如果金额单位是亿元，则直接返回亿元单位的结果 5. 按照项目金额：xxx元的格式设定输出结果    7. 输出结果-**输出结果案例**：项目金额：233.0000000万元"},
                {"role": "user", "content": "请提取下文中的项目金额，只需回答项目金额：xx元或者项目金额：xx万元即可，不要有其他描述，文本如下：%s" % (amountStr)}
            ],
        )
        answerStr = response.choices[0].message.content
        print(datetime.now(),'GPT金额提取结果:',answerStr)
        match = re.search(pattern, answerStr.replace(',',''))  
        if match:  
            # 提取并打印招标编号  
            tender_number = match.group(1)
            if '万元' in tender_number:
                amountstr = tender_number.replace('万元','')
                amount = float(amountstr) * 10000
                print(datetime.now(),'最终项目金额:',amount)
                return amount
            elif '亿元' in tender_number:
                amountstr = tender_number.replace('亿元','')
                amount = float(amountstr) * 100000000
                print(datetime.now(),'最终项目金额:',amount)
                return amount
            elif '元' in tender_number:
                amount = float(tender_number.replace('元',''))
                print(datetime.now(),'最终项目金额:',amount)
                return amount
            else:
                amount = float(tender_number)
                print(datetime.now(),'最终项目金额:',amount)
                return amount
        else:
            # print(type(resContent))
            return None    
    except Exception as get_amount_err:
        print(datetime.now(),'GPT解析金额失败',get_amount_err)
        return None
    # client = ZhipuAI(api_key="9ece6c42cdca139afa262b16c93814d5.qVKFvLXWFfwuaHgp") # 填写您自己的APIKey
    
def getProvinceId(provinceStr):
    try:
        print(datetime.now(),'请求GPT提取省份信息:',provinceStr)
        response = client.chat.completions.create(
            model="glm-4-flash",  # 填写需要调用的模型编码
            messages=[
                {"role": "system", "content": "# 角色：您是项目所属省提取专家，专注于从项目公告中确认省份## 技能：项目省份匹配## 约束条件###1、项目所属地名一定在用户输入的原文内，不要杜撰###2、仅保留一个结果###3、结果按JSON格式返回，如{'provinceId': '330000','provinceName': '浙江'}###4、如果文中没有明确写明所属地，则返回空值即可###5、provinceId一定是0000结尾的###6、抛弃街道、社区、村等小范围的信息，只根据省市区信息进行匹配，如果内容只有街道、社区、村这类小范围信息，则provinceId和provinceName返回空值。###6、输出结果之前验算一下约束条件### 示例互动流程- **用户询问**：陕西省渭南市秦岭北麓（东部）森林火灾高风险区综合治理工程建设项目招标公告 **处理步骤**：   7. 输出结果-**输出结果案例**：{'provinceId': '610000','provinceName': '陕西'}"},
                {"role": "user", "content": "请提取内容所属的省份信息，文本如下%s" % (provinceStr)}
            ],
        )
        resContent = response.choices[0].message.content

        result = resContent.replace('```','').replace('json','').replace(' ','').replace("'",'"')
        try:
            data =  json.loads(result)
            provinceName = data['provinceName']
            if provinceName and provinceName != '':
                provinceId = dbHelper.queryProvinceId(provinceName)
                print(datetime.now(),'GPT提取省份结果:',provinceName,provinceId)

                return str(provinceId[0])
            else:
                return None
        except Exception as parse_province_json_err:
            print(datetime.now(),'解析GPT响应json错误')
            return None
        # if '项目所属地：'in resContent:  
        #     # 提取并打印招标编号  
        #     cityName = resContent.split('：')[1]
        #     return cityName
        # else:
        #     return None
        # return resContent

    except Exception as parse_city_err:
        print(datetime.now(),'GPT解析地市失败',parse_city_err)
        return None

def getCityInfo(cityInfoStr):
    try:
        print(datetime.now(),'请求GPT提取地市名称:',cityInfoStr)
        response = client.chat.completions.create(
            model="glm-4-flash",  # 填写需要调用的模型编码
            messages=[
                {"role": "system", "content": "# 角色：您是项目所属地提取专家，专注于从项目公告中地名## 技能：项目地名提取## 约束条件###1、项目所属地名一定在用户输入的原文内，不要杜撰###2、如果项目名同时包含省、市、区，只返回区名###3、仅保留一个结果###3、结果按项目所属地：XXX的格式返回，且不要有其他描述，只显示一个项目所属地：xx市/区即可###4、如果文中没有明确写明所属地，则范围空值即可###8、输出结果之前验算一下约束条件### 示例互动流程- **用户询问**：陕西省渭南市秦岭北麓（东部）森林火灾高风险区综合治理工程建设项目招标公告 **处理步骤**：  1. 先提取出用户输入文本内包含的省市区地名，如陕西省、渭南市  2. 遍历提取出的地名，判断地名数量，地名是属于省还是地市还是地区  3. 按地区>地市>省份的优先级排序  4. 取最高优先级的地名拼凑结果    7. 输出结果-**输出结果案例**：项目所属地：渭南"},
                {"role": "user", "content": "请提取下标题中的的项目所属地，只需回答项目所属地：xx即可，不要有其他描述，文本如下%s" % (cityInfoStr)}
            ],
        )
        resContent = response.choices[0].message.content
        print(datetime.now(),'GPT提取地市名称结果:',resContent)

        if '项目所属地：'in resContent:  
            # 提取并打印招标编号  
            cityName = resContent.split('：')[1]
            return cityName
        else:
            return None

    except Exception as parse_city_err:
        print(datetime.now(),'GPT解析地市失败',parse_city_err)
        return None

# 这个函数的目标是输入内容，让AI直接返回省-市-地，但是当前质谱AI的省市地匹配不准确。当只有地名时无法返回完整信息。比如输入“盐城人社局”，会响应无。暂时不能使用
def getCityAndProvince(cityInfoStr):
    try:
        print(datetime.now(),'请求GPT提取地市名称:',cityInfoStr)
        response = client.chat.completions.create(
            model="glm-4-flash",  # 填写需要调用的模型编码
            messages=[
                {"role": "system", "content": "# 角色：您是项目所属省市提取专家，专注于从项目公告中省和地名## 技能：项目地名提取## 约束条件###1、项目所属地名一定在用户输入的原文内，不要杜撰###2、如果无法确定省份,则返回无###3、仅保留一个结果###3、结果按项目所属地：XX-XXX的格式返回，且不要有其他描述，只显示一个项目所属地：xx省-xx市/区即可###4、输出结果之前验算一下约束条件### 示例互动流程- **用户询问**：陕西省渭南市秦岭北麓（东部）森林火灾高风险区综合治理工程建设项目招标公告 **处理步骤**：  1. 先提取出用户输入文本内包含的省市区地名，如陕西省、渭南市  2. 输出结果-**输出结果案例**：项目所属地：陕西-渭南"},
                {"role": "user", "content": "请提取下标题中的的项目所属地，只需回答项目所属地：xx-xx即可，不要有其他描述，文本如下%s" % (cityInfoStr)}
            ],
        )
        resContent = response.choices[0].message.content
        print(datetime.now(),'GPT提取地市名称结果:',resContent)

        if '项目所属地：'in resContent:  
            # 提取并打印招标编号  
            cityName = resContent.split('：')[1]
            return cityName
        else:
            return None

    except Exception as parse_city_err:
        print(datetime.now(),'GPT解析地市失败',parse_city_err)
        return None

def parsePublishTime(str):
    publishTimeStr = str.replace('：',':').replace('/','-').strip()
    try:
        if '-' in publishTimeStr:
            semCount = publishTimeStr.count(':')
            if semCount == 0:
                dateObj = datetime.strptime(publishTimeStr,'%Y-%m-%d')
                # 如果时间是同一天，但是没有详细时间，返回当前的详细时间
                if dateObj.date() == datetime.now().date():
                    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                else:
                    return dateObj.strftime('%Y-%m-%d %H:%M:%S')
            elif semCount == 1:
                dateObj = datetime.strptime(publishTimeStr,'%Y-%m-%d %H:%M')
                return dateObj.strftime('%Y-%m-%d %H:%M:%S')            
            elif semCount == 2:
                dateObj = datetime.strptime(publishTimeStr,'%Y-%m-%d %H:%M:%S')
                return dateObj.strftime('%Y-%m-%d %H:%M:%S')
        elif '年' in publishTimeStr:
            semCount = publishTimeStr.count(':')
            if semCount == 0:
                dateObj = datetime.strptime(publishTimeStr,'%Y年%m月%d日')
                return dateObj.strftime('%Y-%m-%d %H:%M:%S')
            elif semCount == 1:
                dateObj = datetime.strptime(publishTimeStr,'%Y年%m月%d日 %H:%M')
                return dateObj.strftime('%Y-%m-%d %H:%M:%S')            
            elif semCount == 2:
                dateObj = datetime.strptime(publishTimeStr,'%Y年%m月%d日 %H:%M:%S')
                return dateObj.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    except Exception as parse_date_err:
        print(datetime.now(),'时间识别错误，发布时间默认为当前时间',parse_date_err)
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')  



def remove_space(str):
    return ' '.join(str.split())

# 部分网站公告是用iframe嵌入pdf链接展示的，可获取pdf链接后直接调用该方法进行字段信息的解析
def parsePdfWithUrl(pdfUrl,noteInfo):
    try:
        
        pdfResponse = requestHelper.request_get(pdfUrl)
        fileName = noteInfo['name']+ ossHelper.generate_snowflake_id() + ".pdf"
        try:
            # 检查请求是否成功
            if pdfResponse.status_code == 200:
                # 将PDF文件保存到本地
                with open(fileName, 'wb') as file:
                    file.write(pdfResponse.content)
            else:
                print(f"Failed to download PDF: {pdfResponse.status_code}")

            noteInfo = getPdfContent(fileName,noteInfo)
            ossFileUrl = ossHelper.upload_file_to_minio(fileName,'pdf/'+fileName)
            noteInfo['accessory'] = 'https://'+ossFileUrl
        except Exception as get_pdf_err:
            print(datetime.now(),f'获取pdf内容失败',get_pdf_err)
            traceback.print_exc()
        finally:
            if os.path.exists(fileName):
                os.remove(fileName)
        return noteInfo
    except Exception as get_detail_err:
        print(datetime.now(),'获取详情异常',get_detail_err)
        traceback.print_exc()

# 部分网站公告是用iframe嵌入pdf链接展示的，可获取pdf链接后直接调用该方法进行字段信息的解析
def parsePdfInIframe(pdfUrl,noteInfo):
    try:
        # 解析URL
        parsed_url = urlparse(pdfUrl)

        # 获取查询参数
        query_params = parse_qs(parsed_url.query)

        # 获取file参数的值
        file_param_value = query_params.get('file', [None])[0]
        print(file_param_value)
        pdfResponse = requestHelper.request_get(file_param_value)
        # pdfResponse = requestHelper.request_get(pdfUrl)
        fileName = noteInfo['name']+ ossHelper.generate_snowflake_id() + ".pdf"
        try:
            # 检查请求是否成功
            if pdfResponse.status_code == 200:
                # 将PDF文件保存到本地
                with open(fileName, 'wb') as file:
                    file.write(pdfResponse.content)
            else:
                print(f"Failed to download PDF: {pdfResponse.status_code}")

            noteInfo = getPdfContent(fileName,noteInfo)
            ossFileUrl = ossHelper.upload_file_to_minio(fileName,'pdf/'+fileName)
            noteInfo['accessory'] = 'https://'+ossFileUrl
        except Exception as get_pdf_err:
            print(datetime.now(),f'获取pdf内容失败',get_pdf_err)
            traceback.print_exc()
        finally:
            if os.path.exists(fileName):
                os.remove(fileName)
        return noteInfo
    except Exception as get_detail_err:
        print(datetime.now(),'获取详情异常',get_detail_err)
        traceback.print_exc()

# 读取PDF文件内容并解析项目信息--PDF默认是OSS的地址
def getPdfContent(pdfPath,noteInfo):

    objFile = open(pdfPath,'rb')
    objPdfReader = PyPDF2.PdfReader(objFile) #打开pdf
 
    nPages = objPdfReader.pages #获取总页数
    content = ''
    screenList = []
    for nPageIndex in range(len(nPages)):
        objPage = objPdfReader.pages[nPageIndex] #获取某页
        strContent = objPage.extract_text()
        content += strContent
        list1 = strContent.split('\n')
        screenList.extend(list1)
        # print("strContent",strContent.split('\n')) #打印内容
    
    objFile.close() #关闭
    noteInfo = parseScreen(screenList,noteInfo)
    noteInfo['content'] = content
    return noteInfo


def remove_table_styles(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 找到所有table相关的标签
    table_tags = soup.find_all(['table', 'tr', 'td', 'th', 'thead', 'tbody', 'tfoot','p','span','font'])
    
    for tag in table_tags:
        # 移除style属性
        if tag.has_attr('style'):
            del tag['style']
        # 移除class属性
        if tag.has_attr('class'):
            del tag['class']
        # 移除其他样式相关属性
        style_attrs = ['bgcolor', 'width', 'height', 'align', 'valign', 'cellpadding', 'cellspacing', 'border']
        for attr in style_attrs:
            if tag.has_attr(attr):
                del tag[attr]
    
    return str(soup)

# 设定main函数,程序起点
if __name__ == '__main__':
    try:
    #    noteInfo = testMatch('电话：ABC公司')
        pStr = '广信区茶亭片区环境品质提升项目材料设备采购项目招标公告'
        a = '''
           
        <html>
        <head>
            <style>
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid black; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body style="font-family: Arial, sans-serif;">
        
<p>终止公告</p>

<p>一、采购单编号：P-XJ-25-00303749</p>


<p>二、采购单名称：特许经营公司二郎项目2024年厂前区至生产值班楼A区增设封闭式步行廊道工程</p>


<p>三、采购执行单位：重庆远达烟气治理特许经营有限公司</p>


<p>四、采购执行人：耿朋飞</p>


<p>五、采国 购执行人联系方式：18503750201 国 国 国</p>
<p>六、采购终止原因：经评审后无合格供应商，流标处理/重新采购.</p>
<p>发布日期：2025-01-16</p>
<p>（盖章）</p>






























</body></html>
        ''' 
        noteInfo ={
            'noticeType': 0,
            'name': 'dfasdfa',
            'url': 'fsdfasd'
        }
        b = parseContent(a,noteInfo)
        print(b)

    except Exception as err:
        print(f'任务执行失败',err)
        traceback.print_exc()
        

