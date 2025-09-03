from selenium import webdriver
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC  
import zipfile
import string
import time
from datetime import datetime
import noteparse.proxyHelper as proxy
import traceback
from fake_useragent import UserAgent
from noteparse.configReader import readConfig


proxyConf = readConfig('minute_url','minute_user','minute_pwd','daily_url','daily_user','daily_pwd',section='proxyConfig')

# 带账密的代理selenium
def create_proxy_auth_extension(proxy_host, proxy_port, proxy_username, proxy_password, scheme='http',
                                plugin_path=None):
    if plugin_path is None:
        plugin_path = r'{}_{}@http-dyn.dobel.com_9020.zip'.format(proxy_username, proxy_password)

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Dobel Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = string.Template(
        """
        var config = {
            mode: "fixed_servers",
            rules: {
                singleProxy: {
                    scheme: "${scheme}",
                    host: "${host}",
                    port: parseInt(${port})
                },
                bypassList: ["foobar.com"]
            }
          };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "${username}",
                    password: "${password}"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
        );
        """
    ).substitute(
        host=proxy_host,
        port=proxy_port,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )

    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return plugin_path


def from_proxy_get_daili(proxy):
    # proxy是这种格式 user:pass@ip:port
    user_pass_str, ip_port_str = proxy.split('@')
    proxyHost, proxyPort = ip_port_str.split(':')
    proxyUser, proxyPass = user_pass_str.split(':')
    return proxyHost, proxyPort, proxyUser, proxyPass

def getDriver(proxyInfo):
    proxyHost, proxyPort, proxyUser, proxyPass = from_proxy_get_daili(proxyInfo)
    proxy_auth_plugin_path = create_proxy_auth_extension(
        proxy_host=proxyHost,
        proxy_port=proxyPort,
        proxy_username=proxyUser,
        proxy_password=proxyPass)
    option = webdriver.ChromeOptions()
    option.add_argument('--headless=new') #静默模式,不打开浏览器
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-dev-shm-usage')
    option.add_argument('--disable-gpu')
    option.add_argument('log-level=3')
    option.add_extension(proxy_auth_plugin_path)
    # current_location = os.path.dirname(__file__)
    # path = os.path.join(current_location,"BidFile")
    # prefs = { 'profile.default_content_settings.popups': 0, 'download.default_directory': path}
    # option.add_experimental_option( 'prefs', prefs)
    # proxyInfo = proxy.get_daily_ip()
    # proxyIp = "http://imdlxin:imdlxin@"+str(proxyInfo['ip'])+":"+str(proxyInfo['port'])
    # print('--daili--:',proxyIp)
    # option.add_argument(f'--proxy-server={proxyIp}')
    # 放弃样式\图像\子帧
    driver = webdriver.Chrome(options=option)
    return driver

def get_driver():
    proxyInfo = proxy.get_daily_ip()
    ip = proxyInfo['ip']
    port = proxyInfo['port']
    proxys = f"{proxyConf['daily_user']}:{proxyConf['daily_pwd']}@{ip}:{port}"
    driver = getDriver(proxys)
    return driver

def getCookie():
    print(datetime.now(),'==========开始获取cookie======')
    try:
        proxyInfo = proxy.get_daily_ip()
        ip = proxyInfo['ip']
        port = proxyInfo['port']
        proxys = f"{proxyConf['daily_user']}:{proxyConf['daily_pwd']}@{ip}:{port}"
        driver = getDriver(proxys)
        # 打开登录页
        loginUrl = 'http://qiye.qianlima.com/yfbsite/a/login'
        driver.get(loginUrl)
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="loginTypeForm"]'))
        )
        pwdLoginBtn = driver.find_element(By.XPATH,'//*[@id="accountLogin"]/i')
        pwdLoginBtn.click()
        time.sleep(2)
        userInput = driver.find_element(By.XPATH,'//*[@id="username"]')
        pwdInput = driver.find_element(By.XPATH,'//*[@id="password"]')
        # userInput.send_keys(username)
        # pwdInput.send_keys(username)
        # 等待登录
        # isLogin = False
        # while not isLogin:
        #     try:
        #         qrCode = driver.find_element(By.ID, 'qrcode')
        #         if qrCode:
        #             print(datetime.now(),"未登录")
        #             time.sleep(2)
        #         else:
        #             isLogin = True
        #     except Exception:
        #         isLogin = True

        print(datetime.now(),'登录完成!')

        jessionId = driver.get_cookie('yfbSite.session.id')
        cookie = jessionId.get('value')
        # header['Cookie'] = f'yfbSite.session.id={cookie}'
        print(datetime.now(),'jessionid',cookie)
    except Exception as get_cookie_err:
        print(datetime.now(),'获取cookie失败',get_cookie_err)
        traceback.print_exc()