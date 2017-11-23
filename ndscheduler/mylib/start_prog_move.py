# coding: utf-8

import os
import win32process
import win32event
from ctypes import *
from win32gui import *
from win32con import *
import time
import pandas as pd
import datetime
import window_name_utils
import threading

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi

def update_excel(path):
    while True:
        print u'更新软件启动信息表'
        global df # 软件启动信息表，全局变量，定时更新
        df = pd.read_excel(path)
        df['start_time'] = df['start_time'].astype(str)
        time.sleep(10 * 60) # 秒


def start_prog(path):

    global df
    df = pd.read_excel(path)
    df['start_time'] = df['start_time'].astype(str)

    while True:

        now_time_str = str(datetime.datetime.now().time()).split('.')[0]
        time.sleep(0.5)

        print '%s'%now_time_str

        df_to_start = df.query("start_time == @now_time_str")

        for i in range(len(df_to_start)):

            d = df_to_start.iloc[i,:].to_dict()

            x = int(d['x'])
            y = int(d['y'])
            dx = int(d['dx'])
            dy = int(d['dy'])

            si = win32process.STARTUPINFO()
            si.dwX, si.dwY = [x, y]
            xySize = [dx, dy]
            si.dwXSize, si.dwYSize = xySize
            si.dwFlags ^= STARTF_USEPOSITION | STARTF_USESIZE

            if pd.isnull(d['params']):
                cmd_line = u"""%s"""%d['path']
            else:
                cmd_line = u"""%s %s"""%(d['path'], d['params'])

            params = (None, cmd_line, None , None , 0 ,  16 , None , None ,si )
            hProcess, hThread, dwProcessId, dwThreadId = win32process.CreateProcess(*params)

            # 如果不是cmd程序，还要调用Move，否则就结束
            # # 新进程的时候，能得到pid，已经有进程了，得到的不是pid…
            print hProcess, hThread, dwProcessId, dwThreadId

            time.sleep(int(d['sleep_time']))

            if d['is_cmd'] == 'y':
                pass # 因为cmd可以启动时指定位置
            else:

                # 得到当前handle、pid、窗口名称的信息
                window_info_df = window_name_utils.get_window_info()

                if d['use_caption'] == 'n': # 用pid
                    hwnd = window_info_df.loc[window_info_df['pid']==dwProcessId, 'handle'].values[0]

                elif d['use_caption'] == 'y':

                    print u'通过窗口名称获得handle'
                    handles = window_info_df.loc[window_info_df['caption']==d['caption'], 'handle'].values

                    if len(handles) == 1: # 唯一标题，直接根据hwnd移动
                        hwnd = handles[0]

                    elif len(handles) > 1: # 标题名字有重复的，根据 createProcess 得到的pid， 再找handle， 移动
                        # 先假设这个pid只会有一个handle
                        hwnd = window_info_df.loc[window_info_df['pid']==dwProcessId, 'handle'].values[0]

                # ========
                ShowWindow(hwnd, SW_RESTORE)  # 1. 还原 # 有些窗口不能还原?!!!
                time.sleep(1)
                MoveWindow(hwnd, x, y, dx, dy, True)  # 2. 移动

                if d['need_max'] == 'y':
                    ShowWindow(hwnd, SW_MAXIMIZE)  # 最大化

def prog_run():
    path = u'软件启动信息.xlsx'
    # 每隔一段时间，刷新一次软件启动的信息...
    threads = []
    t1 = threading.Thread(target=update_excel, args=(path,))
    t2 = threading.Thread(target=start_prog, args=(path,))
    t1.start()
    t2.start()

if __name__ == '__main__':
    prog_run()
