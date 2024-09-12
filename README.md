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
- profile_path ：调试模式会创建新的用户配置文件，这里是希望用户配置文件存放的路径，不同浏览器应放在不同文件夹里
- directory_path ：浏览器的可执行文件目录路径(不包括可执行文件名)


## 脚本文件
脚本文件位于项目根目录下，有不同的功能，可以根据需要进行选择，配置相关变量后直接运行即可。

### 脚本文件启动
运行脚本文件，打开浏览器后程序会暂停，这时用户可以在已经打开的浏览器中对相关网站进行登录、验证等操作，然后在终端按下任意键以继续。

### 脚本文件介绍
- sunba.py: 指定某个百度贴吧，进行水贴，需要给定某个吧主页的url，示例:url = "https://tieba.baidu.com/f?ie=utf-8&kw=%E6%9D%8E%E6%AF%85"
- qiangke.py: 用于在whu信息门户自动选课，需要在程序第一次暂停期间先手动登录并打开目标课程页面,漏出“选课”字样的按钮，并保证浏览器只有一个标签页，后续敲击终端程序会自动选课

