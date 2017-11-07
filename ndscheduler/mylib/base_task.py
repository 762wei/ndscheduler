# -*- coding:utf-8 -*-  

'''
Created on 2017-08-17
@author: Wang Haiyang
'''

import os
import socket
from urllib import quote
import json
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.header import Header
import sys, os


def str_process(string):
    try:
        string = string.decode('utf-8').encode('gbk')
    except Exception as e:
        pass
    return string


def get_params(params):
    exefiles = params.get("exefile_para")#a list of string
    infiles = params.get("infile_para")#a list of string
    email_para = params.get("email_para")#a dictionary
    if email_para==None:
        email_para = {}
    receivers = email_para.get("receivers")#a list of string
    subject = email_para.get("subject")#a string
    content = email_para.get("content")#a string
    images = email_para.get("images")#a list of string
    attachments = email_para.get("attachments")#a list of string
    return [exefiles, receivers, subject, content, images, attachments, infiles]


def run_script(exefile, new_window=True):
    exe_dir, exe_file = os.path.split(exefile)
    postfix = exe_file.split(' ')[0].split('.')[1]
    if new_window:
        if postfix=='py': #a python file
            status = os.system('start cmd /k "cd %s & python %s"' % (exe_dir, exe_file))
            return status
        elif postfix=='bat': #a bat file
            status = os.system('start cmd /k "cd %s & %s"' % (exe_dir, exe_file))
            return status
    else:
        if postfix=='py': #a python file
            status = os.system('cd %s & python %s' % (exe_dir, exe_file))
            return status
        elif postfix=='bat': #a bat file
            status = os.system('cd %s & %s' % (exe_dir, exe_file))
            return status
    return 1


'''send emails ususally after run the scripts'''
def send_email(receivers, subject, content, images, attachments, email_info_file="config/email_info.json"):

    email_file = open(email_info_file)
    emai_info = json.load(email_file)
    sender = emai_info["sender"]
    smtpserver = emai_info["smtpserver"]
    username = emai_info["username"]
    password = emai_info["password"]
 
    #add the title, from and to
    msg = MIMEMultipart('related')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['from'] = sender
    msg['to'] = ','.join(receivers)

    #add the content into the email
    msgAlternative = MIMEMultipart('alternative')
    msg.attach(msgAlternative)

    mail_msg = ''
    if content!='':
        mail_msg += '{0}{1}{2}'.format('<p>', content, '</p>\n')

    count = 0
    for image in images:
        if image.find('.')!=-1:#it's a file
             mail_msg += '<p><img src="cid:image%d"></p>' % (count)
             count += 1
        else:#it's a dir
            files = os.listdir(image)
            for file in files:
                mail_msg += '<p><img src="cid:image%d"></p>' % (count)
                count += 1
    msgAlternative.attach(MIMEText(mail_msg, 'html', 'utf-8'))


    #add the images into the email
    count = 0
    for image in images:
        if image.find('.')!=-1:#it's a file
            msgImage = MIMEImage(open(image, 'rb').read())
            msgImage.add_header('Content-ID', '<image' + str(count) + '>')
            msg.attach(msgImage)
            count += 1
        else:#it's a dir
            files = os.listdir(image)
            for file in files:
                msgImage = MIMEImage(open('{0}\{1}'.format(image,file), 'rb').read())
                msgImage.add_header('Content-ID', '<image' + str(count) + '>')
                msg.attach(msgImage)
                count += 1


    #add the attachments into the email
    for attachment in attachments:
        if attachment.find('.')!=-1:#it's a file
            att = MIMEApplication(open(attachment, 'rb').read())
            att.add_header('Content-Disposition', 'attachment', filename=os.path.split(attachment)[1])
            msg.attach(att)
        else:#it's a dir
            files = os.listdir(attachment)
            for file in files:
                att = MIMEApplication(open('{0}\{1}'.format(attachment,file), 'rb').read())
                att.add_header('Content-Disposition', 'attachment', filename=file)
                msg.attach(att)


    #send email to receivers
    # smtp = smtplib.SMTP()
    # smtp.connect('smtp.163.com')
    smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)
    smtp.login(username, password)
    smtp.sendmail(sender, receivers, msg.as_string())
    smtp.quit()