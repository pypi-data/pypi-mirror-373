#!/usr/bin/python3
# coding=utf-8
###################################################################
#           ____     _     _ __  __                 
#          / __/__  (_)___(_) /_/ /  ___  ___  ___ _
#         _\ \/ _ \/ / __/ / __/ /__/ _ \/ _ \/ _ `/
#        /___/ .__/_/_/ /_/\__/____/\___/_//_/\_, / 
#           /_/                              /___/  
# Copyright (c) 2023 Chongqing Spiritlong Technology Co., Ltd.
# All rights reserved.  
# @author	arthuryang
# @brief	检查源代码，确保源代码文件开始有公司版权说明
###################################################################  

import	os
import	re
import	sys
import	datetime

## 增加/更新源代码版权说明，注释仅第一次添加版权说明有效
#	filename	文件名
#	brief		说明
#	author		作者
#	year		年份

def copyright(filename, brief="", author="SpiritLong", year=None):
	company_name	= "Chongqing Spiritlong Technology Co., Ltd."
	logo_lines	= r'''
             ____     _     _ __  __                 
            / __/__  (_)___(_) /_/ /  ___  ___  ___ _
           _\ \/ _ \/ / __/ / __/ /__/ _ \/ _ \/ _ `/
          /___/ .__/_/_/ /_/\__/____/\___/_//_/\_, / 
             /_/                              /___/  
'''.split('\n')[1:]

	width	= 66
	# 不同类型源代码的默认版权行
	copyright_lines_for_types	= {
		'C/C++'		: {
			'extension_list'	: ['.c', '.cpp', '.h', '.cc', '.js'],
			'before_lines'		: [],
			'top_line'		: ['/'+'*'*width],
			'bottom_line'		: [' '+'*'*width+'/'],
			'prefix'		: ' * ',
		},

		'python'	: {
			'extension_list'	: ['.py'],
			'before_lines'		: ['#!/usr/bin/python3', '# coding=utf-8'],
			'top_line'		: ['#'*width],
			'bottom_line'		: ['#'*width],
			'prefix'		: '# ',
		},

		'shell'		: {
			'extension_list'	: ['.sh'],
			'before_lines'		: ['#!/usr/bin/bash'],
			'top_line'		: ['#'*width],
			'bottom_line'		: ['#'*width],
			'prefix'		: '# ',
		},

		'config'		: {
			'extension_list'	: ['.config'],
			'before_lines'		: [],
			'top_line'		: ['#'*width],
			'bottom_line'		: ['#'*width],
			'prefix'		: '# ',
		},

		'VUE'	: {
			'extension_list'	: ['.vue'],
			'before_lines'		: [],
			'top_line'		: ['<!--'+'-'*width],
			'bottom_line'		: ['-'*width+'--->'],
			'prefix'		: '- ',
		},

		'java'	: {
			'extension_list'	: ['.java'],
			'before_lines'		: [],
			'top_line'		: ['/'+'*'*width],
			'bottom_line'		: [' '+'*'*width+'/'],
			'prefix'		: ' * ',
		},

		'txt'	: {
			'extension_list'	: ['.txt'],
			'before_lines'		: [],
			'top_line'		: ['#'*width],
			'bottom_line'		: ['#'*width],
			'prefix'		: '  ',
		},
	}

	if year is None:
		year	= datetime.datetime.now().year

	with open(filename, "r", encoding='utf-8') as f:
		lines	= [l.replace('\n', '') for l in f.readlines()]

	# 判断源代码类型
	_, extension	= os.path.splitext(filename)
	for t in copyright_lines_for_types:
		config		= copyright_lines_for_types[t]
		if extension in config['extension_list']:
			# 找到类型了
			copyright_line	= len(config['before_lines'])+len(config['top_line'])+len(logo_lines)
			brief_line	= copyright_line+3
			# 做个标记
			extension	= None
			break
	if extension:
		# 没找到类型，即不支持的类型
		print(f"不支持的类型：{extension}")
		return
	
	# 检查版权说明行是否存在
	if len(lines)<=copyright_line:
		# 少于此值的肯定没有版权说明
		copyright_ready	= False
	else:
		copyright_ready	= re.match(r".*Copyright \(c\) \d{4} "+company_name, lines[copyright_line])

	# 构建版权行
	copyright_lines	= config['before_lines']+config['top_line']+[config['prefix']+l for l in logo_lines]+[
				f"{config['prefix']}Copyright (c) {year} {company_name}",
				f"{config['prefix']}All rights reserved.",	
				f"{config['prefix']}@author	{author}",
			]
			
	if not copyright_ready:
		# 没有版权说明才添加指定的说明
		copyright_lines.append(f"{config['prefix']}@brief	{brief}")
		copyright_lines	+= config['bottom_line']
		# 最后加个空行
		copyright_lines.append("")
	
	# 插入/更新标题行
	lines	= copyright_lines[:brief_line]+lines[brief_line:] if copyright_ready else copyright_lines+lines

	# 确保最后一行是空行
	if lines[-1]!='':
		lines.append('')

	# 写入到文件		
	with open(filename, "w", encoding='utf-8') as f:
		f.write('\n'.join(lines))

if __name__ == '__main__':
	filename	= r"C:\Users\yangs\Documents\SVN\TORIA\BJCA_OTA\Source\readme.txt"
	copyright(filename, author="arthuryang")
	# exit()

	#if len(sys.argv)==3:
	#	copyright(sys.argv[1], author=sys.argv[2])
	#elif len(sys.argv)==2:
		
	#	copyright(sys.argv[1])
	#else:
	#	print("source_copyright.py filename author")
	#	exit()
	pass
