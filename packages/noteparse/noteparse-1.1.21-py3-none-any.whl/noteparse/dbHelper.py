import pymysql
from datetime import datetime
import traceback
from noteparse.configReader import readConfig
import atexit
import json

db_config = readConfig('host','port','user','password','db',section='dbConfig')


# 创建数据库连接
def create_connection():
    try:
        print(datetime.now(),'开启数据库链接')
        # 连接数据库
        connection = pymysql.connect(host=db_config['host'], port=int(db_config['port']),
                        user=db_config['user'], password=db_config['password'],
                        db=db_config['db'])
        print(datetime.now(),'数据库链接成功')
    except pymysql.MySQLError as e:
        print(datetime.now(),'数据库链接失败',e)
    return connection

# 确保在程序退出时关闭数据库连接
def close_connection():
    if connection and connection.open:
        print(datetime.now(),'关闭SQL连接')
        cursor.close()
        connection.close()
        
connection = create_connection()
cursor = connection.cursor()

def getConnection():
    return connection

atexit.register(close_connection)

# 通过城市名称查询城市信息
def queryCityInfo(cityName):
    query = f'''
    (SELECT 
        a.areaid,
        a.area,
        c.cityid,
        c.city,
        p.provinceid,
        p.province
    FROM 
        unvbasicx_khgz.areas a
    JOIN 
        unvbasicx_khgz.cities c ON a.cityid = c.cityid
    JOIN 
        unvbasicx_khgz.provinces p ON c.provinceid = p.provinceid
    WHERE 
        a.area like '%{cityName}%')
    UNION ALL
    (SELECT 
        '' AS areaid,
        '' AS area,
        c.cityid,
        c.city,
        p.provinceid,
        p.province
    FROM 
        unvbasicx_khgz.cities c
    JOIN 
        unvbasicx_khgz.provinces p ON c.provinceid = p.provinceid
    WHERE 
        c.city like '%{cityName}%'
        AND NOT EXISTS (
            SELECT 1 FROM unvbasicx_khgz.areas WHERE area like '%{cityName}%'
        )
    )
    UNION ALL
    (SELECT 
        '' AS areaid,
        '' AS area,
        '' AS cityid,
        '' AS city,
        p.provinceid,
        p.province
    FROM 
        unvbasicx_khgz.provinces p
    WHERE 
        p.province like '%{cityName}%'
        AND NOT EXISTS (
            SELECT 1 FROM unvbasicx_khgz.cities WHERE city like '%{cityName}%'
        )
        AND NOT EXISTS (
            SELECT 1 FROM unvbasicx_khgz.areas WHERE area like '%{cityName}%'
        )
    )
    LIMIT 1
    '''
    if connection == None:
        create_connection()
    try:
        connection.ping(reconnect=True)
        cursor.execute(query)
        result = cursor.fetchall()  # 获取所有查询结果
        return result
    except Exception as e:
        print(datetime.now(),'通过城市名查询城市信息异常',e)
        traceback.print_exc()



# 通过城市名称查询城市信息
def queryCityInfoByAreaId(cityCode):
    query = f'''
    SELECT 
        a.areaid,
        a.area,
        c.cityid,
        c.city,
        p.provinceid,
        p.province
    FROM 
        unvbasicx_khgz.areas a
    JOIN 
        unvbasicx_khgz.cities c ON a.cityid = c.cityid
    JOIN 
        unvbasicx_khgz.provinces p ON c.provinceid = p.provinceid
    WHERE 
        a.areaid like '%{cityCode}%'
    
    LIMIT 1
    '''
    if connection == None:
        create_connection()
    try:
        # 先检查是否端口,断开就重连
        connection.ping(reconnect=True)
        cursor.execute(query)
        result = cursor.fetchall()  # 获取所有查询结果
        return result
    # except pymysql.OperationalError:
    #     connection = create_connection()
    #     cursor = connection.cursor()
    #     cursor.execute(query)
    #     result = cursor.fetchall()  # 获取所有查询结果
    #     return result
    except Exception as e:
        print(datetime.now(),'通过城市code查询城市信息异常',e)
        traceback.print_exc()

# 通过城市名称查询城市信息
def queryProvinceId(provinceName):
    query = f'''
    SELECT 
        p.provinceid
    FROM 
        unvbasicx_khgz.provinces p
    WHERE 
        p.province like '%{provinceName}%'
    
    LIMIT 1
    '''
    if connection == None:
        create_connection()
    try:
        # 先检查是否端口,断开就重连
        connection.ping(reconnect=True)
        cursor.execute(query)
        result = cursor.fetchone()  # 获取所有查询结果
        return result
    # except pymysql.OperationalError:
    #     connection = create_connection()
    #     cursor = connection.cursor()
    #     cursor.execute(query)
    #     result = cursor.fetchall()  # 获取所有查询结果
    #     return result
    except Exception as e:
        print(datetime.now(),'通过城市code查询城市信息异常',e)
        traceback.print_exc()

# 通过城市名称查询城市信息
def queryCityInProvince(cityName,provinceId):
    # 构建provinceId的条件判断
    province_filter = f"AND p.provinceid = '{provinceId}'" if provinceId else ""


    query = f'''
    (SELECT 
        a.areaid,
        a.area,
        c.cityid,
        c.city,
        p.provinceid,
        p.province
    FROM 
        unvbasicx_khgz.areas a
    JOIN 
        unvbasicx_khgz.cities c ON a.cityid = c.cityid
    JOIN 
        unvbasicx_khgz.provinces p ON c.provinceid = p.provinceid
    WHERE 
        a.area like '%{cityName}%'
        {province_filter}
    )
    UNION ALL
    (SELECT 
        '' AS areaid,
        '' AS area,
        c.cityid,
        c.city,
        p.provinceid,
        p.province
    FROM 
        unvbasicx_khgz.cities c
    JOIN 
        unvbasicx_khgz.provinces p ON c.provinceid = p.provinceid
    WHERE 
        c.city like '%{cityName}%'
        {province_filter}
    )
    UNION ALL
    (SELECT 
        '' AS areaid,
        '' AS area,
        '' AS cityid,
        '' AS city,
        p.provinceid,
        p.province
    FROM 
        unvbasicx_khgz.provinces p
    WHERE 
        p.province like '%{cityName}%'
        {province_filter}
    )
    '''
    if connection == None:
        create_connection()
    try:
        connection.ping(reconnect=True)
        cursor.execute(query)
        result = cursor.fetchall()  # 获取所有查询结果
        return result
    except Exception as e:
        print(datetime.now(),'通过城市名查询城市信息异常',e)
        traceback.print_exc()

def queryCityInfoTotal(provinceName,cityName,areaName,noteInfo):
    global connection
    # 这个方法是通过省市地的名称精确获取城市信息
    # 其中provinceName不会为空，但cityName和areaName可以为空
    # 当cityName不为空时，要根据cityName和provinceName获取城市信息
    # 当areaName不为空时，要根据areaName+cityName+provinceName获取。
    # 例如（江苏，南京，''）时，就要获取江苏省-南京市
    # （江苏，南京，鼓楼区）时，就要获取江苏-南京-鼓楼区
    # 但是实际可能会出现省市地不符合的情况，比如（江苏，杭州，慈溪），这种情况就要以江苏为准，市和区都是空
    # 另外noteInfo中可能会指定provinceId，也可能指定provincId+cityId。实际查询以noteInfo的优先为准
    
    # 解析 noteInfo（优先使用ID查询）
    province_id = None
    city_id = None
    if noteInfo:
        try:
            parsed = noteInfo
            if isinstance(noteInfo, str) and noteInfo.strip().startswith('{'):
                parsed = json.loads(noteInfo)
            if isinstance(parsed, dict):
                province_id = parsed.get('provinceId') or parsed.get('province_id')
                city_id = parsed.get('cityId') or parsed.get('city_id')
        except Exception:
            pass

    # 确保数据库连接
    if connection == None:
        create_connection()

    try:
        with connection.cursor() as cursor:
            # 1) noteInfo 同时提供 provinceId + cityId
            if province_id and city_id:
                if areaName:
                    sql = f'''
                    SELECT 
                        a.areaid,
                        a.area,
                        c.cityid,
                        c.city,
                        p.provinceid,
                        p.province
                    FROM unvbasicx_khgz.provinces p
                    JOIN unvbasicx_khgz.cities c ON c.provinceid = p.provinceid AND c.cityid = '{city_id}'
                    LEFT JOIN unvbasicx_khgz.areas a ON a.cityid = c.cityid AND a.area LIKE '%{areaName}%'
                    WHERE p.provinceid = '{province_id}'
                    LIMIT 1
                    '''
                    cursor.execute(sql)
                    row = cursor.fetchone()
                    if row and row[0]:
                        return { 'areaid': row[0], 'area': row[1], 'cityid': row[2], 'city': row[3], 'provinceid': row[4], 'province': row[5] }
                    # area 未命中，返回 省+市，区为空
                    sql = f'''
                    SELECT 
                        '' AS areaid,
                        '' AS area,
                        c.cityid,
                        c.city,
                        p.provinceid,
                        p.province
                    FROM unvbasicx_khgz.provinces p
                    JOIN unvbasicx_khgz.cities c ON c.provinceid = p.provinceid AND c.cityid = '{city_id}'
                    WHERE p.provinceid = '{province_id}'
                    LIMIT 1
                    '''
                    cursor.execute(sql)
                    row = cursor.fetchone()
                    if row:
                        return { 'areaid': row[0], 'area': row[1], 'cityid': row[2], 'city': row[3], 'provinceid': row[4], 'province': row[5] }
                else:
                    # 仅返回省+市
                    sql = f'''
                    SELECT 
                        '' AS areaid,
                        '' AS area,
                        c.cityid,
                        c.city,
                        p.provinceid,
                        p.province
                    FROM unvbasicx_khgz.provinces p
                    JOIN unvbasicx_khgz.cities c ON c.provinceid = p.provinceid AND c.cityid = '{city_id}'
                    WHERE p.provinceid = '{province_id}'
                    LIMIT 1
                    '''
                    cursor.execute(sql)
                    row = cursor.fetchone()
                    if row:
                        return { 'areaid': row[0], 'area': row[1], 'cityid': row[2], 'city': row[3], 'provinceid': row[4], 'province': row[5] }

            # 2) noteInfo 仅提供 provinceId
            if province_id and not city_id:
                if cityName:
                    # 先找该省下的城市
                    sql = f'''
                    SELECT 
                        c.cityid, c.city, p.provinceid, p.province
                    FROM unvbasicx_khgz.provinces p
                    JOIN unvbasicx_khgz.cities c ON c.provinceid = p.provinceid
                    WHERE p.provinceid = '{province_id}' AND c.city LIKE '%{cityName}%'
                    LIMIT 1
                    '''
                    cursor.execute(sql)
                    city_row = cursor.fetchone()
                    if city_row:
                        cid, cname, pid, pname = city_row
                        if areaName:
                            sql = f'''
                            SELECT 
                                a.areaid,
                                a.area,
                                c.cityid,
                                c.city,
                                p.provinceid,
                                p.province
                            FROM unvbasicx_khgz.provinces p
                            JOIN unvbasicx_khgz.cities c ON c.provinceid = p.provinceid AND c.cityid = '{cid}'
                            JOIN unvbasicx_khgz.areas a ON a.cityid = c.cityid AND a.area LIKE '%{areaName}%'
                            WHERE p.provinceid = '{province_id}'
                            LIMIT 1
                            '''
                            cursor.execute(sql)
                            row = cursor.fetchone()
                            if row:
                                return { 'areaid': row[0], 'area': row[1], 'cityid': row[2], 'city': row[3], 'provinceid': row[4], 'province': row[5] }
                        # area 不存在，返回省+市
                        return { 'areaid': '', 'area': '', 'cityid': cid, 'city': cname, 'provinceid': pid, 'province': pname }
                    # 市不属于该省，返回省
                    sql = f"""
                    SELECT '' AS areaid, '' AS area, '' AS cityid, '' AS city, p.provinceid, p.province
                    FROM unvbasicx_khgz.provinces p WHERE p.provinceid = '{province_id}' LIMIT 1
                    """
                    cursor.execute(sql)
                    row = cursor.fetchone()
                    if row:
                        return { 'areaid': row[0], 'area': row[1], 'cityid': row[2], 'city': row[3], 'provinceid': row[4], 'province': row[5] }
                else:
                    # 仅省
                    sql = f"""
                    SELECT '' AS areaid, '' AS area, '' AS cityid, '' AS city, p.provinceid, p.province
                    FROM unvbasicx_khgz.provinces p WHERE p.provinceid = '{province_id}' LIMIT 1
                    """
                    cursor.execute(sql)
                    row = cursor.fetchone()
                    if row:
                        return { 'areaid': row[0], 'area': row[1], 'cityid': row[2], 'city': row[3], 'provinceid': row[4], 'province': row[5] }

            # 3) 无 noteInfo，按名称精确匹配并带容错
            if areaName and cityName and provinceName:
                # 省-市-区 全量
                sql = f'''
                SELECT 
                    a.areaid,
                    a.area,
                    c.cityid,
                    c.city,
                    p.provinceid,
                    p.province
                FROM unvbasicx_khgz.areas a
                JOIN unvbasicx_khgz.cities c ON a.cityid = c.cityid
                JOIN unvbasicx_khgz.provinces p ON c.provinceid = p.provinceid
                WHERE p.province LIKE '%{provinceName}%' AND c.city LIKE '%{cityName}%' AND a.area LIKE '%{areaName}%'
                LIMIT 1
                '''
                cursor.execute(sql)
                row = cursor.fetchone()
                if row:
                    return { 'areaid': row[0], 'area': row[1], 'cityid': row[2], 'city': row[3], 'provinceid': row[4], 'province': row[5] }
                # 尝试仅省-市
                sql = f'''
                SELECT 
                    '' AS areaid,
                    '' AS area,
                    c.cityid,
                    c.city,
                    p.provinceid,
                    p.province
                FROM unvbasicx_khgz.cities c
                JOIN unvbasicx_khgz.provinces p ON c.provinceid = p.provinceid
                WHERE p.province LIKE '%{provinceName}%' AND c.city LIKE '%{cityName}%'
                LIMIT 1
                '''
                cursor.execute(sql)
                row = cursor.fetchone()
                if row:
                    return { 'areaid': row[0], 'area': row[1], 'cityid': row[2], 'city': row[3], 'provinceid': row[4], 'province': row[5] }
                # 省-市不匹配，返回省
                sql = f"""
                SELECT '' AS areaid, '' AS area, '' AS cityid, '' AS city, p.provinceid, p.province
                FROM unvbasicx_khgz.provinces p WHERE p.province LIKE '%{provinceName}%' LIMIT 1
                """
                cursor.execute(sql)
                row = cursor.fetchone()
                if row:
                    return { 'areaid': row[0], 'area': row[1], 'cityid': row[2], 'city': row[3], 'provinceid': row[4], 'province': row[5] }

            if cityName and provinceName:
                # 省-市
                sql = f'''
                SELECT 
                    '' AS areaid,
                    '' AS area,
                    c.cityid,
                    c.city,
                    p.provinceid,
                    p.province
                FROM unvbasicx_khgz.cities c
                JOIN unvbasicx_khgz.provinces p ON c.provinceid = p.provinceid
                WHERE p.province LIKE '%{provinceName}%' AND c.city LIKE '%{cityName}%'
                LIMIT 1
                '''
                cursor.execute(sql)
                row = cursor.fetchone()
                if row:
                    return { 'areaid': row[0], 'area': row[1], 'cityid': row[2], 'city': row[3], 'provinceid': row[4], 'province': row[5] }
                # 不匹配，返回省
                sql = f"""
                SELECT '' AS areaid, '' AS area, '' AS cityid, '' AS city, p.provinceid, p.province
                FROM unvbasicx_khgz.provinces p WHERE p.province LIKE '%{provinceName}%' LIMIT 1
                """
                cursor.execute(sql)
                row = cursor.fetchone()
                if row:
                    return { 'areaid': row[0], 'area': row[1], 'cityid': row[2], 'city': row[3], 'provinceid': row[4], 'province': row[5] }

            # 仅省
            if provinceName:
                sql = f"""
                SELECT '' AS areaid, '' AS area, '' AS cityid, '' AS city, p.provinceid, p.province
                FROM unvbasicx_khgz.provinces p WHERE p.province LIKE '%{provinceName}%' LIMIT 1
                """
                cursor.execute(sql)
                row = cursor.fetchone()
                if row:
                    return { 'areaid': row[0], 'area': row[1], 'cityid': row[2], 'city': row[3], 'provinceid': row[4], 'province': row[5] }

            return None
    except Exception as e:
        print(datetime.now(),'通过城市名查询城市信息异常',e)
        traceback.print_exc()
        return None



# 设定main函数,程序起点
if __name__ == '__main__':
    try:
    #    noteInfo = testMatch('电话：ABC公司')
        pStr = 'zho'
        # text = re.sub('\s+','',pStr.replace(u'\xa0','').strip().replace('\n','').replace(':','：'))
        # print('======text:',text)
        # a = remove_space(text)
        # print(a)
        # a = getProvinceId(pStr)
        # data = json.loads(a.replace('```','').replace('json','').replace(' ',''))
        # print(data['provinceId'])
        noteInfo = {
        }
        a = queryCityInfoTotal('河北','雄安','无极县',noteInfo)
        # a = queryCityInfoByArea('江山')
        print(a)
    #    a = ' 1.2852万元。收取对象：中标（成交）供应商。2.采购预算总金额：1,000,000.00元，最高限价：978,000.00元。地址：中国(四川)自由贸易试验区成都高新区益州大道中段722号3栋1单元603号中标（成交）金额：952,000.00元金额(元)：952,000.00'
    #    amount = getAmount(a[:1000])
    #    print('noteInfo',amount)

    except Exception as err:
        print(f'任务执行失败',err)
        traceback.print_exc()
        