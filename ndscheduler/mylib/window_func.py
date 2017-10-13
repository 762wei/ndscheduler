# -*- coding:utf-8 -*-  
#Author: Wang Haiyang
#Aug 18, 2017

import os
import pandas as pd
import time


def read_tasks(params='''cmdow /T /P /F /B'''):
	matrix = []
	tasks = os.popen(params).readlines()
	fields = "Handle  Lev  Pid -Window status-   Left    Top  Width Height Image                Caption".strip()
	columns = ['Handle', 'Lev', 'Pid', '-Window status-', 'Left', 'Top', 'Width', 'Height', 'Image', 'Caption']
	for i in xrange(0, len(tasks)):
		handle = tasks[i][fields.find('Handle'):fields.find('Lev')+1].strip()
		lev = tasks[i][fields.find('Lev'):fields.find('Lev')+3].strip()
		pid = tasks[i][fields.find('Lev')+3:fields.find('Pid')+3].strip()
		window_status = tasks[i][fields.find('Pid')+3:fields.find('-Window status-')+15].strip()
		left = tasks[i][fields.find('-Window status-')+15+1:fields.find('Left')+4].strip()
		top = tasks[i][fields.find('Left')+4:fields.find('Top')+3].strip()
		width = tasks[i][fields.find('Top')+3:fields.find('Width')+5].strip()
		height = tasks[i][fields.find('Width')+5:fields.find('Height')+6].strip()
		image = tasks[i][fields.find('Image'):fields.find('Caption')].strip()
		caption = tasks[i][fields.find('Caption'):-1].strip()
		matrix.append([handle, lev, pid, window_status, left, top, width, height, image, caption])
	tasks_df = pd.DataFrame(matrix, columns=columns)
	return tasks_df


def list_tasks():
	os.system('''cmdow /T /P /F''')


def get_handles(params='''cmdow /T /P /F /B'''):
	tasks_df = read_tasks(params)
	return tasks_df['Handle'].values


def get_images(params='''cmdow /T /P /F /B'''):
	tasks_df = read_tasks(params)
	return tasks_df['Image'].values


def get_handle_by_pid(pid):
	tasks_df = read_tasks()
	pid = str(pid)
	return  tasks_df[tasks_df.Pid == pid]['Handle'].values[0]


def get_handle_by_image(image):
	tasks_df = read_tasks()
	return tasks_df[tasks_df.Image == image]['Handle'].values[0]


def get_handle_by_wname(wname):
	tasks_df = read_tasks()
	wname = wname.decode('utf-8').encode('gbk')
	return tasks_df[tasks_df.Caption == wname]['Handle'].values[0]


def set_window_specify(handle, left, top, width, height):
	handle = str(handle)
	restore = '''cmdow %s /RES''' % (handle)
	os.system(restore)
	mov = '''cmdow %s /MOV %d %d''' % (handle, left, top)
	os.system(mov)
	size = '''cmdow %s /SIZ %d %d''' % (handle, width, height)
	os.system(size)


def set_window_max(handle):
	handle = str(handle)
	os.system('''cmdow %s /MAX''' % (handle))


def start_window(program, timeout=15):
	if program.find("HsOrganClient.exe")!=-1:#Hsclient
		params = '''cmdow /P /F | findstr 资产管理综合业务平台'''.decode('utf-8').encode('gbk')	
	elif program.find("WindNET.exe")!=-1:#Wind
		params = '''cmdow /P /F | findstr Wind资讯金融终端..浦明'''.decode('utf-8').encode('gbk')	
	else:
		params = '''cmdow /T /P /F /B'''
	old_handles = set(get_handles(params))
	old_time = time.time()
	start_cmd = '''start %s''' % (program)
	os.system(start_cmd)
	while True:
		handles = set(get_handles(params))
		if handles!=old_handles:
			if program.find("WindNET.exe")!=-1:#Wind:
				if get_images(params)[0]!="wmain":#not wmain
					print get_images(params)[0]
					continue
			break
		if time.time() - old_time >= timeout:
			print "Time out when excuting" + program
			return 
	handle = list(handles-old_handles)[0]
	return handle


def start_set_window(command):
	program = command[0]
	handle = start_window(program)
	if len(command)==1:#maximum
		set_window_max(handle)
	else:#specified
		[program, left, top, width, height] = command
		set_window_specify(handle, left, top, width, height)