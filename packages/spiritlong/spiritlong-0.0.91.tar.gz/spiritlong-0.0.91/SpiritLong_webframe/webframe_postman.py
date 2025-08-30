#!/usr/bin/python3
# coding=utf-8
##################################################################
#              ____     _     _ __  __                 
#             / __/__  (_)___(_) /_/ /  ___  ___  ___ _
#            _\ \/ _ \/ / __/ / __/ /__/ _ \/ _ \/ _ `/
#           /___/ .__/_/_/ /_/\__/____/\___/_//_/\_, / 
#              /_/                              /___/  
# 
# Copyright (c) 2025 Chongqing Spiritlong Technology Co., Ltd.
# All rights reserved.
# @author	arthuryang
# @brief	测试POST API的工具
##################################################################

import	json
import	requests

## 测试POST API，显示返回的数据
#	URL		协议+主机+端口
#	route		路由
#	post_json	要传递的json
def postman(URL, route, post_json, print_return=False):
	response	= requests.post(URL+route, json=post_json)
	print(f"\npost test: {URL+route:64}{response.status_code}")

	if print_return:
		try:
			j	= json.loads(response.text)
			for t in j:
				print(f"{t:32}{j[t]}")
		except Exception as e:
			print(e)

	return response.text


# 脚本执行
if __name__ == '__main__':
	postman("http://localhost:8080", "/test_DTO", {
		'group_ID'	: 1234,
		'fghCDEF'	: 'test2',
		'nobody'	: 'test3'
	}, True)

	
