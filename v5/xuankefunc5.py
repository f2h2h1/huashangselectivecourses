# coding:utf-8
from urllib import request, parse
from html.parser import HTMLParser
import re
import os
import time
import sys
import json
import random
import string

# 定义教务系统重启的异常
class FError(Exception):
    pass

# 去除html属性
# 去除已选课程表格的html属性
class MyHTMLParser(HTMLParser):
    age = ""
    def handle_starttag(self, tag, attrs):
        # print('<%s>' % tag)
        tag = '<'+tag+'>'
        self.age += tag

    def handle_endtag(self, tag):
        # print('</%s>' % tag)
        tag = '</'+tag+'>'
        self.age += tag

    def handle_startendtag(self, tag, attrs):
        # print('<%s/>' % tag)
        tag = '<'+tag+'/>'
        self.age += tag

    def handle_data(self, data):
        # print(data)
        self.age += data
# 去除可选课程表格的html属性
class MyHTMLParser2(HTMLParser):
    age = ""
    title = ""
    def handle_starttag(self, tag, attrs):
        # print('<%s>' % tag)
        # 获取完整的上课时间（包含单双周的上课时间）
        if tag == "td":
            if len(attrs) > 0:
                if len(attrs[0]) > 0 and attrs[0][0] == "title":
                    self.title = attrs[0][1]
        tag = '<'+tag+'>'
        self.age += tag

    def handle_endtag(self, tag):
        # print('</%s>' % tag)
        tag = '</'+tag+'>'
        self.age += tag

    def handle_startendtag(self, tag, attrs):
        # print('<%s/>' % tag)
        tag = '<'+tag+'/>'
        self.age += tag

    def handle_data(self, data):
        # print(data)
        if self.title != "":
            self.age += self.title
            self.title = ""
        else:
            self.age += data


# 打印日志的函数
def logger(str):
    desc = "["+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"]" + str + "\n"
    print(desc)
    # log_name是全局变量
    fo = open(log_name, "a", encoding = 'utf8')
    fo.write(desc)
    fo.close()

# 打印变量用的函数
def print_all(module_):
  modulelist = dir(module_)
  length = len(modulelist)
  for i in range(0,length,1):
    print (module_,modulelist[i])

# 初始化
def init(ipaddress, port, studentid, password, tagclass, teacher, classtime, taglen):
    # 设置cmd编码
    os.system('chcp 65001')
    # 设置cmd标题
    global tag_id
    tag_id = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    title = studentid + "-" + tagclass + "-" + port + "-" + tag_id
    os.system("title " + title)
    
    # 设置cmd窗口大小
    os.system('mode con: cols=95')
    print(title)
    print("If you encounter a garbled code, please set the font of the command line to be Chinese font.")

    global log_name # 日志文件名

    log_name = title + ".log"

    init = ipaddress + "    " + \
            port + "    " + \
            studentid + "    " + \
            tagclass + "    " + \
            teacher + "    " + \
            classtime + "    " + \
            taglen + "    "
    logger(init)

# curl函数
def basecurl(url, login_data = "", headers_data = {}):
    protocol = 'http://'
    url = protocol + url
    try:
        req = request.Request(url, data=login_data.encode('utf-8'), headers=headers_data)
        u = request.urlopen(req)
        if u.status != 200:
            ret = {"status":0, "desc":"打开网址失败"}
        else:
            with u as f:
                result = f.read().decode('gb18030')
            ret = {"status":1, "desc":"打开网址失败", "geturl":u.geturl(), "getstr":result}
    except:
        ret = {"status":-1, "desc":"curl错误"}
    return ret

# 获取sessionid和隐藏字段的函数
# 以字典的形式返回sessionid和隐藏字段
def get_new_sessionid(ipaddress, port):
    url = ipaddress + ':' + port + '/' + 'default2.aspx'
    result = basecurl(url)
    if result['status'] != 1:
        logger("登录页面打开失败")
        ret = {"status":-1, "desc":"session获取失败", "error":result['desc']}
    else:
        logger("登录页面打开成功")
        # 抓取sessionid
        m = re.match(r'.*\((.*)\).*', result['geturl'])
        sessionid = m.group(1)
        # 抓取隐藏字段
        VIEWSTATE =re.findall(r'<input type="hidden" name="__VIEWSTATE" value="(.*?)" />', result['getstr'], re.I)
        ret = {"status":1, "desc":"session获取成功", "sessionid":sessionid, "VIEWSTATE":VIEWSTATE[0]}
    return ret

# post登录数据
def post_denglu(url, studentid, password):
    url = url + "default_vsso.aspx"
    postdata =  parse.urlencode([
                    ('TextBox1', studentid),
                    ('TextBox2', password),
                    ('RadioButtonList1_2', "学生"),
                    ('Button1', ""),
                ])
    result = basecurl(url, postdata)
    if result['status'] != 1:
        logger("登录参数发送失败")
        ret = {"status":0, "desc":"登录参数发送失败", "error":result['desc']}
    else:
        logger("登录参数发送成功")
        p1 = r'评价完后请完善个人信息和修改登入密码' # 这是我们写的正则表达式
        pattern1 = re.compile(p1) # 正则表达式编译
        matcher1 = re.search(pattern1, result['getstr']) # 正则表达式查询
        if matcher1 == None:
            logger("登录失败")
            ret = {"status":-2, "desc":"登录失败"}
        else:
            logger("登录成功")
            ret = {"status":1, "desc":"登录成功"}
    return ret

# 登录函数
def denglu(ipaddress, port, studentid, password):
    result = get_new_sessionid(ipaddress, port)
    if result['status'] != 1:
        # sessionid获取失败
        desc = "sessionid获取失败"
        logger(desc)
        ret = {"status":0, "desc":desc, "errors":result['desc']}
    else:
        # sessionid获取成功
        sessionid = result['sessionid']
        # post登录数据
        url = ipaddress + ":" + port + "/(" + sessionid + ")/"
        ret = post_denglu(url, studentid, password)
        ret['sessionid'] = sessionid
    return ret

# 通过是否回到登录页面判断教务系统是否重启
# 重启后sessionid会失效需要重新登录
def is_jw_restart(key):
    p1 = r'请输入验证码' # 这是我们写的正则表达式
    pattern1 = re.compile(p1) # 正则表达式编译
    matcher1 = re.search(pattern1, key) # 正则表达式查询
    if matcher1 == None:
        desc = "没有回到登录页面，教务系统没有重启"
        # logger(desc)
        ret = {"status":1, "desc":desc}
    else:
        desc = "回到登录页面，目测教务系统重启了"
        logger(desc)
        ret = {"status":0, "desc":desc}
    return ret

# 打开选课页面的函数
# 如果成功打开选课页面返回result，
def open_xuanke(url, studentid, postdata = ""):
    time.sleep(3)
    url = url +'xf_xsqxxxk.aspx?xh=' + studentid + "&gnmkdm=N121203"
    headers_data={
        # 'Host': '119.145.67.59',
        'Connection': 'keep-alive',
        # 'Content-Length': '197',
        'Cache-Control': 'max-age=0',
        # 'Origin': 'http://119.145.67.59',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36 LBBROWSER',
        # 'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'DNT': '1',
        # 'Referer': 'http://119.145.67.59/(bvqgth2ocwwvvv2ku4tifd2t)/xs_main.aspx?xh='+studentid,
        # 'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        }
    result = basecurl(url, postdata, headers_data)
    if result['status'] != 1:
        logger("选课页面打开失败 00")
        ret = {"status":0, "desc":"选课页面打开失败 00", "error":result['desc']}
    else:
        # 判断教务系统是否重启
        temp = is_jw_restart(result['getstr'])
        if temp['status'] != 1:
            raise FError("抛出教务系统重启的异常")

        p1 = r'可选课程' # 这是我们写的正则表达式
        pattern1 = re.compile(p1) # 正则表达式编译
        matcher1 = re.search(pattern1, result['getstr']) # 正则表达式查询
        if matcher1 == None:
            logger("选课页面打开失败 01")
            logger(result['getstr'])
            ret = {"status":-1, "desc":"选课页面打开失败 01", "getstr":result['getstr']}
        else:
            logger("选课页面打开成功")
            ret = {"status":1, "desc":"选课页面打开成功", "getstr":result['getstr']}
    return ret

# 搜索目标课程
# 如果成功搜索到目标课程返回选课的postdata
# 如果失败返回显示200条记录的postdata
def srarch_tag_class(result, tagclass, teacher = "", classtime = "", classcode = ""):

    # 抓取这个字段dpkcmcGrid%3AtxtPageSize的值
    dpkcmcGridAtxtPageSize = re.findall(r'<input name="dpkcmcGrid:txtPageSize" type="text" value="(.*)" onchange="(.*)" language="javascript" id="dpkcmcGrid_txtPageSize" class="width30 text_nor" />', result, re.I)
    # 抓取选课表格
    xuanketable = re.findall(r'<table class="datelist " cellspacing="0" cellpadding="3" border="0" id="kcmcGrid" width="100%">[\s\S]*?<\/table>', result, re.I)
    # print(xuanketable[0])
    # 清除html标签的属性
    parser = MyHTMLParser2()
    parser.feed(xuanketable[0])
    # print(parser.age)
    # 抓取tr标签
    xuanketabletr = re.findall(r'<tr>[\s\S]*?</tr>', parser.age,re.I)
    # print(xuanketabletr)
    # 抓取td标签
    xuanketabletd=[[0 for col in range(18)] for row in range(int(dpkcmcGridAtxtPageSize[0][0])+1)]
    for i in range(0, len(xuanketabletr)):
        xuanketabletd[i] = re.findall(r'<td>[\s\S]*?</td>', xuanketabletr[i],re.I)
    # print(xuanketabletd)
    # exit()
    # 抓取隐藏字段
    VIEWSTATE =re.findall(r'<input type="hidden" name="__VIEWSTATE" value="(.*?)" />', result, re.I)

    # 0多选框 1预定教材 2课程名称 3课程代码 4教师名称 5上课时间
    # 搜索目标课程
    tagflg = 0
    for i in range(0, len(xuanketabletr)):
        # print(xuanketabletd[i])
        # print(xuanketabletd[i][2])
        # 匹配课程名称
        pattern1 = re.compile(tagclass)
        matcher1 = re.search(pattern1,xuanketabletd[i][2])
        if matcher1 != None:
            # 匹配教师名称
            if teacher != "":
                if "<td><a>" + teacher + "</a></td>" != xuanketabletd[i][4]:
                    continue
            # 匹配上课时间
            if classtime != "":
                pattern1 = re.compile(classtime)#同样是编译
                matcher1 = re.search(pattern1,xuanketabletd[i][5])#同样是查询
                if matcher1 == None:
                    continue
            tagflg = 1
            tagclassnumber = i + 1
            logger(xuanketabletd[i][2] + xuanketabletd[i][4] + xuanketabletd[i][5])
            break
    if (tagflg == 1):
        logger("目标课程搜索成功")

        # 拼接选课的post数据
        postdata =  parse.urlencode([
                        ('__EVENTTARGET', "dpkcmcGrid%3AtxtPageSize"),
                        ('__EVENTARGUMENT', ""),
                        ('__VIEWSTATE', VIEWSTATE[0]),
                    ])
        for i in range(2, int(dpkcmcGridAtxtPageSize[0][0])+2):
            if (i == tagclassnumber):
                postdata = postdata + '&kcmcGrid%3A_ctl' + str(i) +'%3Axk=on'
            postdata = postdata + '&kcmcGrid%3A_ctl' + str(i) +'%3Ajcnr=%7C%7C%7C'
        postdata = postdata + '&dpkcmcGrid%3AtxtChoosePage=1&dpkcmcGrid%3AtxtPageSize=' + dpkcmcGridAtxtPageSize[0][0] + '&Button1=++%CC%E1%BD%BB++'
        ret = {"status":1, "postdata":postdata}
    else:
        logger("目标课程搜索失败")
        logger("发送每页显示200条记录的请求")

        # 拼接每页显示200条记录的post字段
        postdata =  parse.urlencode([
                        ('__EVENTTARGET', "dpkcmcGrid%3AtxtPageSize"),
                        ('__EVENTARGUMENT', ""),
                        ('__VIEWSTATE', VIEWSTATE[0]),
                    ])

        postdata = postdata + '&ddl_kcxz=&ddl_ywyl=%D3%D0&ddl_kcgs=&ddl_xqbs=1&ddl_sksj=&TextBox1='
        for i in range(2, int(dpkcmcGridAtxtPageSize[0][0])+2):
            postdata = postdata + '&kcmcGrid%3A_ctl' + str(i) +'%3Ajcnr=%7C%7C%7C'
        postdata = postdata + '&dpkcmcGrid%3AtxtChoosePage=1&dpkcmcGrid%3AtxtPageSize=' + str(200)
        ret = {"status":0, "postdata":postdata}
    return ret

# 检测是否已选课
# 如果有则返回1，没有则返回0
def check_tag_class(result, tagclass, taglen, teacher = "", classtime = ""):
    # 抓取已选课的表格
    yixuanketable = re.findall(r'<table class="datelist" cellspacing="0" cellpadding="3" border="0" id="DataGrid2" width="100%">[\s\S]*?</table>', result, re.I)
    # 清除html标签的属性
    parser = MyHTMLParser()
    parser.feed(yixuanketable[0])
    # 抓取tr标签
    yixuanketabletr = re.findall(r'<tr>[\s\S]*?</tr>', parser.age,re.I)
    # print(len(yixuanketabletr))
    # 抓取td标签
    yixuanketabletd=[[0 for col in range(18)] for row in range(len(yixuanketabletr))]
    for i in range(0, len(yixuanketabletr)):
        yixuanketabletd[i] = re.findall(r'<td>[\s\S]*?</td>', yixuanketabletr[i],re.I)
    # 0课程名称 1教师姓名 6上课时间
    yitagflg = 0
    for i in range(0, len(yixuanketabletr)):
        # print(yixuanketabletd[i])
        # print(xuanketabletd[i][2])
        # 匹配课程名称
        pattern1 = re.compile(tagclass) # 同样是编译
        matcher1 = re.search(pattern1,yixuanketabletd[i][0]) # 同样是查询
        if matcher1 != None:
            # 匹配教师名称
            if teacher != "":
                if "<td>" + teacher + "</td>" != yixuanketabletd[i][1]:
                    continue
            # 匹配上课时间
            if classtime != "":
                pattern1 = re.compile(classtime) # 同样是编译
                matcher1 = re.search(pattern1,yixuanketabletd[i][1]) # 同样是查询
                if matcher1 == None:
                    continue
            logger(yixuanketabletd[i][0] + yixuanketabletd[i][1] + yixuanketabletd[i][1])
            yitagflg = 1
            break
    if (yitagflg == 1):
        desc = "目标课程在已选课的表格中搜索到"
        logger(desc)
        ret = {"status":1, "desc":desc, "yixuanketabletr":yixuanketabletr, "yixuanketabletd":yixuanketabletd, "yixuanketabletdlen":len(yixuanketabletr)}
    else:
        desc = "目标课程在已选课的表格中搜索不到"
        # taglen = int(taglen)
        if taglen == -1:
            desc = desc + "，未选课 不知道选课程的数量"
            ret = {"status":0, "desc":desc, "yixuanketabletr":yixuanketabletr, "yixuanketabletd":yixuanketabletd, "yixuanketabletdlen":len(yixuanketabletr)}
        else:
            if len(yixuanketabletr) - 1 > taglen:
                desc = desc + "，已选课"
                ret = {"status":-1, "desc":desc, "yixuanketabletr":yixuanketabletr, "yixuanketabletd":yixuanketabletd, "yixuanketabletdlen":len(yixuanketabletr)}
            else:
                desc = desc + "，未选课"
                ret = {"status":0, "desc":desc, "yixuanketabletr":yixuanketabletr, "yixuanketabletd":yixuanketabletd, "yixuanketabletdlen":len(yixuanketabletr)}
        logger(desc)
    return ret

# post选课数据
def post_xuenke(url, studentid, postdata, tagclass, taglen, teacher, classtime):
    logger("发送选课的post数据")
    # post选课数据
    result = open_xuanke(url, studentid, postdata)
    while result['status'] != 1:
        logger("发送选课的post数据失败，正在重试")
        result = open_xuanke(url, studentid, postdata)
        return
    logger("发送选课的post数据成功")
    # 检测是否已选课
    result = check_tag_class(result['getstr'], tagclass, taglen, teacher, classtime)
    if result['status'] == 1:
        # 成功选到目标课程
        desc = "成功选到目标课程"
        logger(desc)
        xuankefinish(studentid, tagclass, teacher, classtime, desc, result['yixuanketabletr'])
    elif result['status'] == -1:
        # 已选课,不过所选课程貌似不是目标课程
        logger("已选课,不过所选课程貌似不是目标课程")
        xuankefinish(studentid, tagclass, teacher, classtime, result['desc'], result['yixuanketabletr'])
    elif result['status'] == 0:
        # 已经发送选课请求，但貌似没有成功，正在重试
        logger("已经发送选课请求，但貌似没有成功，正在重试")
        xuanke(url, studentid, tagclass, teacher, classtime, taglen)
        # xuankefinish(studentid, tagclass, teacher, classtime, result['desc'], result['yixuanketabletr'])

# 选课结束时调用的函数
def xuankefinish(studentid, tagclass, teacher, classtime, desc, getstr = ""):
    # textstr = desc + '\t' + studentid + "-" + tagclass + "-" + teacher + "-" + classtime + '\t' + str(getstr)
    logger(desc + "\n" + str(getstr))

    textstr = desc + '\t' + studentid + "-" + tagclass + "-" + teacher
    filename = desc
    filename += '-'
    filename += studentid
    filename += '-'
    filename += ''.join(random.sample(string.ascii_letters + string.digits, 8))
    batcmd = 'echo ' + textstr + ' > ' + filename + '.txt'
    os.system(batcmd)

    # 关闭同一个学号的选课进程
    os.system('taskkill /f /fi "windowtitle eq ' + studentid + '*" & taskkill /f /fi "windowtitle eq ' + studentid + '*"')

    # os.system("pause")
    exit()

# url       = "http://119.145.67.59:8889/(4viuo2ulgajodxqsffgias55)/"
# studentid = ""     # 学号
# password  = ""      # 密码
# tagclass  = "健美操"         # 课程名称
# teacher   = "陈泉宇"         # 教师姓名
# classtime = "周五第7,8节"    # 上课时间
# taglen    = 0               # 已选修课的数量
# 选课主函数
def xuanke(url, studentid, tagclass, teacher, classtime, taglen):
    # 打开选课页面
    result = open_xuanke(url, studentid)
    if result['status'] != 1:
        # 选课页面打开失败
        # xuanke(url, studentid, tagclass, teacher, classtime, taglen)
        logger(result['desc'])
        ret = {"status":0, "desc":result['desc']}
        return ret
    getstr = result['getstr']
    # 检测是否已选课
    result = check_tag_class(getstr, tagclass, taglen, teacher, classtime)
    if result['status'] == 1 or result['status'] == -1:
        # 已选课
        xuankefinish(studentid, tagclass, teacher, classtime, result['desc'], result['yixuanketabletr'])

    # 搜索目标课程
    result = srarch_tag_class(getstr, tagclass, teacher, classtime)
    if result['status'] == 1:
        # 搜索到目标课程，post选课数据
        post_xuenke(url, studentid, result['postdata'], tagclass, taglen, teacher, classtime)
    else:
        # 搜索不到目标课程，post一页显示200条记录的数据
        result = open_xuanke(url, studentid, result['postdata'])
        # 搜索目标课程
        result = srarch_tag_class(result['getstr'], tagclass, teacher, classtime)
        if result['status'] == 1:
            # 搜索到目标课程，post选课数据
            post_xuenke(url, studentid, result['postdata'], tagclass, taglen, teacher, classtime)
        else:
            desc = "目标课程不存在，可能已经选完了"
            logger(desc)
            xuankefinish(studentid, tagclass, teacher, classtime, desc)

if __name__ == '__main__':
    dev = False
    if dev != True:
        if len(sys.argv) != 9 or \
            sys.argv[1].strip() == '' or \
            sys.argv[2].strip() == '' or \
            sys.argv[3].strip() == '' or \
            sys.argv[4].strip() == '' or \
            sys.argv[5].strip() == '' or \
            sys.argv[6].strip() == '' or \
            sys.argv[7].strip() == '' or \
            sys.argv[8].strip() == '':
            print("命令行参数错误")
            exit()

        ipaddress = sys.argv[1] # ip地址
        port      = sys.argv[2] # 端口
        studentid = sys.argv[3] # 学号
        password  = sys.argv[4] # 密码
        tagclass  = sys.argv[5] # 课程名称
        teacher   = sys.argv[6] # 教师姓名
        classtime = sys.argv[7] # 上课时间
        taglen    = sys.argv[8] # 已选修课的数量

    else:
        ipaddress = "119.145.67.59" # ip地址
        port      = "80"            # 端口
        studentid = "417070512"     # 学号
        password  = "x111111"      # 密码
        tagclass  = "中医养生与保健"         # 课程名称
        teacher   = "汪丹"         # 教师姓名    陈昌盛
        classtime = "周一第7,8节{第4-18周|双周}"    # 上课时间    周五第7,8节    周一第7,8节{第4-18周|双周}
        taglen    = "NULL"               # 已选修的课的数量

        print("dev")
    # exit()

    init(ipaddress, port, studentid, password, tagclass, teacher, classtime, taglen)

    if teacher == "NULL":
        teacher = ""
    if classtime == "NULL":
        classtime = ""
    if taglen == "NULL":
        taglen = "-1"
    taglen = int(taglen)

    while 1:
        # 登录
        result = {"status": -1}
        while result['status'] != 1:
            result = denglu(ipaddress, port, studentid, password)
        try:
            # 选课
            url = ipaddress + ":" + port + "/(" + result['sessionid'] + ")/"
            result = {"status": 0}
            while result['status'] == 0:
                result = xuanke(url, studentid, tagclass, teacher, classtime, taglen)
        except FError as e: # 捕获教务系统重启异常，重新开始登录
            print(e)
            continue
    # os.system("pause")
