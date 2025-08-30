#!/usr/bin/python3
# coding=utf-8
###################################################################
#           ____     _     _ __  __                 
#          / __/__  (_)___(_) /_/ /  ___  ___  ___ _
#         _\ \/ _ \/ / __/ / __/ /__/ _ \/ _ \/ _ `/
#        /___/ .__/_/_/ /_/\__/____/\___/_//_/\_, / 
#           /_/                              /___/  
# Copyright (c) 2024 Chongqing Spiritlong Technology Co., Ltd.
# All rights reserved.  
# @author	arthuryang
# @brief	字符串相关工具，包括json
#
###################################################################  

import	datetime
import	re
import	os
import	json
import	decimal

## 判断一个字符串是不是浮点数
def is_float(s):
	try:
		float(s)
		# 浮点数
		return True
	except ValueError:
		pass

## 字符串tab对齐
# 	list_data	数据
#	list_align	对齐字符串
# 	length_tab	TAB空格数
# list	

def list_content_align_tab(list_data, list_align, length_tab=8):
        list_content    = []
        list_data_temp  = list_data
        for align in list_align:
                # 字符串分割
                list_list_data  = []
                for line in list_data_temp:
                        list_list_data.append(line.strip().split(align))

                # 最小列数
                list_length_tab = []
                list_length     = len(min(list_list_data, key=len))
                
                # 每列最大长度的tab数
                for i in range(list_length):
                        list_length_tab.append(int(len(max(list(zip(*list_list_data))[i], key=len))/length_tab+1))

                # 数据拼接
                for lines in list_list_data:
                        row     = ""
                        for i in range(list_length):
                                line            = lines[i]
                                row             = row + line
                                
                                for n in range(int(len(line)/length_tab), list_length_tab[i]):
                                        row    = row+"\t"

                                if i<list_length-1:
                                        row     = row+align
                                
                        list_content.append(row + "\n")
                list_data_temp  = list_content

        return list_content

### JSON格式化日期和Decimal
class SpiritLongJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime.datetime):
			return obj.strftime('%Y-%m-%d %H:%M:%S')
		elif isinstance(obj, datetime.date):
			return obj.strftime('%Y-%m-%d')
		elif isinstance(obj, decimal.Decimal):
			return str(obj).rstrip("0").rstrip(".")
		else:
			return json.JSONEncoder.default(self, obj) 
		
## 对象转json字符串
#	object_data	数据
#	default		默认值
# string
def object_to_json(object_data, default=""):
	try:
		return json.dumps(object_data, ensure_ascii=False, cls=SpiritLongJsonEncoder)
	except Exception as ex:
		return default
	
## json字符串转对象
#	json_string	数据
#	default		默认值
# object
def json_to_object(json_string, default={}):
	try:
		return json.loads(json_string, strict=False)
	except Exception as ex:
		return default

## json转为bytes
#	json_data	json对象
# b''
def json_to_bytes(json_data):
	return bytes(json_data, encoding='utf8')

# 调试/测试代码
if __name__ == '__main__':
	pass

