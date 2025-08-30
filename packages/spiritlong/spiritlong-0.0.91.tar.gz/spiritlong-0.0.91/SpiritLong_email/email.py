#!/usr/bin/python3
# coding=utf-8
###################################################################
#           ____     _     _ __  __                 
#          / __/__  (_)___(_) /_/ /  ___  ___  ___ _
#         _\ \/ _ \/ / __/ / __/ /__/ _ \/ _ \/ _ `/
#        /___/ .__/_/_/ /_/\__/____/\___/_//_/\_, / 
#           /_/                              /___/  
# Copyright (c) 2025 Chongqing Spiritlong Technology Co., Ltd.
# All rights reserved.  
# @author	arthuryang
# @brief	邮件操作
#
###################################################################  

import	os
import	smtplib
from email.mime.text			import MIMEText
from email.mime.multipart		import MIMEMultipart
from email.mime.application		import MIMEApplication
from email.header			import Header


## 邮件类
class  SpiritLongEmail(object):
	## 初始化
	#	email_host		邮件服务器host
	#	email_port		邮件服务器端口
	#	email_user		登录用户
	#	email_password		登录密码
	# ''
	def __init__(self, email_host, email_port, email_user, email_password):
		self.email_host		= email_host
		self.email_port		= email_port
		self.email_user		= email_user
		self.email_password	= email_password

	## 发送邮件
	#	receiver	接收者，可为数组或单个邮件
	#	subject		标题
	#	content		内容
	#	attachments	附件文件地址列表
	# 返回是否发送成功True/False
	def send_mail(self, receiver, subject, content, attachments):
		# 邮件接收者列表
		receiver_list			= receiver if isinstance(receiver, list) else [receiver]

		# 邮件
		message				= MIMEMultipart()
		message['From']			= self.email_user
		message['To']			= ','.join(receiver_list)
		message['Subject']		= Header(subject, 'utf-8')
		message['Accept-Language']	= "zh-CN"
		message['Accept-Charset']	= "ISO-8859-1,utf-8"

		message.attach(MIMEText(content, 'html', 'utf-8'))

		# 添加附件
		for file in attachments:
			apart	= MIMEApplication(open(file, 'rb').read())
			apart.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
			message.attach(apart)
			
		# 发送邮件
		try:
			server	= smtplib.SMTP_SSL(self.email_host)
			server.connect(self.email_host, self.email_port)
			server.login(self.email_user, self.email_password)
			server.sendmail(self.email_user, receiver_list, message.as_string())
			server.quit()

			return True
		except Exception as ex:
			print(str(ex))

			return False
		
## 调试/测试代码
if __name__ == '__main__':
	EMAIL_HOST		= "smtp.exmail.qq.com"
	EMAIL_PORT		= 465
	EMAIL_USER		= "exon@spiritlong.com"
	EMAIL_PASSWORD		= "xxxxxx"

	# 调用库
	SL_email	= SpiritLongEmail(EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD)

	# 发送邮件
	SL_email.send_mail("exon@spiritlong.com", "测试邮件", "测试内容", ["__init__.py"])