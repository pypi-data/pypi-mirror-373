#******************************************************************
# *           ____     _     _ __  __                 
# *          / __/__  (_)___(_) /_/ /  ___  ___  ___ _
# *         _\ \/ _ \/ / __/ / __/ /__/ _ \/ _ \/ _ `/
# *        /___/ .__/_/_/ /_/\__/____/\___/_//_/\_, / 
# *           /_/                              /___/  
# * Copyright (c) 2023 Chongqing Spiritlong Technology Co., Ltd.
# * All rights reserved.  
# * @author	shun
# * @brief	参数校验
# *
# *****************************************************************/

import re

## 是否为空
def is_empty(value):
	if not value:
		return True
	return False

## 是否是手机号
def is_mobile(value):
	if is_empty(value):
		return False
	
	if re.fullmatch(re.compile(r"^1\d{10}$"), str(value)):
		return True
	return False

## 是否是邮箱
def is_email(value):
	if is_empty(value):
		return False

	if re.fullmatch(re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'), str(value)):
		return True
	return False