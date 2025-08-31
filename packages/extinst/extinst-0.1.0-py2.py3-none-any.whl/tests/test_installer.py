#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chrome扩展安装器测试
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock, mock_open

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extinst.installer import ChromeExtensionInstaller


class TestChromeExtensionInstaller(unittest.TestCase):
    """测试ChromeExtensionInstaller类"""
    
    def setUp(self):
        """每个测试用例前的设置"""
        self.installer = ChromeExtensionInstaller()
    
    @patch('platform.system')
    def test_find_chrome_path_windows(self, mock_system):
        """测试在Windows系统上查找Chrome路径"""
        mock_system.return_value = 'Windows'
        
        with patch('os.path.exists') as mock_exists, \
             patch('os.path.expandvars') as mock_expandvars:
            # 模拟路径存在
            mock_exists.return_value = True
            # 模拟环境变量展开
            mock_expandvars.side_effect = lambda x: x.replace('%ProgramFiles%', 'C:\Program Files')
            
            installer = ChromeExtensionInstaller()
            chrome_path = installer._find_chrome_path()
            
            self.assertIn('chrome.exe', chrome_path)
    
    @patch('platform.system')
    def test_find_chrome_path_macos(self, mock_system):
        """测试在macOS系统上查找Chrome路径"""
        mock_system.return_value = 'Darwin'
        
        with patch('os.path.exists') as mock_exists:
            # 模拟路径存在
            mock_exists.return_value = True
            
            installer = ChromeExtensionInstaller()
            chrome_path = installer._find_chrome_path()
            
            self.assertEqual(chrome_path, '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    
    @patch('platform.system')
    def test_find_chrome_path_linux(self, mock_system):
        """测试在Linux系统上查找Chrome路径"""
        mock_system.return_value = 'Linux'
        
        with patch('os.path.exists') as mock_exists:
            # 模拟路径存在
            mock_exists.return_value = True
            
            installer = ChromeExtensionInstaller()
            chrome_path = installer._find_chrome_path()
            
            self.assertIn('google-chrome', chrome_path)
    
    @patch('os.path.exists')
    def test_is_chrome_running_windows(self, mock_exists):
        """测试在Windows系统上检查Chrome是否运行"""
        self.installer.os_type = 'Windows'
        
        # 测试Chrome运行的情况
        with patch('subprocess.check_output') as mock_check_output:
            mock_check_output.return_value = b'chrome.exe'
            self.assertTrue(self.installer._is_chrome_running())
        
        # 测试Chrome未运行的情况
        with patch('subprocess.check_output') as mock_check_output:
            mock_check_output.return_value = b'notepad.exe'
            self.assertFalse(self.installer._is_chrome_running())
    
    def test_get_extension_id(self):
        """测试获取扩展ID"""
        # 创建一个临时文件用于测试
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'test content')
            temp_path = f.name
        
        try:
            extension_id = self.installer._get_extension_id(temp_path)
            # 验证ID是32个字符的哈希值
            self.assertEqual(len(extension_id), 32)
        finally:
            # 清理临时文件
            os.unlink(temp_path)
    
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('zipfile.ZipFile')
    @patch('shutil.copytree')
    @patch('shutil.copy2')
    @patch('tempfile.TemporaryDirectory')
    @patch.object(ChromeExtensionInstaller, '_update_master_preferences')
    @patch.object(ChromeExtensionInstaller, '_get_extension_id')
    def test_install_from_file(self, mock_get_id, mock_update_prefs, \
                             mock_temp_dir, mock_copy2, mock_copytree, \
                             mock_zipfile, mock_exists, mock_makedirs):
        """测试从文件安装扩展"""
        # 设置模拟返回值
        mock_exists.return_value = True
        mock_temp_dir.return_value.__enter__.return_value = '/tmp/test'
        mock_get_id.return_value = 'test_extension_id'
        
        # 模拟os.listdir返回值
        with patch('os.listdir') as mock_listdir:
            mock_listdir.return_value = ['file1.js', 'dir1']
            
            # 模拟os.path.isdir返回值
            with patch('os.path.isdir') as mock_isdir:
                def mock_isdir_side_effect(path):
                    return path.endswith('dir1')
                mock_isdir.side_effect = mock_isdir_side_effect
                
                # 执行安装
                result = self.installer.install_from_file('test.crx')
                
                # 验证结果
                self.assertTrue(result)
                mock_update_prefs.assert_called_once_with('test_extension_id')
    
    @patch.object(ChromeExtensionInstaller, '_update_master_preferences')
    def test_install_from_store(self, mock_update_prefs):
        """测试从Chrome Web Store安装扩展"""
        # 执行安装
        result = self.installer.install_from_store('test_extension_id')
        
        # 验证结果
        self.assertTrue(result)
        mock_update_prefs.assert_called_once_with('test_extension_id')
    
    @patch('os.path.exists')
    @patch('json.load')
    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_update_master_preferences(self, mock_file, mock_json_dump, mock_json_load, mock_exists):
        """测试更新master_preferences文件"""
        # 设置模拟返回值
        mock_exists.return_value = True
        mock_json_load.return_value = {"extensions": {"forced_installs": []}}
        
        # 执行更新
        self.installer._update_master_preferences('test_extension_id')
        
        # 验证结果
        mock_json_dump.assert_called_once()
        mock_file.assert_called()


if __name__ == '__main__':
    unittest.main()