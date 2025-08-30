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
# @brief	VUE3项目框架实施
##################################################################

import	os
import	SpiritLong_utility
import	webframe_VUE3_src
import	webframe_VUE3_App_vue
import	webframe_VUE3_webframe_js

## 准备VUE3基本框架
def generate_basic_frame(path, project_name='webframe'):
	# 创建基本目录
	os.makedirs(f"{path}/public", 		exist_ok=True)
	os.makedirs(f"{path}/src/conponent", 	exist_ok=True)
	os.makedirs(f"{path}/src/view", 	exist_ok=True)
	os.makedirs(f"{path}/src/library", 	exist_ok=True)

	# ----------------------------------- src -----------------------------------
	with open(f'{path}/src/App.vue', 'w') as f:
		f.write(webframe_VUE3_App_vue.content)
	
	with open(f'{path}/src/main.js', 'w') as f:
		f.write(webframe_VUE3_src.content_main_js)

	with open(f'{path}/src/webframe.js', 'w') as f:
		f.write(webframe_VUE3_src.content_webframe_js)

	# ----------------------------------- package.json -----------------------------------
	with open(f'{path}/package.json', 'w') as f:
		f.write('''{
  "name"	: "vite-project",
  "private"	: true,
  "version"	: "0.0.0",
  "type"	: "module",
  "scripts"	: {
  	"dev"		: "vite --force --host",
  	"build"		: "vite build",
  	"preview"	: "vite preview"
  },
  "dependencies": {
  	"async-validator"		: "^4.2.5",
  	"axios"				: "^1.8.1",
  	"default-passive-events"	: "^2.0.0",
  	"lodash-es"			: "^4.17.21",
  	"nanoid"			: "^5.1.5",
  	"pinia"				: "^3.0.1",
  	"vconsole"			: "^3.15.1",
  	"vue"				: "^3.5.13",
  	"vue-qrcode"			: "^2.2.2",
  	"vue-router"			: "^4.5.0",
  	"ws"				: "^8.18.1"
  },
  "devDependencies": {
  	"@vitejs/plugin-vue"	: "^5.2.1",
  	"vite"			: "^6.2.3"
  }
}
''')
		
	# ----------------------------------- index.html -----------------------------------
	with open(f'{path}/index.html', 'w') as f:
		f.write('''
<!doctype html>
<html lang="en">
	<head>
		<meta charset="UTF-8" />
		<!-- 网页标题页LOGO -->
		<link rel="icon" type="image/svg+xml" href="/SpiritLong_logo_2024.svg" />
		<!-- 页面标题 -->
		<title>SpiritLong</title>
		<meta name="viewport" content="width=device-width, initial-scale=1.0" />
	</head>
	<body style="padding: 0px;margin:0px;">
		<div id="app" ></div>
		<!-- 启动main.js -->
		<script type="module" src="/src/main.js"></script>
	</body>
</html>
''')
	# ----------------------------------- vite.config.js -----------------------------------
	with open(f'{path}/vite.config.js', 'w') as f:
		f.write('''import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
	plugins: [vue()],
	server	:{
		proxy	: {
			'/API'	: {
				// 服务器URL
				target		: 'https://develop02.spiritlong.com',
				// 更改源
				changeOrigin	: true,
				// 防止自签名https被VITE挡住
				secure		: false,
			}
		}
	},
})
''')


# 脚本执行
if __name__ == '__main__':
	# 给文件增加版权说明
	# SpiritLong_utility.copyright(__file__, author='arthuryang')

	generate_basic_frame('./frontend')
