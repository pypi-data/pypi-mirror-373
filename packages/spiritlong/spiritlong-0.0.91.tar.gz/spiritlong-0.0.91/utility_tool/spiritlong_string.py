#******************************************************************
# *           ____     _     _ __  __                 
# *          / __/__  (_)___(_) /_/ /  ___  ___  ___ _
# *         _\ \/ _ \/ / __/ / __/ /__/ _ \/ _ \/ _ `/
# *        /___/ .__/_/_/ /_/\__/____/\___/_//_/\_, / 
# *           /_/                              /___/  
# * Copyright (c) 2023 Chongqing Spiritlong Technology Co., Ltd.
# * All rights reserved.  
# * @author	shun
# * @brief	字符串、字符串数组处理
# *
# *****************************************************************/


# 获取字符串在的所有行
def list_content_in(list_data, list_key):
        list_content    = []

        for line in list_data:
                for content in list_key:
                        if line.find(content)>-1:
                                line    = line.strip()

                                list_content.append(line+"\n")
                                
                                # 防止行重复
                                break
        return list_content

# 获取字符串之间的行
def list_content_between(list_data, start, end, is_contain=True):
	count_line      = 0
	list_content    = []
	for line in list_data:
                # 开始
		if line.find(start)>-1:
			count_line   = 1
			if is_contain:
				count_line      = 2
                
		if count_line > 1:
                        
			# 结束
			if line.find(end)>-1:
				count_line      = 0
				list_content.append("\n")
				if is_contain==False:
					continue

			line    = line.rstrip()
			list_content.append(line+"\n")
                
		if count_line > 0:
			count_line      = count_line + 1

	return list_content
