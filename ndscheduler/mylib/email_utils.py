# -*- coding:utf-8 -*-  

'''
Created on 2017-10-07
author: qcyfred
'''

import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.header import Header
import os


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
    smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)
    smtp.login(username, password)
    smtp.sendmail(sender, receivers, msg.as_string())
    smtp.quit()

