

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
# @brief	excel工具集
#
###################################################################  

import sys

from	SpiritLong_excel.excel	import		\
		cell_font,			\
		cell_fill,			\
		cell_border,			\
		open_xlsx,			\
		set_cell,			\
		get_records_with_title,		\
		get_records_with_parameters,	\
		get_records_with_table_fields,	\
		adjust_column_width,		\
		adjust_all_column_width,	\
		cell_code,			\
		records_to_sheet,		\
		records_to_excel,		\
		csv_save_as_xlsx,		\
		xls_save_as_xlsx,		\
		alignment_center,		\
		alignment_left,			\
		alignment_right,		\
		style_title