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
import	unicodedata

## 判断一个字符串是不是浮点数
def is_float(s):
	try:
		float(s)
		# 浮点数
		return True
	except ValueError:
		pass

# 对UTF8字符串（中英文混合）计算显示长度，中文按两字符计算
def UTF8_string_length(s):
	length	= 0
	for c in s:
		# east_asian_width返回字符的类型，F和W都是占两个位置的（全角）
		length	+= 2 if unicodedata.east_asian_width(c) in 'FW' else 1
	return length

## 多行字符串按分隔字符串用tab对齐，适用于多行赋值/注释对齐
# 	list_data	多行数据，列表中每个元素是一行
#	seperators	分隔字符串列表，例如['=', '// ']
# 	TAB_length	TAB空格数
# 返回拼接好的多行字符串
def list_content_align_tab(list_data, seperators, TAB_length=8):
	# 把list_data按seperators分割成列表，每个元素对应一行是一个分割的各部分构成的子列表
	lines	= [[] for d in list_data]
	for seperator in seperators:
		# 字符串分割
		for i in range(len(list_data)):
			# 只分割一次
			parts	= list_data[i].split(seperator, maxsplit=1)
			# 分割是否成功都把第一个部分加进去
			lines[i].append(parts[0])
			# 分割成功则保留剩下的部分在list_data[i]，不成功则保留空字符串
			list_data[i]	= parts[1] if(len(parts)==2) else ''
	# 最后一个列要处理。lines的每个子列必定是一样长了
	lines	= [lines[i]+[list_data[i]] for i in range(len(lines))]
	
	# 计算每列的最大宽度
	column_lengths	= [max([UTF8_string_length(lines[i][j]) for i in range(len(lines))]) for j in range(len(lines[0]))]
	# 扩展到加上tab分隔后的列宽（按tab数）
	column_lengths	= [((int)(n/TAB_length)+1) for n in column_lengths]

	for i in range(len(lines)):
		# 逐行处理成输出的字符串
		line	= ''
		# 按分隔符数量来
		for j in range(len(seperators)):
			# 计算本行j列需要补的tab数
			column_align_tabs	= (int)((UTF8_string_length(lines[i][j]))/TAB_length)
			tabs	= column_lengths[j]-column_align_tabs
			line	+= lines[i][j]+'\t'*tabs
		# 注意要补上最后一个列
		lines[i]	= line+lines[i][len(seperators)]

	return lines

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

