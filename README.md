# 项目简介
利用浏览器调试模式和selenium自动化工具，实现一些小工具的使用，通过自动化脚本和用户本人操作相结合，可以相对轻松地绕开绝大多数网站的防火墙和验证码。

## 环境配置

### python包安装
安装selenium包：
pip install selenium

### 浏览器驱动安装
下载对应浏览器对应版本的驱动，并将驱动文件放到website的driver目录下，可以参考selenium官方文档。
这里提供chrome和edge浏览器的驱动下载地址：
- Chrome：https://chromedriver.chromium.org/downloads
- Edge：https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/


## 浏览器相关参数配置
在脚本文件开头配置浏览器相关参数browser_config，包括：
- browser_name：浏览器名称，目前支持chrome、edge
- port：调试模式端口号，根据需要更改
- profile_path ：调试模式会创建新的用户配置文件，这里是希望用户配置文件存放的路径
- directory_path ：浏览器的可执行文件路径


## 脚本文件
脚本文件位于项目跟目录下，有不同的功能，可以根据需要进行选择，配置相关变量后直接运行即可。
- sunba.py: 指定某个百度贴吧，进行水贴

