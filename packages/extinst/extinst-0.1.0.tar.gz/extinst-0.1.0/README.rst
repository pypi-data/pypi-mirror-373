extinst
=======

一个用于在Windows/Mac/Linux上自动安装Chrome插件的Python模块。

功能特性
--------

- 自动检测操作系统类型
- 自动查找Chrome安装路径
- 支持.crx格式的Chrome插件安装
- 简单易用的API

安装
----

.. code-block:: bash

    pip install extinst

使用示例
--------

.. code-block:: python

    from extinst import ChromeExtensionInstaller

    # 创建安装器实例
    installer = ChromeExtensionInstaller()

    # 安装本地crx文件
    extension_path = "path/to/extension.crx"
    installer.install_from_file(extension_path)

    # 从Chrome Web Store安装
    extension_id = "abcdefghijklmnopqrstuvwxyzabcdef"
    installer.install_from_store(extension_id)

    # 从Chrome Web Store下载扩展到本地（不安装）
    # 保存到默认路径
    installer.download_from_store(extension_id)
    # 保存到指定路径
    # installer.download_from_store(extension_id, save_path="my_extension.crx")

    # 列出已安装的扩展
    extensions = installer.list_installed_extensions()
    for ext in extensions:
        print(f"名称: {ext['name']}, ID: {ext['id']}")

支持的操作系统
------------

- Windows
- macOS
- Linux

注意事项
--------

1. 在使用前请确保Chrome浏览器已正确安装
2. 安装插件可能需要重启Chrome浏览器
3. 某些系统可能需要管理员/root权限

License
-------

MIT License