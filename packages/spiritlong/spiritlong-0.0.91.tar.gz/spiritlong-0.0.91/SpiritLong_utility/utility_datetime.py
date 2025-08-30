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
# @brief	日期时间相关工具
#
###################################################################  

import datetime
import	re
import	os

## 根据日期时间字符串返回datetime对象或None
# 注意只支持2000-01-01之后的时间
def datetime_string_parse(datetime_string):
	# 对于传入datetime对象的情况，直接返回
	if isinstance(datetime_string, datetime.datetime):
		return datetime_string
	
	# 得要让第一次能进去，后面在成功赋值之后都进不去
	t	= datetime.datetime(1970,1,1)
	def try_parse(tt, format_string):
		try:
			if tt is None or tt<datetime.datetime(2000,1,1):
				t	= datetime.datetime.strptime(datetime_string, format_string)
			else:
				t	= tt
		except:
			t	= None
		return t
	
	# 有恶心的excel导入只有时和分的奇葩（ALI）
	t	= try_parse(t, "%Y-%m-%d %H:%M")
	t	= try_parse(t, "%Y-%m-%d %H:%M:%S")
	t	= try_parse(t, "%Y-%m-%d")
	t	= try_parse(t, "%Y-%m")
	# 注意此处要先检查%Y%m，否则会把202412识别成2024-01-02
	t	= try_parse(t, "%Y%m")
	t	= try_parse(t, "%Y%m%d")
	t	= try_parse(t, "%Y/%m/%d %H:%M:%S")
	t	= try_parse(t, "%Y/%m")
	t	= try_parse(t, "%Y/%m/%d")	
	t	= try_parse(t, "%Y年%m月")
	t	= try_parse(t, "%Y年%m月%d日")
	
	return t

## 输入日期时间的解析
#	date		None将返回当前日期；datetime.datetime类型；字符串则必须以yyyy-MM-dd开头
#	last_day	True则返回当月最后一天的0点0分
#	last_second	True则返回当月最后一天的23点59分59秒
# 返回字典
#		'year'			
# 		'month'			
# 		'day'			
# 		'datetime'		
# 		'date_string'		
# 		'time_string'		
# 		'datetime_string'
def input_date(date=None, last_day=False, last_second=False):
	# 先转换
	date	= datetime_string_parse(str(date)) if date is not None else datetime.datetime.now()
	
	# 转换不成功直接返回
	if not date:
		return date
	
	year	= date.year
	month	= date.month
	if last_day or last_second:
		# 设置为当月最后一天的23:59:59
		t	= date.replace(day=28) + datetime.timedelta(days=4)
		day	= (t-datetime.timedelta(days=t.day)).day
		if last_second:
			date	= date.replace(day=day, hour=23, minute=59, second=59)
		else:
			date	= date.replace(day=day, hour=0, minute=0, second=0)
	else:
		day	= date.day

	return {
		'year'				: year,
		'month'				: month, 
		'day'				: day,
		'datetime'			: date,
		'date_string'			: date.strftime('%Y-%m-%d'),
		'time_string'			: date.strftime('%H-%M-%S'),
		'datetime_string'		: date.strftime('%Y-%m-%d %H:%M:%S'),
		'date_string_chinese'		: date.strftime('%Y年%m月%d日'),
	}

# 调试/测试代码
if __name__ == '__main__':
	# print('fdsfds')
	pass
