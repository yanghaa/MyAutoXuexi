
##首先说明
“学习强国”学习平台是由中共中央宣传部主管，以习近平新时代中国特色社会主义思想和党的十九大精神为主要内容，立足全体党员、面向全社会的优质平台。
本项目初衷是本人为了学习python和appium等自动化框架，本人也是非专业编程人员，所以还需要各路高手一起完善项目。
本项目遵守开源许可协议，严禁用于商业用途，禁止使用进行任何盈利活动，对使用本项目进行一切非法行为产生的后果，本人概不负责。

## 项目主要参考：
>#### <https://github.com/kessil/AutoXue> 和 <https://github.com/TechXueXi/AutoXue>
>####非常感谢以上项目作者！
>####我的修改主要基于kessil，后期修改延续他的思路而成。
>####交流群 https://t.me/buxuebushuang，欢迎有兴趣的同好一起加入学习python。


>## 12.15 代码上线
## 已实现功能
#### 1. 满分自动学习（除强国运动外） 
#### 2. 多个号同时一起学习
#### 3. 支持三种模拟器，可以任意在ini文件中选择切换使用。
#### 4. 模拟器设置好后，程序会自动启动模拟器，自行开始学习。多号同刷，请看后面的使用说明
#### 5. 为满足刷星、刷题（更新答题库）或者补学等要求，各个模块可以单独测试运行，可以设置测试次数。（挑战答题通关不是梦，本人没那么无聊，没测试过50次以上）
#### 6. 支持sqlite和mysql题库，在data目录下的数据文件已经由8000题题库，且基本经过本人几个月来不停更正错误答案，基本错误量已经非常少。
#### 7. 为怕自己粗心，误把私人帐号密码传输出来，提供了帐号RSA加密功能（gen_key.py生成公私密钥，jiami.py对个人帐号进行加密输出密文），不想使用可以修改源码即可。  
~~~
   # 在config目录下有users.ini，修改为自己要刷的帐号和密码，用jiami.py生成相应密文
   # 准备几个号同时学习需要设置对应的用户名和密码，采用了RSA 1024位加密解密  
   # pubkey_path，prikey_path，对应公钥和私钥的路径
   # 使用gen_key.py可以生成公钥和私钥文件，默认生成文件名为‘public.pem’和‘private.pem’  
   # jiami.py 用来生成用户名和密码对应的RSA加密密文  
   
   prikey_path = d:\\rsa\\private.pem  
   pubkey_path = d:\\rsa\\public.pem
~~~
~~~
# 如果不想使用用户名加密方式，可以修改源码这段代码 

'username': decrypt(cfg.get('users', f'username{i}'), cfg.get('users', 'prikey_path')),  
'password': decrypt(cfg.get('users', f'password{i}'), cfg.get('users', 'prikey_path')),
              
# 改为

'username': cfg.get('users', f'username{i}'),  
'password': cfg.get('users', f'password{i}'),
~~~             
#### 8.提供由json题库转换到mysql数据库的脚本（json_to_mysql.py），提供从<https://124731.cn/>网上提供的题库转化到本地数据库的不成熟的脚本；update_packages.py是自动升级所有本机python模块的（供“版本不是最新就不爽”强迫症患者使用）
#### 9.程序使用的模块都是更新至最新版本，所有测试都是基于到目前为止的最新版本
>## 以下为服用指南
#### 1. 首先需要安装模拟器（逍遥、雷电、Nox三选一），并在ini文件里面设置安装目录（文件夹）信息。目录名称里面又没哟含有空格没关系。
~~~
    注意ini文件设定项前有(;或者#)是注释行，相同的键值是N选一，选了一个注意注释掉另外的
    [emu_args]
    是否采用真机进行答题，是（1），不是（0）
    true_machine = 0
    Microvirt（逍遥模拟器）、雷电（leidian）和Nox（夜神模拟器）三选一
    emu_name = microvirt
    ;emu_name = nox
    ;emu_name = leidian
    microvirt_path = D:\Program Files\Microvirt\MEmu
    nox_path = D:\Program Files\Nox\bin
    leidian_path = D:\Program Files\leidian\LDPlayer4
~~~
#### 2. 安装python，或者安装vscode、pycharm等IDE直接在里面调试运行也行 
#### 3. 安装JDK（我使用的jdk1.8.0_121）
#### 4. 安装android sdk r24.4.1
#### 5. 由于采用的是数据库，可以考虑安装一个Navicat进行数据库管理数据。注意在ini文件里面设定你喜欢用的数据库；默认是sqlite，data目录下已有相应的题库数据库。对“答题争上游”和“双人对战”胜负情况做简单统计。
~~~
    注意ini文件设定项前有(;或者#)是注释行，相同的键值是N选一，选了一个注意注释掉另外的
    # 选择数据库平台
    [database]
    # sqlite3数据库存储在/data文件夹下
    data_platform = sqlite3
    ;data_platform = mysql
~~~
#### 6. 模拟器设置：可以多个号，同时一起刷（因为订阅耗时间较多，有单独为各个号设置的事先翻页页数）
~~~
# 用户名和密码
username1 = f6ycdByVgBkCHQwqC+qUxg8LyY2vxC3d00MzqtKtWvJDBJQ+c50xw7Fk2XiY+RIb4YnGrTFq4u+dZC5U9KA+vH40mkHOpWQnIZVSFvQse5Z0si9GilOA/9aNVjV1yz5A88/I2E/yZ0yQMpE7iiHWJPzfHB2vwKr9b0LHb0c9DAE=
password1 = j9zzXRpPOy6SIfTLijMXCljIo1preGIs26dNEkmlR+H1jxXLQyFPKZ+/gk5hktnoaT0n4jDJGAsi08s7swIv7ucvSXqBkAQt0WYqn7seIZ13Ow79f0kx6MalCRX3/AKtrOhBCcHPtyDbQbvhMWyTrS1PxEIOibz7tONogGDAgzw=
# 多开的话，分两种情况：逍遥模拟器为第一类，雷电和Nox为第二类情况。
# 第一类情况，因为逍遥模拟器是固定名字（'MEmu', 'MEmu_1', 'MEmu_2', 'MEmu_3',...）的，根据实际运行个数修改为emu_mv_1=MEmu, emu_mv_2=MEmu_1,emu_mv_3=MEmu_2等名称。可以参考ini里面
emu_mv_1 = MEmu
# 第二类情况：下面是设置夜神或者雷电模拟器，因为夜神和雷电启动模拟器是以多开器里命名的名字来启动的，所以要和多开器里面的命名相同。注意是键名是命名形式："emu_nox_"+数字，名字和多开器里面的名字相同即可。
emu_nox_1 = long
# 为提高订阅效率，设置事先翻过已经订阅的页面
# 在程序里面有提示上次翻动到第几页有订阅内容
# 设置为0表示订阅已经全部完成了，无须在订阅（这部分会在以后版本更新为根据上次翻页情况自动设置）
   subscribed_pages_1 = 54
~~~
#### 9. 
#### 8.其他无关运行的小知识
* **如果需要将pip源设置为国内源，阿里源、豆瓣源、网易源等**  
在windows操作如下：  
（1）打开文件资源管理器(文件夹地址栏中)  
（2）地址栏上面输入 %appdata%  
（3）在这里面新建一个文件夹 pip  
（4）在pip文件夹里面新建一个文件叫做 pip.ini ,内容写如下即可  
~~~
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
[install]
trusted-host = mirrors.aliyun.com
~~~

---
#**上传之前的历史版本迭代情况：**
>## 12.13 更新
1. 争上游答题效率更新，控制在20秒左右答题完成，胜率大幅度提高
2. 修改少量bug

>## 11.8 重大更新
> ####整体框架换成UIautomator2
1. 所有代码更换，效率提高，但是多开稳定性下降
2. 争上游答题胜率提高
3. 多模拟器切换（目前支持逍遥、雷电、Nox三种）--本人测试大多基于逍遥模拟器。

>## 10.17 更新
1. 已经基本完成强国满分的目标，修改完成争上游答题部分
2. 修改专项答题，提供精准度，但是还是无法解决答案提示差别大的时候的精准度
<br/>


>## 09.26 更新
1. 完成专项答题和自动订阅模块
2. 初步完成新上线的争上游答题和双人对战模块

<br/>

>## 09.07 已经实现的功能
1. 脱离批处理启动，支持同时开多个号，appium和模拟器随着需要启动相应的服务和数量，运行一次大概在45分钟
2. 各个的用户相关信息置入到配置文件中，帐号密码等敏感信息使用了RSA加密算法方式保护
3. 题库重新采集到了mysql数据库，实现本地题库处理（查询、更新题库）
4. 支持单个模块单独测试运行
5. **现支持挑战答题、每日答题、专项答题、新闻阅读、视听学习等所有学习项，可以达到57分/天。**


---

### 本自动学习脚本的缺点：对电脑配置要求较高，且安装运行环境很麻烦  

---

## 免责申明

`AutoXue`为本人`Python`学习交流的开源非营利项目，仅作为`Python`学习交流之用，使用需严格遵守开源许可协议。严禁用于商业用途，禁止使用`AutoXue`进行任何盈利活动。对一切非法使用所产生的后果，本人概不负责。

## 写在最后

+ 本人学习python时间较短（一个半月），有很多不懂的地方，只是对大神的项目作了些修补而已，错漏地方还有很多，在此再次感谢原项目作者，从中学习到很多python的知识。
+ 强烈建议需要自定义配置文件的用户下载使用vscode编辑器,[why vscode?](https://hacpai.com/article/1569745141957)，请一定不要使用系统自带记事本修改配置文件。
"# MyAutoXuexi" 
