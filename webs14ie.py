from urllib import request, parse
import re
import os
import threading
import time
import sys

def print_all(module_):
  modulelist = dir(module_)
  length = len(modulelist)
  for i in range(0,length,1):
    print (module_,modulelist[i])

def basecurl(url, login_data = ""):
    try:
        if login_data.strip() == '':
            req = request.Request(url)
        else:
            print(login_data)
            req = request.Request(url, data=login_data.encode('utf-8'))
        u = request.urlopen(req)
        if u.status != 200:
            result = 0
        else:
            # with u as f:
            #     result = f.read().decode('gb18030')
            result = u
    except BaseException as e:
        result = 0
    return result


def xuankecurl(ipaddress, port, studentid, password):
    protocol = 'http://'
    # ipaddress = '119.145.67.5'
    # port = '8889'
    # port = '80'
    # sessionid = '5ltzxyqmv5rsby45ksiyucyg'
    # host = protocol + ipaddress + ':' + port + '/' + '(' + sessionid +')' + '/'
    host = protocol + ipaddress + ':' + port + '/'
    url = host + 'default_vsso.aspx'
    result = basecurl(url)
    
    if result != 0:
        # print(result)
        print("登录页面打开成功")
        m = re.match('.*\((.*)\).*', result.geturl())
        sessionid = m.group(1)

        host = protocol + ipaddress + ':' + port + '/' + '(' + sessionid +')' + '/'
        url = host + 'default_vsso.aspx'
        login_data = parse.urlencode([
            ('TextBox1', studentid),
            ('TextBox2', password),
            ('RadioButtonList1_2', '%D1%A7%C9%FA'),
            ('Button1', ''),
        ])
        result = basecurl(url, login_data)
        if result != 0:
            # print(result)
            print("登录参数发送成功")
            with result as f:
                resultstr = f.read().decode('gb18030')
            # print(resultstr)
            key = resultstr#这是源文本
            p1 = r'评价完后请完善个人信息和修改登入密码'#这是我们写的正则表达式
            pattern1 = re.compile(p1)#同样是编译
            matcher1 = re.search(pattern1,key)#同样是查询
            if matcher1 != None:
                print("登录成功")
                url = host +'xf_xsqxxxk.aspx?xh=' + studentid
                # batcmd = '%windir%\explorer.exe shell:Appsfolder\Microsoft.MicrosoftEdge_8wekyb3d8bbwe!MicrosoftEdge open="' + url + '"' # 使用edge浏览器
                batcmd = 'start iexplore.exe "' + url + '"' # 使用ie浏览器
                print(batcmd)
                for i in range(3):
                    os.system(batcmd)
                    time.sleep(4)
            else:
                print("登录失败")
        else:
            print("登录参数发送失败")
    else:
        print("登录页面打开失败")
for i in range(0, len(sys.argv)):
    print("参数", i, sys.argv[i])
if len(sys.argv) != 5 or sys.argv[1].strip() == '' or sys.argv[2].strip() == '' or sys.argv[3].strip() == '' or sys.argv[4].strip() == '':
    print("命令行参数错误")
    quit()

ipaddress = sys.argv[1]
port = sys.argv[2]
studentid = sys.argv[3]
password = sys.argv[4]

xuankecurl(ipaddress, port, studentid, password)
os.system("pause")