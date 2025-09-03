# -*- coding:utf-8 -*-
import os
import platform
import getpass
from selenium import webdriver as selenium_webdriver
try:
    from seleniumwire import webdriver as wire_webdriver
except ImportError:
    wire_webdriver = None
from selenium.webdriver.chrome.service import Service
import re
import socket
import tempfile
import shutil
import uuid
import subprocess

dir_path = os.path.expanduser("~")


class GetDriverException(Exception):
    """自定义异常：GetDriver相关错误"""
    pass


class GetDriver:
    """
    Selenium ChromeDriver 管理器，支持多平台、代理、无头模式、下载目录、User-Agent等高级配置。
    支持上下文管理器（with语法），自动资源清理。
    """
    def __init__(self, url=None, headless=False, proxy=None, user_agent=None, download_dir=None, chrome_path=None, chromedriver_path=None, maximize_window=True, is_selenium_wire=False):
        """
        初始化GetDriver
        :param url: 允许的安全站点（用于insecure origin as secure）
        :param headless: 是否无头模式
        :param proxy: 代理（支持http、https、socks5，格式如socks5://127.0.0.1:1080）
        :param user_agent: 自定义User-Agent
        :param download_dir: 下载目录
        :param chrome_path: Chrome浏览器路径
        :param chromedriver_path: Chromedriver路径
        """
        self.url = url
        self.headless = headless
        self.proxy = proxy
        self.user_agent = user_agent
        self.download_dir = os.path.expanduser(download_dir) if download_dir else os.path.expanduser('~/Downloads')
        self.chrome_path = chrome_path
        self.chromedriver_path = chromedriver_path
        self.temp_dirs = []  # 存储临时目录路径，用于清理
        self.driver = None
        if not self.user_agent:
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            ]
            import random
            self.user_agent = user_agents[random.randint(0, len(user_agents) - 1)]
        self.maximize_window = maximize_window
        self.is_selenium_wire = is_selenium_wire

    def check_proxy(self):
        """
        校验代理格式和连通性，支持http/https/socks5
        :return: True/False
        """
        if not self.proxy:
            return True
        # 支持协议前缀
        proxy_pattern = r'^(socks5|http|https)://(\d{1,3}(\.\d{1,3}){3}):(\d+)$'
        if not re.match(proxy_pattern, self.proxy):
            return False
        proto, ip, _, _, port = re.match(proxy_pattern, self.proxy).groups()
        try:
            sock = socket.create_connection((ip, int(port)), timeout=5)
            sock.close()
            return True
        except:
            return False

    def _get_chrome_version(self, chrome_path):
        """
        获取Chrome版本号
        :param chrome_path: Chrome可执行文件路径
        :return: 版本号字符串，如"120.0.6099.109"
        """
        try:
            if platform.system().lower() == 'windows':
                # 方法1: 尝试从注册表获取版本
                try:
                    import winreg
                    key_path = r"SOFTWARE\Google\Chrome\BLBeacon"
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                        version = winreg.QueryValueEx(key, "version")[0]
                        return version
                except:
                    pass
                # 方法2: 尝试从文件属性获取版本
                try:
                    result = subprocess.run(['wmic', 'datafile', 'where', f'name="{chrome_path.replace("/", "\\")}"', 'get', 'version', '/value'], 
                                          capture_output=True, text=True, timeout=10, shell=True)
                    if result.returncode == 0:
                        version_match = re.search(r'Version=(\d+\.\d+\.\d+\.\d+)', result.stdout)
                        if version_match:
                            return version_match.group(1)
                except:
                    pass
            else:
                # macOS和Linux下使用--version参数
                result = subprocess.run([chrome_path, '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    # 输出格式: "Google Chrome 120.0.6099.109"
                    version_match = re.search(r'Chrome\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
                    if version_match:
                        return version_match.group(1)
        except Exception as e:
            pass
            # print(f"获取Chrome版本失败: {e}")
        return None

    def _get_chromedriver_version(self, chromedriver_path):
        """
        获取Chromedriver版本号
        :param chromedriver_path: Chromedriver可执行文件路径
        :return: 版本号字符串，如"120.0.6099.109"
        """
        try:
            if platform.system().lower() == 'windows':
                # Windows下使用shell=True确保参数正确传递
                result = subprocess.run([chromedriver_path, '--version'], 
                                      capture_output=True, text=True, timeout=10, shell=True)
            else:
                result = subprocess.run([chromedriver_path, '--version'], 
                                      capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # 输出格式: "ChromeDriver 120.0.6099.109"
                version_match = re.search(r'ChromeDriver\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
                if version_match:
                    return version_match.group(1)
        except Exception as e:
            pass
            # print(f"获取Chromedriver版本失败: {e}")
        return None

    def _check_version_compatibility(self, chrome_path, chromedriver_path):
        """
        检查Chrome和Chromedriver版本兼容性
        :param chrome_path: Chrome可执行文件路径
        :param chromedriver_path: Chromedriver可执行文件路径
        :return: (is_compatible, chrome_version, chromedriver_version)
        """
        chrome_version = self._get_chrome_version(chrome_path)
        chromedriver_version = self._get_chromedriver_version(chromedriver_path)
        # print(f"Chrome版本: {chrome_version}, Chromedriver版本: {chromedriver_version}")
        
        # 如果无法获取版本信息，返回True允许尝试启动
        if not chrome_version or not chromedriver_version:
            #(f"警告: 无法获取版本信息 - Chrome: {chrome_version}, Chromedriver: {chromedriver_version}")
            return True, chrome_version, chromedriver_version
        
        # 提取主版本号进行比较
        chrome_major = chrome_version.split('.')[0]
        chromedriver_major = chromedriver_version.split('.')[0]
        
        is_compatible = chrome_major == chromedriver_major
        return is_compatible, chrome_version, chromedriver_version

    def _try_create_driver(self, chrome_path, chromedriver_path, option, temp_dir):
        """
        尝试创建Chrome WebDriver实例
        :param chrome_path: Chrome可执行文件路径
        :param chromedriver_path: Chromedriver可执行文件路径
        :param option: ChromeOptions实例
        :param temp_dir: 临时目录路径
        :return: Chrome WebDriver实例或None
        """
        try:
            option.binary_location = chrome_path
            service = Service(chromedriver_path)
            if self.is_selenium_wire and wire_webdriver:
                driver = wire_webdriver.Chrome(service=service, options=option)
            else:
                driver = selenium_webdriver.Chrome(service=service, options=option)
            if self.maximize_window:
                driver.maximize_window()
            
            # --- 防反爬：注入多段JS隐藏Selenium特征 ---
            js_hide_features = [
                # 隐藏webdriver属性
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined, configurable: true});",
                # 模拟真实浏览器插件
                "Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5], configurable: true});",
                # 设置语言
                "Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en'], configurable: true});",
                # 模拟Chrome运行时
                "window.chrome = {runtime: {}, loadTimes: function(){}, csi: function(){}, app: {}};",
                # 删除原型链上的webdriver
                "delete window.navigator.__proto__.webdriver;",
                # 删除Selenium相关属性
                r"for (let key in window) {if (key.match(/^[\$\_]{3,}/)) {try {delete window[key];} catch(e){}}}",
                # 隐藏自动化相关属性
                "Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})}), configurable: true});",
                # 模拟真实的navigator属性
                "Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8, configurable: true});",
                "Object.defineProperty(navigator, 'deviceMemory', {get: () => 8, configurable: true});",
                # 防止检测自动化工具
                "Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 0, configurable: true});",
                # 隐藏CDP相关属性
                "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;",
                "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;",
                "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;"
            ]
            for js in js_hide_features:
                driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js})
            
            return driver
        except Exception as e:
            pass
            # print(f"创建Chrome WebDriver失败: {e}")
            return None

    def getdriver(self):
        """
        创建并返回Chrome WebDriver实例，自动注入反检测JS，异常时抛出GetDriverException
        智能版本检测：优先使用正式版，版本不匹配时自动切换到测试版
        :return: selenium.webdriver.Chrome实例
        :raises: GetDriverException
        """
        if not self.check_proxy():
            raise GetDriverException(f"代理不可用或格式错误: {self.proxy}")
        
        if self.is_selenium_wire and wire_webdriver:
            option = wire_webdriver.ChromeOptions()  # 浏览器启动选项
        else:
            option = selenium_webdriver.ChromeOptions()  # 浏览器启动选项
        if self.headless:
            option.add_argument("--headless")  # 设置无界面模式
        option.add_argument("--window-size=1920,1080")
        option.add_argument("--disable-gpu")
        option.add_argument("--no-sandbox")
        option.add_argument("--disable-dev-shm-usage")
        # 隐藏Chrome测试版提示信息
        option.add_argument("--disable-blink-features=AutomationControlled")
        option.add_argument("--disable-features=VizDisplayCompositor")
        option.add_argument("--disable-background-timer-throttling")
        option.add_argument("--disable-backgrounding-occluded-windows")
        option.add_argument("--disable-renderer-backgrounding")
        option.add_argument("--disable-features=TranslateUI")
        option.add_argument("--disable-ipc-flooding-protection")
        # 添加唯一的用户数据目录，避免Chrome实例冲突
        temp_dir = tempfile.mkdtemp(prefix=f'chrome_automation_{uuid.uuid4().hex[:8]}_')
        option.add_argument(f'--user-data-dir={temp_dir}')
        option.add_argument('--no-first-run')
        option.add_argument('--no-default-browser-check')
        # 关键安全浏览禁用参数
        option.add_argument('--allow-insecure-localhost')
        option.add_argument('--allow-running-insecure-content')
        option.add_argument('--disable-features=BlockInsecurePrivateNetworkRequests,SafeBrowsing,DownloadBubble,SafeBrowsingEnhancedProtection,DownloadWarning')
        option.add_argument('--safebrowsing-disable-download-protection')
        option.add_argument('--disable-client-side-phishing-detection')
        option.add_argument('--disable-popup-blocking')
        option.add_argument('--ignore-certificate-errors')
        if self.url:
            option.add_argument(f"--unsafely-treat-insecure-origin-as-secure={self.url}")
        # User-Agent
        option.add_argument(f'--user-agent={self.user_agent}')
        # 自动化相关设置
        option.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        option.add_experimental_option("useAutomationExtension", False)
        # 代理设置
        if self.proxy:
            option.add_argument(f'--proxy-server={self.proxy}')
        # 下载配置
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "safebrowsing.disable_download_protection": True,
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "download_restrictions": 0,
        }
        option.add_experimental_option("prefs", prefs)
        
        # 平台与路径自动检测
        sys_platform = platform.system().lower()
        chrome_path = self.chrome_path
        chromedriver_path = self.chromedriver_path
        
        try:
            if sys_platform == 'windows':
                if not chrome_path:
                    chrome_path_candidates = [
                        os.path.join(f'C:\\Users\\{getpass.getuser()}', 'chrome\\chrome_win64\\chrome.exe'),  # 测试版
                        'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',  # 正式版
                    ]
                if not chromedriver_path:
                    chromedriver_path_candidates = [
                        os.path.join(f'C:\\Users\\{getpass.getuser()}', 'chrome\\chrome_win64\\chromedriver.exe'),
                        os.path.join(f'C:\\Users\\{getpass.getuser()}', 'chrome\\chromedriver.exe'),
                    ]
            elif sys_platform == 'linux':
                if not chrome_path:
                    chrome_path_candidates = [
                        '/usr/bin/chrome/chrome',  # 测试版
                        '/usr/bin/google-chrome',  # 正式版
                    ]
                if not chromedriver_path:
                    chromedriver_path_candidates = [
                        '/usr/bin/chromedriver',
                        '/usr/local/bin/chromedriver',
                    ]
            elif sys_platform == 'darwin':
                if not chrome_path:
                    chrome_path_candidates = [
                        '/usr/local/chrome/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',  # 测试版
                        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # 正式版
                    ]
                if not chromedriver_path:
                    chromedriver_path_candidates = [
                        '/usr/local/chrome/chromedriver',
                        '/usr/local/bin/chromedriver',
                        '/opt/homebrew/bin/chromedriver',
                    ]
            else:
                raise GetDriverException(f"不支持的平台: {sys_platform}")
            
            # 如果用户指定了路径，直接使用
            if chrome_path and chromedriver_path:
                driver = self._try_create_driver(chrome_path, chromedriver_path, option, temp_dir)
                if driver:
                    self.temp_dirs.append(temp_dir)
                    self.driver = driver
                    return driver
                else:
                    raise GetDriverException(f"指定的Chrome路径无法启动: {chrome_path}")
            
            # 智能版本检测和切换
            chrome_paths = [p for p in chrome_path_candidates if os.path.exists(p)]
            chromedriver_paths = [p for p in chromedriver_path_candidates if os.path.exists(p)]
            
            if not chrome_paths:
                raise GetDriverException("未找到Chrome浏览器，请手动指定chrome_path")
            if not chromedriver_paths:
                raise GetDriverException("未找到Chromedriver，请手动指定chromedriver_path")
            
            # 优先尝试正式版Chrome
            for chrome_path in chrome_paths:
                for chromedriver_path in chromedriver_paths:
                    # 检查版本兼容性
                    is_compatible, chrome_version, chromedriver_version = self._check_version_compatibility(chrome_path, chromedriver_path)
                    
                    if is_compatible:
                        # print(f"版本兼容: Chrome {chrome_version}, Chromedriver {chromedriver_version}")
                        driver = self._try_create_driver(chrome_path, chromedriver_path, option, temp_dir)
                        if driver:
                            self.temp_dirs.append(temp_dir)
                            self.driver = driver
                            return driver
                    else:
                        # print(f"版本不兼容: Chrome {chrome_version}, Chromedriver {chromedriver_version}")
                        # 即使版本不兼容也尝试启动，有时可能仍然可以工作
                        driver = self._try_create_driver(chrome_path, chromedriver_path, option, temp_dir)
                        if driver:
                            # print("警告: 版本不兼容, 建议更新Chromedriver")
                            self.temp_dirs.append(temp_dir)
                            self.driver = driver
                            return driver
            
            # 如果所有组合都失败，抛出异常
            raise GetDriverException("所有Chrome和Chromedriver组合都无法启动，请检查版本兼容性")
            
        except Exception as e:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception as cleanup_error:
                pass
            if isinstance(e, GetDriverException):
                raise e
            else:
                raise GetDriverException(f"启动ChromeDriver失败: {e}")

    def _cleanup_temp_dirs(self):
        """
        清理所有创建的临时目录
        """
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except:
                pass
        self.temp_dirs = []

    def __enter__(self):
        """
        支持with语法自动获取driver
        :return: selenium.webdriver.Chrome实例
        """
        self.driver = self.getdriver()
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        支持with语法自动清理资源
        """
        self.quit()

    def close(self):
        """
        关闭浏览器窗口并清理临时目录
        """
        if self.driver:
            try:
                self.driver.close()
            except:
                pass
        self._cleanup_temp_dirs()

    def quit(self):
        """
        彻底退出浏览器并清理临时目录
        """
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        self._cleanup_temp_dirs()


if __name__ == '__main__':
    # with GetDriver(
    #     headless=True,
    #     proxy=None,  # 代理（'socks5://127.0.0.1:1080'）
    #     user_agent=None,
    #     download_dir=None, 
    #     chrome_path=None, 
    #     chromedriver_path=None,
    # ) as driver:
    #     driver.get('https://www.baidu.com')
    #     print(driver.title)

    
    driver = GetDriver(headless=False).getdriver()
    driver.get('https://www.baidu.com')
    print(driver.title)
    import time
    time.sleep(1000)
