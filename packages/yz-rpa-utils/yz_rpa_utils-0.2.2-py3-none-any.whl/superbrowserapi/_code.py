import time
import os
import random
import uuid
import json
import requests
import subprocess
import psutil
import xml.etree.ElementTree as ET
import shutil
from time import sleep
import hashlib, traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .utils import terminate_processes_by_names
from tenacity import (
    retry,
    retry_if_result,
    stop_after_attempt,
    wait_fixed
)
import subprocess


def encrypt_sha1(fpath: str) -> str:
    with open(fpath, 'rb') as f:
        return hashlib.new('sha1', f.read()).hexdigest()


def download_file(url, save_path):
    # 发送GET请求获取文件内容
    response = requests.get(url, stream=True)
    # 检查请求是否成功
    if response.status_code == 200:
        # 创建一个本地文件并写入下载的内容（如果文件已存在，将被覆盖）
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"文件已成功下载并保存到：{save_path}")
    else:
        print(f"下载失败，响应状态码为：{response.status_code}")


class SuperBrowserAPI:

    def __init__(self, company, username, password, _print=print, xbot=None):
        self.current_cef = "superbrowser"
        self.main_browser_running = False
        self.exe_path = self.get_super_browser_exe_path()
        self.print = _print
        # 获取当前运行路径
        self.driver_folder_path = os.path.join(os.getcwd(), "ziniao_driver")
        self.download_driver(self.driver_folder_path)
        assert company and username and password, "登录信息都是必选,请检查"
        self.user_info = {"company": company, "username": username, "password": password}
        self.socket_port = None
        # 初始化一个端口
        self.web_driver = None
        self.xbot = xbot

    def get_driver(self, open_ret_json):
        core_type = open_ret_json.get('core_type')
        if core_type == 'Chromium' or core_type == 0:
            major = open_ret_json.get('core_version').split('.')[0]
            chrome_driver_path = os.path.join(self.driver_folder_path, 'chromedriver%s.exe') % major
            self.print(f"chrome_driver_path: {chrome_driver_path}")
            port = open_ret_json.get('debuggingPort')
            options = webdriver.ChromeOptions()
            options.add_experimental_option("debuggerAddress", '127.0.0.1:' + str(port))
            return webdriver.Chrome(service=Service(chrome_driver_path), options=options)
        else:
            return None

    def get_cef(self):
        return self.current_cef

    def download_driver(self, driver_folder_path):
        config_url = "https://cdn-superbrowser-attachment.ziniao.com/webdriver/exe_32/config.json"
        response = requests.get(config_url)
        # 检查请求是否成功
        if response.status_code == 200:
            # 获取文本内容
            txt_content = response.text
            config = json.loads(txt_content)
        else:
            self.print(f"下载驱动失败，状态码：{response.status_code}")
            exit()
        if not os.path.exists(driver_folder_path):
            os.makedirs(driver_folder_path)

        # 获取文件夹中所有chromedriver文件
        driver_list = [filename for filename in os.listdir(driver_folder_path) if filename.startswith('chromedriver')]

        for item in config:
            filename = item['name']
            filename = filename + ".exe"
            local_file_path = os.path.join(driver_folder_path, filename)
            if filename in driver_list:
                # 判断sha1是否一致
                file_sha1 = encrypt_sha1(str(local_file_path))
                if file_sha1 == item['sha1']:
                    self.print(f"驱动{filename}已存在，sha1校验通过...")
                else:
                    self.print(f"驱动{filename}的sha1不一致，重新下载...")
                    download_file(item['url'], local_file_path)
            else:
                self.print(f"驱动{filename}不存在，开始下载...")
                download_file(item['url'], local_file_path)

    def get_super_browser_exe_path(self):
        """获取紫鸟浏览器启动文件路径"""
        config_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'ShadowBot', 'ChromiumBrowser.config')

        if not os.path.exists(config_path):
            raise Exception("未安装紫鸟浏览器插件，请在影刀中安装插件")

        # 解析XML文件
        tree = ET.parse(config_path)
        root = tree.getroot()
        # 提取ProcessName和ExePath
        matching_nodes = root.findall(".//ChromiumBrowserInfo")
        if len(matching_nodes) == 0:
            raise Exception("未安装紫鸟浏览器插件，请在影刀中安装插件")
        node = matching_nodes[0]
        product_name, process_name, exe_path = node.find('ProductName').text, node.find('ProcessName').text, node.find('ExePath').text
        assert product_name in ["superbrowser", "ziniaobrowser"] and process_name in ["superbrowser", "ziniaobrowser"], "紫鸟浏览器插件未正确安装，请检查"
        self.current_cef = process_name
        assert os.path.exists(exe_path), "紫鸟浏览器未正确安装"
        return exe_path

    def get_port(self):
        procarr = []
        for conn in psutil.net_connections():
            if conn.raddr and conn.status == 'LISTEN':
                procarr.append(conn.laddr.port)
        # 判断当前端口是否占用,如果占用刷新端口
        if not self.socket_port or self.socket_port in procarr:
            tt = random.randint(15000, 20000)
            if tt not in procarr:
                return tt
            else:
                return self.get_port()
        else:
            return self.socket_port

    def start_exe_browser(self):
        """
        启动紫鸟客户端
        :return:
        """
        self.kill_all_super_browser()
        self.kill_all_store_process()
        # 尝试启动3次
        try_max_count = 0
        while try_max_count < 3 and not self.main_browser_running:
            try:
                self.socket_port = self.get_port()
                cmd_text = [self.exe_path, '--run_type=web_driver', '--ipc_type=http', '--port=' + str(self.socket_port)]
                self.print(" ".join(cmd_text))
                subprocess.Popen(cmd_text)
                self.print("start ..")
                time.sleep(3)
                # 更新内核
                self.update_core()
                # 如果执行没报错就是启动成功
                self.main_browser_running = True
            except Exception as e:
                self.print("start_ExeBrowser err...", e)
            finally:
                try_max_count += 1
        if not self.main_browser_running:
            raise Exception("启动紫鸟控制台失败")
        return self.main_browser_running

    @retry(
        stop=stop_after_attempt(10),  # 最大重试次数
        wait=wait_fixed(1),  # 每次重试间隔10秒
        reraise=True
    )
    def send_http(self, data):
        """
        通讯方式
        :param data:
        :return:
        """
        try:
            url = 'http://127.0.0.1:{}'.format(self.socket_port)
            # response = requests.post(url, json.dumps(data).encode('utf-8'), timeout=120)
            response = requests.post(url, json=data, timeout=120)
            r = json.loads(response.text)
            status_code = str(r.get("statusCode"))
            if status_code == "0":
                return r
            elif status_code == "-10003":
                raise Exception(json.dumps(r, ensure_ascii=False))
            else:
                return r
        except Exception as err:
            raise err

    def update_core(self):
        """
        下载所有内核，打开店铺前调用，需客户端版本5.285.7以上
        因为http有超时时间，所以这个action适合循环调用，直到返回成功
        """
        data = {
            "action": "updateCore",
            "requestId": str(uuid.uuid4()),
        }
        data.update(self.user_info)
        while True:
            result = self.send_http(data)
            self.print(result)
            if result is None:
                self.print("等待客户端启动...")
                time.sleep(2)
                continue
            if result.get("statusCode") is None or result.get("statusCode") == -10003:
                self.print("当前版本不支持此接口，请升级客户端")
                return
            elif result.get("statusCode") == 0:
                self.print("更新内核完成")
                return
            else:
                self.print(f"等待更新内核: {json.dumps(result)}")
                time.sleep(2)

    def get_running_info(self):
        """
        下载所有内核，打开店铺前调用，需客户端版本5.285.7以上
        因为http有超时时间，所以这个action适合循环调用，直到返回成功
        """
        data = {
            "action": "getRunningInfo",
            "requestId": str(uuid.uuid4()),
        }
        data.update(self.user_info)
        result = self.send_http(data)
        return result.get("browsers")

    def open_store(self, store_info,
                   close_other_store=True,
                   isWebDriverReadOnlyMode=0,
                   isprivacy=0,
                   cookieTypeLoad=0,
                   cookieTypeSave=0,
                   isHeadless=False,
                   jsInfo="",
                   pluginIdList="16312716772451"):
        # 关闭其他店铺
        if close_other_store:
            self.kill_all_store_process()
        """
        打开店铺
        """
        # 控制下载目录
        download_shop_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'Super Browser', store_info)
        # 如果目录存在则删除（包括所有内容）
        if os.path.exists(download_shop_path):
            shutil.rmtree(download_shop_path)  # 递归删除整个目录
        # 创建目录（包括所有必要的中间目录）
        os.makedirs(download_shop_path, exist_ok=True)
        self.print(f"目录 {download_shop_path} 已成功重置")

        requestId = str(uuid.uuid4())
        data = {
            "action": "startBrowser",
            "internalPluginList": "SBShopReport.zip,SBRPAEditor.zip,SBMessage.zip,SBCRM.zip,SBEcology.zip,SBHelp.zip,SBPassword.zip,SBRPA.zip,SBSems.zip,SBSetting.zip,SBShop.zip",
            "isWaitPluginUpdate": True,
            "isHeadless": isHeadless,
            "requestId": requestId,
            "isWebDriverReadOnlyMode": isWebDriverReadOnlyMode,
            "cookieTypeLoad": cookieTypeLoad,
            "cookieTypeSave": cookieTypeSave,
            "runMode": "2",
            "isLoadUserPlugin": False,
            "notPromptForDownload": 0,
            "pluginIdType": 1,
            "pluginIdList": pluginIdList,
            "privacyMode": isprivacy,
            "forceDownloadPath": download_shop_path,
        }
        data.update(self.user_info)

        data["browserId"] = store_info

        if len(str(jsInfo)) > 2:
            data["injectJsInfo"] = json.dumps(jsInfo)
        res_result = self.send_http(data)

        self.web_driver = self.get_driver(res_result)
        if not self.web_driver:
            raise Exception("启动失败,driver获取失败")
        # 隐式等待 5s
        self.web_driver.implicitly_wait(5)

        # 优化IP
        self.optimization_ip(res_result.get('ipDetectionPage'))
        # 创建并返回
        return res_result, self.get_web_page("https://www.baidu.com/", timeout=60) if self.xbot else None

    def get_web_page(self, url, timeout=60):
        """
        进入主页，如果插件加载失败则重试
        """
        start_time = time.time()
        while True:
            try:
                web_page = self.xbot.web.create(url, mode=self.get_cef(), load_timeout=0)
                try:
                    web_page.wait_load_completed(10)
                except:
                    pass
                return web_page
            except Exception as e:
                if '等待页面加载超时' in str(e):
                    web_page = self.xbot.web.get(url=f"{url}", mode=self.get_cef(), load_timeout=0, use_wildcard=True)
                    return web_page
                if time.time() - start_time < timeout:
                    sleep(2)
                else:
                    raise e

    def find_element_by_xpath(self, xpath):
        try:
            return self.web_driver.find_element(By.XPATH, xpath)
        except Exception as e:
            self.print(f"找不到元素 {xpath}")
            return None

    def optimization_ip(self, ip_detection_page: str):
        """
        打开ip检测页检测ip是否正常
        :param ip_detection_page:
        :return 检测结果
        """
        # 先进入紫鸟官方插件,可自动优化IP
        self.web_driver.get(ip_detection_page)
        next_button = self.find_element_by_xpath('//span[contains(text(),"继续访问")]/..')
        if next_button:
            next_button.click()
        try:
            next_button = WebDriverWait(self.web_driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="打开账号"]/..'))
            )
        except Exception as ex:
            self.print("等待打开店铺按钮异常:" + traceback.format_exc())
        self.print("检测IP完毕")

    def close_store(self, ziniao_shop_id):
        request_id = str(uuid.uuid4())
        data = {
            "action": "stopBrowser"
            , "requestId": request_id
            , "duplicate": 0
            , "browserOauth": ziniao_shop_id
        }
        data.update(self.user_info)

        r = self.send_http(data)
        if str(r.get("statusCode")) == "0":
            return r
        elif str(r.get("statusCode")) == "-10003":
            self.print(f"login Err {json.dumps(r, ensure_ascii=False)}")
        else:
            self.print(f"Fail {json.dumps(r, ensure_ascii=False)} ")

    def get_browser_list(self):
        requestId = str(uuid.uuid4())
        data = {
            "action": "getBrowserList",
            "requestId": requestId
        }
        data.update(self.user_info)

        r = self.send_http(data)
        return r.get("browserList")

    def get_store_name_list(self):
        browser_list = self.get_browser_list()
        store_name_list = []
        for item in browser_list:
            store_name_list.append(item.get("browserName"))
        return store_name_list

    def delete_all_cache(self):
        """
        删除所有店铺缓存
        非必要的，如果店铺特别多、硬盘空间不够了才要删除
        """
        # self.kill_all_store_process()
        # self.kill_all_super_browser()
        # local_appdata = os.getenv('LOCALAPPDATA')
        # cache_path = os.path.join(local_appdata, 'SuperBrowser')
        # if os.path.exists(cache_path):
        #     try:
        #         shutil.rmtree(cache_path)
        #     except Exception as ex:
        #         pass
        pass

    @staticmethod
    def kill_all_store_process():
        terminate_processes_by_names(["superbrowser", "chromedriver", "ziniaobrowser"])

    @staticmethod
    def kill_all_super_browser():
        terminate_processes_by_names(["SuperBrowser", "ziniao", "chromedriver"])

    def get_exit(self):
        """
        关闭客户端
        :return:
        """
        data = {"action": "exit", "requestId": str(uuid.uuid4())}
        data.update(self.user_info)
        self.print('@@ get_exit...' + json.dumps(self.send_http(data)))
        self.main_browser_running = False
        self.kill_all_store_process()
        self.kill_all_super_browser()


def go_home(url, timeout=20):
    pass


def main(args):
    pass
