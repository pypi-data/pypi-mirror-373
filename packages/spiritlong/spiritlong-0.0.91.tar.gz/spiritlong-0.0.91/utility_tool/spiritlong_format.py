###
#******************************************************************
# *           ____     _     _ __  __                 
# *          / __/__  (_)___(_) /_/ /  ___  ___  ___ _
# *         _\ \/ _ \/ / __/ / __/ /__/ _ \/ _ \/ _ `/
# *        /___/ .__/_/_/ /_/\__/____/\___/_//_/\_, / 
# *           /_/                              /___/  
# * Copyright (c) 2023 Chongqing Spiritlong Technology Co., Ltd.
# * All rights reserved.  
# * @author	shun
# * @brief	格式化输出工具函数
# *
# *****************************************************************/

import  json
import	time
import  base64
from    datetime	import date
from    datetime	import datetime
from    decimal 	import Decimal
from    json 	        import JSONEncoder

### JSON格式化日期和Decimal
class SpiritLongJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime):
			return obj.strftime('%Y-%m-%d %H:%M:%S')
		elif isinstance(obj, date):
			return obj.strftime('%Y-%m-%d')
		elif isinstance(obj, Decimal):
			return str(obj).rstrip("0").rstrip(".")
		else:
			return JSONEncoder.default(self, obj) 

## 格式化输出
#	code		代码
#	message		描述
#	data		数据
# {}
def format_error(code, message, data=None):
	return {
		"code"		: code,
		"message"	: message,
		"data"		: data
	}

## json转为bytes
#	json_data	json对象
# b''
def json_to_bytes(json_data):
	return bytes(json_data, encoding='utf8')

## json转字符串
#	json_data	json对象
# ''
def json_to_string(json_data):
	# 中文不转义
	return json.dumps(json_data, ensure_ascii=False)

## 字符串转json
#	json_data	json字符串
# object
def string_to_json(json_string):
	return json.loads(json_string)

## 格式化数据-成功
#	data		数据
# b''
def success(data=None):
	error		= format_error(0, '请求成功')
	error['data']	= data
	
	return json_to_bytes(json.dumps(error, ensure_ascii=False, cls=SpiritLongJsonEncoder))

## 格式化数据-失败
#	code		代码
#	message		描述
#	data		数据
# b''
def fail(message=None, code=500, data=None):
	# 0	请求成功
	# 400	TOKEN错误
	# 401	API不存在
	# 402	参数不存在
	# 500	自定义错误
	error	= format_error(500, '自定义错误')
	if code!=500:
		error['code']		= code
	
	if message is not None:
		error['message']	= message

	if data is not None:
		error['data']		= data
	
	return json_to_bytes(json.dumps(error))

## 字符串是否为空
#	data		数据
# bool
def is_none(data):
	if data==None or data=="None" or data=="" or len(str(data))==0:
		return True
	return False

## base64数据写入文件
#	data		base64格式数据
# 	file		文件名称，带路径
#
def base64_to_file(file, data):
	with open(file, 'wb') as f:
		f.write(base64.b64decode(data))

## 数组转元组格式字符串
#	list_data	数据
# 	is_number	内容是否是数字
# str
def list_to_touple_string(list_data, is_number=False):
	if is_number:
		return "(" + ','.join(str(i) for i in list_data) + ")"
	else:
		return "(" + ','.join('"'+str(i)+'"' for i in list_data) + ")"

## 数组字典提取指定KEY数据组成数组
#	list_dict	数据
# 	key		字典的key
# []
def list_dict_to_list(list_dict, key="ID"):
	if len(list_dict)<1 or key not in list_dict[0].keys():
		return []
	
	return [item[key] for item in list_dict]

## 数组字典提取指定KEY数据组成字典
#	list_dict	数据
# 	key_key		新字典的key在数组字典中的key
# 	key_value	新字典的value在数组字典中的key
# {}
def list_dict_to_dict(list_dict, key_key="ID", key_value="NAME"):
	if len(list_dict)<1 or key_key not in list_dict[0].keys():
		return {}
	
	return {item[key_key]:item[key_value] for item in list_dict}

## 获取浮点数
# 	data_string	数据
# float	
def format_float(data_string):
	try:
		return float(data_string)
	except Exception as ex:
		return 0
	
## 获取整数
# 	data_string	数据
# int	
def format_int(data_string):
	try:
		return int(data_string)
	except Exception as ex:
		return 0
	
## 获取日期和时间
# 	data_string	数据
# datetime
def format_datetime(data_string):
	try:
		return datetime.strptime(data_string, '%Y-%m-%d %H:%M:%S')
	except Exception as ex:
		return None
	
# 获取日期	
#  	data_string	数据
# datetime	
def format_date(data_string):
	try:
		return datetime.strptime(data_string,'%Y-%m-%d').date()
	except Exception as ex:
		return None

## 列表转元组字符串	如果列表长度大于1则返回元组，等于1则返回字符串
#	list_data	列表数据
# tuple/string
def list_to_tuple_string(list_data):
	if len(list_data) > 1:
		return tuple(list_data)
	if len(list_data)==1:
		if isinstance(list_data[0], (int, float)):
			return f'''({list_data[0]})'''
		else:
			return f'''("{list_data[0]}")'''
	return None

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

## 获取年月日
#	None
# 20230907
def get_string_date():
	return time.strftime('%Y%m%d',time.localtime(time.time()))

## 获取年月日时分秒
#	None
# 20230907121212
def get_string_datetime():
	return time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))

## 获取时分秒
#	None
# 12:12:12
def get_string_time():
	return time.strftime('%H:%M:%S',time.localtime(time.time()))

## 获取年月日时分秒和数据库时间一致
#	None
# 2023-09-07 12:12:12
def get_string_datetime_timestamp():
	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

## 获取年月日短横线相连
#	None
# 2023-09-07
def get_string_date_timestamp():
	return time.strftime('%Y-%m-%d', time.localtime(time.time()))


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



### 调试/测试代码
if __name__ == '__main__':
	pass