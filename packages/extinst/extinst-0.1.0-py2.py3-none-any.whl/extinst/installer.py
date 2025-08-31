import os
import platform
import shutil
import json
import time
import subprocess
from pathlib import Path
import tempfile
import zipfile
import requests
import re

class ChromeExtensionInstaller:
    """
    Chrome浏览器插件自动安装器
    支持Windows/Mac/Linux操作系统
    """
    def __init__(self):
        self.os_type = platform.system()
        self.chrome_path = self._find_chrome_path()
        self.user_data_dir = self._find_user_data_dir()
        self.extensions_dir = self._find_extensions_dir()
        self.policy_path = self._get_policy_path()

    def _find_chrome_path(self):
        """查找Chrome浏览器的安装路径"""
        if self.os_type == "Windows":
            # Windows系统Chrome路径
            paths = [
                os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
            ]
            for path in paths:
                if os.path.exists(path):
                    return path
        elif self.os_type == "Darwin":  # macOS
            # macOS系统Chrome路径
            chrome_app = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            if os.path.exists(chrome_app):
                return chrome_app
        elif self.os_type == "Linux":
            # Linux系统Chrome路径
            paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/usr/local/bin/google-chrome"
            ]
            for path in paths:
                if os.path.exists(path):
                    return path
        return None

    def _find_user_data_dir(self):
        """查找Chrome用户数据目录"""
        if self.os_type == "Windows":
            return os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
        elif self.os_type == "Darwin":
            return os.path.expanduser("~/Library/Application Support/Google/Chrome")
        elif self.os_type == "Linux":
            return os.path.expanduser("~/.config/google-chrome")
        return None

    def _find_extensions_dir(self):
        """查找Chrome扩展目录"""
        if self.user_data_dir:
            # 默认使用Default配置文件的扩展目录
            return os.path.join(self.user_data_dir, "Default", "Extensions")
        return None

    def _get_policy_path(self):
        """获取Chrome策略配置路径"""
        if self.os_type == "Windows":
            return os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\master_preferences")
        elif self.os_type == "Darwin":
            return "/Library/Google/Chrome/master_preferences"
        elif self.os_type == "Linux":
            return "/etc/google-chrome/master_preferences"
        return None

    def _get_extension_id(self, crx_path):
        """从CRX文件中提取扩展ID"""
        # 这是一个简化的实现，实际可能需要解析CRX文件头
        # 这里我们使用文件名作为ID的一部分
        import hashlib
        with open(crx_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return file_hash[:32]

    def _is_chrome_running(self):
        """检查Chrome是否正在运行"""
        if self.os_type == "Windows":
            try:
                subprocess.check_output("tasklist", shell=True)
                return "chrome.exe" in subprocess.check_output("tasklist", shell=True).decode()
            except:
                return False
        elif self.os_type in ["Darwin", "Linux"]:
            try:
                subprocess.check_output(["pgrep", "chrome"], stderr=subprocess.STDOUT)
                return True
            except subprocess.CalledProcessError:
                return False
        return False

    def _kill_chrome(self):
        """关闭Chrome浏览器进程"""
        if self._is_chrome_running():
            if self.os_type == "Windows":
                subprocess.call(["taskkill", "/F", "/IM", "chrome.exe"])
            elif self.os_type in ["Darwin", "Linux"]:
                subprocess.call(["pkill", "chrome"])
            time.sleep(2)  # 等待进程完全关闭

    def install_from_file(self, crx_path):
        """
        从本地CRX文件安装Chrome插件
        :param crx_path: CRX文件的路径
        :return: 安装是否成功
        """
        if not os.path.exists(crx_path):
            raise FileNotFoundError(f"CRX文件不存在: {crx_path}")

        if not self.chrome_path:
            raise Exception("未找到Chrome浏览器安装路径")

        if not self.extensions_dir:
            raise Exception("未找到Chrome扩展目录")

        try:
            # 获取扩展ID
            extension_id = self._get_extension_id(crx_path)
            
            # 创建扩展目录
            extension_dir = os.path.join(self.extensions_dir, extension_id)
            os.makedirs(extension_dir, exist_ok=True)
            
            # 临时目录用于解压CRX文件
            with tempfile.TemporaryDirectory() as temp_dir:
                # CRX文件实际上是一个zip文件，我们可以直接解压
                with zipfile.ZipFile(crx_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # 将解压后的文件复制到扩展目录
                for item in os.listdir(temp_dir):
                    s = os.path.join(temp_dir, item)
                    d = os.path.join(extension_dir, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
            
            # 创建或修改master_preferences文件来强制安装扩展
            self._update_master_preferences(extension_id)
            
            print(f"Chrome扩展安装成功: {extension_id}")
            print("请重启Chrome浏览器以加载扩展")
            return True
        except Exception as e:
            print(f"安装扩展时出错: {str(e)}")
            return False

    def install_from_store(self, extension_id):
        """
        从Chrome Web Store安装扩展
        :param extension_id: Chrome Web Store中的扩展ID
        :return: 安装是否成功
        """
        try:
            # 创建或修改master_preferences文件来强制安装扩展
            self._update_master_preferences(extension_id)
            
            print(f"已配置Chrome自动安装扩展: {extension_id}")
            print("请重启Chrome浏览器以从Web Store下载并安装扩展")
            return True
        except Exception as e:
            print(f"配置扩展时出错: {str(e)}")
            return False

    def download_from_store(self, extension_id, save_path=None):
        """
        从Chrome Web Store下载扩展并保存到本地
        :param extension_id: Chrome Web Store中的扩展ID
        :param save_path: 保存路径，默认为当前目录下的{extension_id}.crx
        :return: 下载的文件路径，如果下载失败则返回None
        """
        try:
            # 如果未指定保存路径，使用默认路径
            if save_path is None:
                save_path = f"{extension_id}.crx"
            
            # Chrome Web Store下载URL
            # 注意：直接从Chrome Web Store下载CRX文件可能需要特定的头部信息
            # 这里使用一个已知的下载链接格式
            crx_url = f"https://clients2.google.com/service/update2/crx?response=redirect&os=win&arch=x86-64&nacl_arch=x86-64&prod=chromecrx&prodchannel=stable&prodversion=96.0.4664.45&x=id%3D{extension_id}%26installsource%3Dondemand%26uc"
            
            print(f"正在从Chrome Web Store下载扩展: {extension_id}")
            print(f"下载URL: {crx_url}")
            
            # 添加适当的请求头以模拟Chrome浏览器
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
            }
            
            # 发送请求下载文件
            with requests.get(crx_url, headers=headers, stream=True, allow_redirects=True) as response:
                response.raise_for_status()  # 如果状态码不是200，抛出异常
                
                # 检查响应内容是否为CRX文件
                content_type = response.headers.get('Content-Type', '')
                if not (content_type == 'application/x-chrome-extension' or response.url.endswith('.crx')):
                    print(f"警告: 下载的内容可能不是CRX文件 (Content-Type: {content_type})")
                    # 检查是否重定向到了Web Store页面
                    if 'chrome.google.com/webstore' in response.url:
                        print("错误: 无法直接下载扩展，可能需要登录或扩展有下载限制")
                        return None
                
                # 保存文件
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # 过滤掉保持连接的空块
                            f.write(chunk)
            
            print(f"扩展下载成功，保存到: {save_path}")
            return save_path
        except requests.exceptions.RequestException as e:
            print(f"下载扩展时发生网络错误: {str(e)}")
            return None
        except Exception as e:
            print(f"下载扩展时出错: {str(e)}")
            return None

    def _update_master_preferences(self, extension_id):
        """更新master_preferences文件以强制安装扩展"""
        # 创建目录（如果不存在）
        policy_dir = os.path.dirname(self.policy_path)
        if policy_dir and not os.path.exists(policy_dir):
            try:
                os.makedirs(policy_dir)
            except PermissionError:
                print("警告: 没有权限创建策略目录，可能需要管理员/root权限")
                return
        
        # 读取现有配置或创建新配置
        preferences = {}
        if os.path.exists(self.policy_path):
            try:
                with open(self.policy_path, 'r') as f:
                    preferences = json.load(f)
            except:
                pass
        
        # 确保extensions节点存在
        if "extensions" not in preferences:
            preferences["extensions"] = {}
        
        # 添加扩展ID到强制安装列表
        if "forced_installs" not in preferences["extensions"]:
            preferences["extensions"]["forced_installs"] = []
        
        # 检查扩展是否已经在列表中
        extension_exists = False
        for ext in preferences["extensions"]["forced_installs"]:
            if ext.get("id") == extension_id:
                extension_exists = True
                break
        
        if not extension_exists:
            preferences["extensions"]["forced_installs"].append({
                "id": extension_id,
                "update_url": "https://clients2.google.com/service/update2/crx"
            })
        
        # 写入配置文件
        try:
            with open(self.policy_path, 'w') as f:
                json.dump(preferences, f, indent=2)
        except PermissionError:
            print(f"警告: 没有权限写入配置文件 {self.policy_path}，可能需要管理员/root权限")
        except Exception as e:
            print(f"写入配置文件时出错: {str(e)}")

    def list_installed_extensions(self):
        """列出已安装的扩展"""
        if not self.extensions_dir or not os.path.exists(self.extensions_dir):
            print("未找到扩展目录")
            return []
        
        extensions = []
        for ext_id in os.listdir(self.extensions_dir):
            ext_path = os.path.join(self.extensions_dir, ext_id)
            if os.path.isdir(ext_path):
                # 查找manifest.json文件
                for root, _, files in os.walk(ext_path):
                    if "manifest.json" in files:
                        manifest_path = os.path.join(root, "manifest.json")
                        try:
                            with open(manifest_path, 'r') as f:
                                manifest = json.load(f)
                                extensions.append({
                                    "id": ext_id,
                                    "name": manifest.get("name", "未知"),
                                    "version": manifest.get("version", "未知"),
                                    "description": manifest.get("description", "无描述")
                                })
                        except:
                            extensions.append({
                                "id": ext_id,
                                "name": "未知",
                                "version": "未知",
                                "description": "无法解析manifest.json"
                            })
                        break
        
        return extensions