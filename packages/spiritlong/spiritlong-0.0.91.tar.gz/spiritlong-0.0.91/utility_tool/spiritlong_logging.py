#******************************************************************
# *           ____     _     _ __  __                 
# *          / __/__  (_)___(_) /_/ /  ___  ___  ___ _
# *         _\ \/ _ \/ / __/ / __/ /__/ _ \/ _ \/ _ `/
# *        /___/ .__/_/_/ /_/\__/____/\___/_//_/\_, / 
# *           /_/                              /___/  
# * Copyright (c) 2023 Chongqing Spiritlong Technology Co., Ltd.
# * All rights reserved.  
# * @author	shun
# * @brief	logging日志支持输入多个参数
# *
# *****************************************************************/

import 	logging

### logging日志支持输入多个参数
class SpiritLongLoggingFormatter(logging.Formatter):
	def format(self, record):
		# 第一个参数为数字
		if type(record.msg) is int:
			record.msg 	= str(record.msg)
		
		# dict和tuple分别处理
		if type(record.args) is dict:
			record.msg	= record.msg + ", " + str(record.args)
		elif type(record.args) is tuple:
			for item in record.args:
				record.msg	= record.msg + ", " +str(item)
		
		# 重置参数
		record.args	= ()
		
		return super().format(record)

### 调试/测试代码
if __name__ == '__main__':
	from datetime import datetime
	
	# 基础配置
	logger		= logging.getLogger()
	handler		= logging.StreamHandler()
	handler.setFormatter(SpiritLongLoggingFormatter('%(asctime)s - %(levelname)s - %(message)s'))
	logging.basicConfig(level=logging.INFO, handlers=[handler])

	# 测试
	logger.info("debug message", "test",666)
	logger.info(666)
	logger.info(666, 888)
	logger.info([{"test1":666},{"test2":666}])
	logger.info({"test":666})
	logger.info("debug message", {"test":666})
	logger.info("debug message", {"test":666}, 666)
	logger.info("debug message", [{"test1":666},{"test2":666}])