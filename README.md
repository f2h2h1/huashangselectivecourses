## v4说明    
这是一个用python写的，能全自动选课的脚本，python的版本号为3.6    
xuankefunc.py是入口文件    
只能在windows下使用，只适用于华商的教务系统    
#### 使用方法    
~~~
python xuankefunc.py ip地址 端口 学号 密码 课程名称 教师姓名 上课时间 已选修课的数量    
~~~
#### 注意    
如果教师姓名 上课时间，这两个个参数请填NULL    
如果需要选修的课时网络课，教师姓名 上课时间 这两个参数也请填NULL    
已选修课的数量这个参数一般情况下填NULL    
如果填了已选修课的数量这个参数，将会通过已选课程表格里的课程数量判断选课是否成功    
    
课程名称 教师姓名 上课时间，这三个参数必须和教务系统里可选课程表格一致    
如果遇到需要区分单双周的课程，上课时间必须填完整的    
例如：周一第7,8节{第4-18周|双周}    
#### 例子    
网络课的例子    
~~~
学号：417240101    
密码：123456789    
教务系统地址：172.16.17.11    
端口：80    
课程名称：文化差异与跨文化交际（网络）    
教师姓名：NULL    
上课时间：NULL    
已选修的课的数量：NULL    
python xuankefunc.py 172.16.17.11 80 417240101 123456789 文化差异与跨文化交际（网络） NULL NULL NULL    
~~~
不需要区分单双周的课程的例子    
~~~
学号：417240101    
密码：123456789    
教务系统地址：172.16.17.11    
端口：80    
课程名称：羽毛球    
教师姓名：廖昌盛    
上课时间：周五第7,8节    
已选修的课的数量：1    
python xuankefunc.py 172.16.17.11 80 417240101 123456789 羽毛球 廖昌盛 周五第7,8节 1    
~~~
需要区分单双周的课程的例子    
~~~
学号：417240101    
密码：123456789    
教务系统地址：172.16.17.11    
端口：80    
课程名称：羽毛球    
教师姓名：廖昌盛    
上课时间：周五第7,8节    
已选修的课的数量：1    
python xuankefunc.py 172.16.17.11 80 417240101 123456789 羽毛球 廖昌盛 周一第7,8节{第4-18周|双周} 1    
~~~
#### 关于hta文件    
就是一个简单的图形界面，不需要在命令行里输入参数    
    
gui-single.hta是单人选课界面    
    
gui-multiple.hta是多人选课界面    
能从excel表格里批量读取学号密码，然后通过cmd调用xuankefunc.py    
也就是说可以同时间帮多个小伙伴选课哦^-^    
windows server系统可能运行不了gui-multiple.hta    
#### 目录结构    
~~~
v4
├─xuankefunc.py           选课脚本
├─gui-single.hta          单人选课界面
├─gui-multiple.hta        多人选课界面
├─book1.xls               多人选课excel表格例子
~~~

## v3说明    
这是一个用python写的，能全自动选课的脚本，python的版本号为3.6    
xuankefunc4.py是入口文件    
只能在windows下使用，只适用于华商的教务系统    
### 使用方法    
python xuankefunc4.py ip地址 端口 学号 密码 课程名称 教师姓名 上课时间 已选修课的数量    
如果教师姓名 上课时间 已选修课的数量不清楚的话，这三个参数请填NULL    
如果需要选修的课时网络课，教师姓名 上课时间 这两个参数也请填NULL    
### 例子    
学号：417240101    
密码：123456789    
教务系统地址：172.16.17.11    
端口：80    
课程名称：羽毛球    
教师姓名：廖昌盛    
上课时间：周五第7,8节    
已选修的课的数量：1    
python xuankefunc4.py 172.16.17.11 80 417240101 123456789 羽毛球 廖昌盛 周五第7,8节 1    
### 关于那个hta文件（gui-multiple.hta）    
就是一个图形界面，不需要在命令行里输入参数    
能从excel表格里批量读取学号密码，然后通过cmd调用xuankefunc4.py    
也就是说可以同时间帮多个小伙伴选课哦^-^    
    
## v2说明    
这是一个用python写的，能全自动选课的脚本，python的版本号为3.6    
webs20_001.py是入口文件    
只能在windows下使用，只适用于华商的教务系统    
### 使用方法    
python webs20_001.py ip地址 端口 学号 密码 课程关键字   
### 例子    
学号：417240101    
密码：123456789    
教务系统地址：172.16.17.11    
端口：8889    
课程关键字：网络    
python webs20_001.py 172.16.17.11 8889 417240101 23456789 网络    
### 关于那个hta文件（test17.hta）    
就是一个图形界面，不需要在命令行里输入参数    
能从excel表格里批量读取学号密码，然后通过cmd调用webs20_001.py    
也就是说可以同时间帮多个小伙伴选课哦^-^    
    
## v1说明    
这是一个用python写的，能自动打开选课页面的脚本，python的版本号为3.6    
只能在windows下使用，只适用于华商的教务系统    
### 使用方法    
python webs14ie.py ip地址 端口 学号 密码    
### 例子    
学号：417240101    
密码：123456789    
教务系统地址：172.16.17.11    
端口：8889    
python webs14ie.py 172.16.17.11 8889 417240101 23456789    
### 关于那个hta文件    
就是一个图形界面，不需要在命令行里输入参数    
会一次性打开36个选课页面，总有一个不崩溃的^-^    
使用时，系统需要配置python环境，需要和那个python脚本放在同一目录下    
