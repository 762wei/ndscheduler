#-*- coding: utf-8 -*-
import socket
from urllib import quote
from urllib import unquote
import os
import threading
import ctypes
import datetime
import json


# 获取主机在本地局域网中的IP
def get_lan_ip(prefix = '192.'):

    print u'正在获取主机在本地局域网中的IP...'

    localIP = socket.gethostbyname(socket.gethostname())#得到本地ip
    ipList = socket.gethostbyname_ex(socket.gethostname())
    for i in ipList:
        # if i != localIP:
        if len(i) > 0 and isinstance(i, list):
            for ii in i :
                if ii.startswith(prefix) and ii != localIP:
                    print "LAN IP:%s"%ii
                    return ii

    return 'unknown'


# socket client端
def send_msg(ip_addr, port, msg):

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ip_addr, port))
        client.settimeout(5)
        client.sendall(quote(msg).encode('utf-8'))
        
    except Exception as e:
        print e
    finally:
        client.close()


# socket server端
def setup_socket_server(local_port = 43218, need_hide_window = False):

    local_ip = get_lan_ip()  # 配置socket server绑定的本地IP
    print 'server starting...'

    if need_hide_window:     
        # 隐藏窗口
        whnd = ctypes.windll.kernel32.GetConsoleWindow()    
        if whnd != 0:    
            ctypes.windll.user32.ShowWindow(whnd, 0)    
            ctypes.windll.kernel32.CloseHandle(whnd)  

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((local_ip, local_port))
    server.listen(5)

    # 应该在外面用一个配置文件来指定白名单的IP列表
    # 只响应白名单中的计算机发来的任务
    # admin_filter的key()
    admin_filter = {}
    admin_filter['192.168.36.252'] = {'exe'}
    admin_filter['192.168.33.113'] = {'exe'}
    admin_filter['192.168.35.186'] = {'exe'}
    admin_filter['127.0.0.1'] = {'exe'}

    # 启动py程序
    def start_py_prog(msg):
        
        params = json.loads(msg)

        py_dir = params['remote_py_dir']
        py_file = params['remote_py_file']

        command = '''start cmd /k "cd {py_dir} & python {py_file} {extra_param}"'''
        param_json_str = json.dumps(params)
        param_json_str = param_json_str.replace('"','\\\\"').replace(' ','')
        command = command.format(**{'py_dir':py_dir, 'py_file': py_file, 'extra_param': param_json_str})
        
        print command
        os.system(command)


    while 1:
        
        conn, addr = server.accept()
        msg = unquote(conn.recv(1024).decode('utf-8'))
        
        peer_name = conn.getpeername() # peer_name是个tuple，peer_name[0]是ip，peer_name[1]是端口号
        now_dt = str(datetime.datetime.now())
        print u'%s, visitor: %s:%s'%(now_dt, peer_name[0],peer_name[1]) # , sock_name

        # 管理员权限验证
        if True:
        # if peer_name[0] in admin_filter.keys():
            # # print msg, 'quit'==msg, u'quit'==msg, u'quit'==str(msg), 'quit' == str(msg)
            # if '"quit"' == msg:
            #     conn.close()
            #     exit(0)

            t = threading.Thread(target=start_py_prog,args=(msg,))
            t.start()

