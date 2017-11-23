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
                # if ii.startswith(prefix) and ii != localIP:
                if ii.startswith(prefix):
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


# ---   socket server端   ---

# 启动py程序
def start_py_prog(params):

    print u'执行py文件'
    remote_py_file_path = params['remote_py_file_path']

    command = '''start cmd /k " python {remote_py_file_path} {extra_param} && exit"'''
    param_json_str = json.dumps(params)
    param_json_str = param_json_str.replace('"','$')
    command = command.format(**{'remote_py_file_path': remote_py_file_path,
                                'extra_param': param_json_str})

    print command
    os.system(command)


# 处理wind行情订阅数据
def proc_wsq_data(params):
    print u'处理wind行情订阅数据'
    pass


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

    while 1:
        
        conn, addr = server.accept()
        msg = unquote(conn.recv(1024).decode('utf-8')) # json格式的str

        peer_name = conn.getpeername()  # peer_name是个tuple，peer_name[0]是ip，peer_name[1]是端口号
        now_dt = str(datetime.datetime.now())
        print u'%s, visitor: %s:%s' % (now_dt, peer_name[0], peer_name[1])  # , sock_name

        params = json.loads(msg)
        msg_type = params['msg_type']

        # 管理员权限验证
        if True: # if peer_name[0] in admin_filter.keys():
            # 1. 普通运行脚本的msg
            if 'run_py' == msg_type:
                t = threading.Thread(target=start_py_prog,args=(params,))
                t.start()
            # 2. 处理wind订阅的行情数据
            elif 'wsq_data' == msg_type:
                t = threading.Thread(target=proc_wsq_data, args=(params,))
                t.start()


if __name__ == '__main__':
    setup_socket_server(local_port = 43218, need_hide_window = True)
