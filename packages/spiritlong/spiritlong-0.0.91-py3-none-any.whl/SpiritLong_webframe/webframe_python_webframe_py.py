content	= '''#!/usr/bin/python3
# coding=utf-8
##################################################################
#               ____     _     _ __  __                 
#              / __/__  (_)___(_) /_/ /  ___  ___  ___ _
#             _\\ \\/ _ \\/ / __/ / __/ /__/ _ \\/ _ \\/ _ `/
#            /___/ .__/_/_/ /_/\\__/____/\\___/_//_/\\_, / 
#               /_/                              /___/  
# 
# Copyright (c) 2025 Chongqing Spiritlong Technology Co., Ltd.
# All rights reserved.
# @author	arthuryang
# @brief	webframe框架python后端，包括路由、uWSGI入口
##################################################################

import	sys
import	os
import	datetime
import	time
import	textwrap
import	redis
import	SpiritLong_utility as utility
import	SpiritLong_database as database
import	SpiritLong_excel as excel

from	routes		import routes

# 全局redis客户端
redis_client		= redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
# 全局配置
application_config	= {}
# 视图表配置
view_table_config	= {}

############################## 工具 ############################## 

## 更新全局配置
def update_application_config(config_file=None, config_db=None):
	global application_config

	file_path	= os.path.abspath(os.path.dirname(__file__))

	if config_file is None:
		# 默认的配置文件在./config/application.config
		config_file	= f"{file_path}/config/application.config"

	if not os.path.exists(config_file):
		# 无配置文件
		print(f"failed to update application_config for config_file not exists: {config_file}")
		return 
	# 读取配置文件
	with open(config_file, 'r') as f:
		for line in f:
			if line.strip().startswith('#'):
				continue
			parts	= line.split('=')
			if len(parts)==2:
				application_config[parts[0].strip()]	= parts[1].strip()
	# 检查主机是否为DEVELOP
	application_config['hostname']	= os.uname().nodename
	is_develop_host	= True if application_config['hostname'].startswith('DEVELOP') else False

	# 尝试读取配置数据库
	try:
		EXON_db	= database.Database({
			"host"		: application_config['EXON_application_host'],
			"user"		: application_config['EXON_application_user'],
			"passwd"	: application_config['EXON_application_password'],
			"database"	: application_config['EXON_application_database'],
			"port"		: int(application_config['EXON_application_port']),
		})


		result	= EXON_db.query_single(f\'\'\'
			SELECT 
				`APPLICATION`.`ID`,
				`APPLICATION`.`CODE`,
				`APPLICATION`.`NAME`,
				`APPLICATION`.`HTTP_PORT`,
				`APPLICATION`.`WEBSOCKET_PORT`,
				`APPLICATION`.`DEVELOP_HTTP_PORT`,
				`APPLICATION`.`DEVELOP_WEBSOCKET_PORT`,
				`APPLICATION`.`DEVELOP_REDIS_INDEX`,
				`DOMAIN`.`LEVEL2`,
				`DOMAIN`.`LEVEL1`,
				`PROJECT`.`CODE` AS `PROJECT_CODE`
			FROM `APPLICATION` 
			JOIN `DOMAIN`	ON `APPLICATION`.`DOMAIN_ID`=`DOMAIN`.`ID`
			JOIN `HOST`	ON `HOST`.`ID`=`DOMAIN`.`HOST_ID`
			JOIN `PROJECT`	ON `APPLICATION`.`PROJECT_ID`=`PROJECT`.`ID`
			WHERE `APPLICATION`.`ID`={application_config['EXON_application_ID']}
		\'\'\')
		application_config['application_code']	= result['CODE']
		application_config['application_name']	= result['NAME']
		application_config['http_port']		= result['DEVELOP_HTTP_PORT'] if is_develop_host else result['HTTP_PORT']
		application_config['websocket_port']	= result['DEVELOP_WEBSOCKET_PORT'] if is_develop_host else result['WEBSOCKET_PORT']
		application_config['redis_index']	= result['DEVELOP_REDIS_INDEX']	if is_develop_host else 0
		application_config['domain']		= f"{result['LEVEL2']}.{result['LEVEL1']}"
		application_config['project_code']	= result['PROJECT_CODE']
	except:
		print("failed to query EXON database. use default value")
		application_config['application_code']	= file_path.replace("/", "_").replace(".","")
		application_config['application_name']	= "未知项目"
		application_config['http_port']		= 8080
		application_config['websocket_port']	= 9000
		application_config['redis_index']	= 0
		application_config['domain']		= "unkownn_domain"
		application_config['project_code']	= "UNKNOWN"
	
	# 源代码路径
	application_config['path_source']		= file_path
	application_config['path_config']		= f"{application_config['path_source']}/config"
	application_config['path_frontend']		= f"{application_config['path_source']}/frontend"
	# 部署路径/链接
	application_config['path_base']			= f"/data/Application/{application_config['application_code']}"
	application_config['link_backend']		= f"{application_config['path_base']}/backend"
	application_config['path_frontend_runtime']	= f"{application_config['path_base']}/runtime/frontend"
	application_config['path_file']			= f"{application_config['path_base']}/file"
	application_config['path_log']			= f"{application_config['path_base']}/log"
	application_config['path_runtime']		= f"{application_config['path_base']}/runtime"
	application_config['link_uWSGI_logrotate']	= f"/etc/logrotate.d/uWSGI.{application_config['application_code']}"
	# uWSGI相关文件
	application_config['template_uWSGI_config']	= f"{application_config['path_config']}/uWSGI.config"
	application_config['template_uWSGI_logrotate']	= f"{application_config['path_config']}/logrotate.uWSGI.config"
	application_config['file_uWSGI_config']		= f"{application_config['path_runtime']}/uWSGI.config"
	application_config['file_uWSGI_socket']		= f"{application_config['path_runtime']}/uWSGI.socket"
	application_config['file_uWSGI_PID']		= f"{application_config['path_runtime']}/uWSGI.PID"
	application_config['file_uWSGI_reload']		= f"{application_config['path_runtime']}/uWSGI.reload"
	application_config['file_uWSGI_log_reopen']	= f"{application_config['path_runtime']}/uWSGI.log_reopen"
	application_config['file_uWSGI_logrotate']	= f"{application_config['path_runtime']}/uWSGI.logrotate"
	application_config['file_uWSGI_log']		= f"{application_config['path_log']}/uWSGI.log"
	# nginx相关文件
	application_config['file_certificate']		= f"{application_config['path_config']}/{application_config['domain']}.pem"
	application_config['file_certificate_key']	= f"{application_config['path_config']}/{application_config['domain']}.key"
	application_config['template_nginx_config']	= f"{application_config['path_config']}/nginx.config"
	application_config['file_nginx_config']		= f"{application_config['path_runtime']}/nginx.config"
	application_config['link_nginx_config']		= f"/etc/nginx/sites-enabled/{application_config['application_code']}"
	
	def set_default(name, default_value):
		global application_config
		if name not in application_config:
			application_config[name]	= default_value

	set_default('uWSGI_mount',		'/API') 
	set_default('uWSGI_process_n',		4) 
	set_default('uWSGI_request_max',	5000)
	set_default('uWSGI_buffer_size',	65536)
	set_default('uWSGI_post_buffering',	65536)

	# 数据库
	application_config['db']	= database.Database({
		'host'		: application_config['database_host'],
		'user'		: application_config['database_user'],
		'passwd'	: application_config['database_password'],
		'database'	: application_config['database_database'],
		'port'		: int(application_config['database_port']),
	}, use_redis={ 
		'host'	: application_config['redis_host'],
		'port'	: application_config['redis_port'],
		'db'	: application_config['redis_index'],
	})
	application_config['redis']	= application_config['db'].redis

# 加载视图表配置
def load_view_table_config():
	global view_table_config
	
	# 从config/view_table_config.xlsx中读取视图表配置
	config_file	= f"{application_config['path_config']}/view_table_config.xlsx"
	if not os.path.exists(config_file):
		print(f"未找到视图表配置文件: {config_file}")
		return
	try:
		book	= excel.open_xlsx(config_file)
		meta_sheet	= book['META']
		field_sheet	= book['FIELD']
		view_sheet	= book['VIEW']
		element_sheet	= book['ELEMENT']

		view_config		= excel.get_records_with_title(view_sheet)
		field_config		= excel.get_records_with_title(field_sheet)
		meta_config		= excel.get_records_with_title(meta_sheet)
		view_config_dict	= {}
		# 一个VIEW_NAME对应一个VIEW_TABLE_ID数组
		for view in view_config:
			if view['VIEW_NAME'] not in view_config_dict:
				view_config_dict[view['VIEW_NAME']]	= []
			view_config_dict[view['VIEW_NAME']].append(view['VIEW_TABLE_ID'])
		# 一个VIEW_TABLE_ID对应一个FIELD数组
		field_config_dict	= {}
		for field in field_config:
			if field['VIEW_TABLE_ID'] not in field_config_dict:
				field_config_dict[field['VIEW_TABLE_ID']]	= []
			field_config_dict[field['VIEW_TABLE_ID']].append(field['NAME'])
		# 一个VIEW_TABLE_ID对应一个VIEW_TABLE配置
		view_table_config_dict	= {}
		for view_table in meta_config:
			if view_table['VIEW_TABLE_ID'] not in view_table_config_dict:
				view_table_config_dict[view_table['VIEW_TABLE_ID']]	= {}
			view_table_config_dict[view_table['VIEW_TABLE_ID']]	= view_table
		view_table_config	= {
			'meta'		: view_table_config_dict,
			'element'	: excel.get_records_with_title(element_sheet),
			'field'		: field_config_dict,
			'view'		: view_config_dict,
		}
		print(f'加载视图表配置成功：{view_table_config}')
	except Exception as e:
		sys.exit(f"加载视图表配置失败: {e}")

# 加载所有权限列表
def load_all_permission_list():
	try:
		config_file	= f"{application_config['path_config']}/permission_config.xlsx"
		if not os.path.exists(config_file):
			print(f"未找到权限配置文件: {config_file}")
			return
		book	= excel.open_xlsx(config_file)
		sheet	= book['Sheet1']
		permission_list	= excel.get_records_with_title(sheet)
		permission_list	= [{
			'key'	: permission['序号'],
			'value'	: permission['权限'],
		} for permission in permission_list]
		redis_client.set('ALL_PERMISSION_LIST', utility.object_to_json(permission_list))
	except Exception as e:
		sys.exit(f"加载权限配置失败: {e}")

# 立即加载配置
update_application_config()
load_view_table_config()
load_all_permission_list()

############################## uWSGI ##############################

# 初始化全局路由
routes.redis		= application_config['redis']
routes.db		= application_config['db']

# 注意uwsgi并非一个python包，被uwsgi服务调用时才会有这个内建的模块
try: 
	import	uwsgi
	import	application.route
except ImportError:
	pass

## uWSGI入口
def application(environment, start):
	# ------------------ 路由前处理 ------------------

	# ------------------ 路由解析 ------------------
	data	= routes.query(environment)

	# ------------------ 路由后处理 ------------------
	# 增加日志变量
	uwsgi.set_logvar('datetime', str(datetime.datetime.today()))
	uwsgi.set_logvar('user_ID', str(data['user_ID']))

	# 权限管理
	
	# 执行路由，返回响应
	return	routes.response(data, start)

#################################### run.sh #################################
## 启动
#	backend_only	是否只启动后端
def webframe_run_start(backend_only=True):
	global application_config

	# 准备目录/符号链接：每个应用在/data/Application下有一个以其应用代码为名的目录
	os.system(f"mkdir -p {application_config['path_file']}")
	os.system(f"mkdir -p {application_config['path_log']}")
	os.system(f"mkdir -p {application_config['path_runtime']}")
	os.system(f"mkdir -p {application_config['path_frontend_runtime']}")
	# 第一次添加之后不再覆盖，防止从此路径引用启动
	if not os.path.exists(application_config['link_backend']):
		os.system(f"ln -sf {application_config['path_source']} {application_config['link_backend']}")

	def touch_file(filename, mode="666"):
		os.system(f"touch {filename}; chmod {mode} {filename}")
	touch_file(application_config['file_uWSGI_reload'])
	touch_file(application_config['file_uWSGI_log_reopen'])

	# ----------------- uWSGI -------------------
	# uWSGI配置
	with open(application_config['template_uWSGI_config'], "r") as f:
		content	= f.read()
	content	= content.replace('$APPLICATION_CODE',	application_config['application_code'])
	content	= content.replace('$MOUNT',		application_config['uWSGI_mount'])
	content	= content.replace('$APP_FILE',		os.path.basename(__file__))
	content	= content.replace('$SOCKET',		application_config['file_uWSGI_socket'])
	content	= content.replace('$PROCESS_N',		application_config['uWSGI_process_n'])
	content	= content.replace('$PID_FILE',		application_config['file_uWSGI_PID'])
	content	= content.replace('$LOG_FILE',		application_config['file_uWSGI_log'])
	content	= content.replace('$RELOAD_FILE',	application_config['file_uWSGI_reload'])
	content	= content.replace('$LOG_REOPEN',	application_config['file_uWSGI_log_reopen'])
	content	= content.replace('$REQUEST_MAX',	application_config['uWSGI_request_max'])
	content	= content.replace('$HARAKIRI',		application_config['uWSGI_harakiri'])
	content	= content.replace('$BUFFER_SIZE',	application_config['uWSGI_buffer_size'])
	content	= content.replace('$POST_BUFFERING',	application_config['uWSGI_post_buffering'])
	content	= content.replace('$LOGREOPEN_FILE',	application_config['file_uWSGI_log_reopen'])

	with open(application_config['file_uWSGI_config'], "w") as f:
		f.write(content)

	# 确保日志文件
	os.system(f"touch {application_config['file_uWSGI_log']}")

	# 配置日志切片 uWSGI
	with open(application_config['template_uWSGI_logrotate'], 'r') as f:
		content	= f.read()
	content	= content.replace('$UWSGI_LOG_FILE',		application_config['file_uWSGI_log'])
	content	= content.replace('$UWSGI_LOG_REOPEN',		application_config['file_uWSGI_log_reopen'])
	with open(application_config['file_uWSGI_logrotate'], "w") as f:
		f.write(content)

	# 链接logrotate
	os.system(f"ln -snf {application_config['file_uWSGI_logrotate']} {application_config['link_uWSGI_logrotate']}")

	# 启动uWSGI
	os.system(f"uwsgi --ini {application_config['file_uWSGI_config']}")
	
	# ----------------- frontend ------------------
	# 处理前端源代码目录下的内容：
	if not backend_only:
		for frontend in os.listdir(application_config['path_frontend']):
			frontend_path	= os.path.join(application_config['path_frontend'], frontend)
			# 前端为目录则需要打包
			if os.path.isdir(frontend_path):
				vite_config_file	= os.path.join(frontend_path, 'vite.config.js')
				if not os.path.exists(vite_config_file):
					# 跳过非vite项目
					print(f"跳过非vite项目: {frontend_path}")
					continue
				with open(vite_config_file, "r") as f:
					content	= f.read()
				output	= os.path.join(application_config['path_frontend_runtime'], frontend)
				# 替换vite.config.js中的配置build和base
				replace_flag_start	= '// TO REPLACE START'
				replace_flag_end	= '// TO REPLACE END'
				to_replace_content	= content.split(replace_flag_start)[1]
				if to_replace_content:
					to_replace_content	= to_replace_content.split(replace_flag_end)[0]
				if to_replace_content:
					replace_content	= textwrap.dedent(f\'\'\'
						build: {{
							outDir: '{output}'
						}},
						base: '/{frontend}/'
					\'\'\')
					replace_content	= '\\n'.join(['\\t' + line if line else line for line in replace_content.split('\\n')])+'\\t'
					content	= content.replace(to_replace_content, replace_content)
				with open(vite_config_file, "w") as f:
					f.write(content)
				# 先清除之前的打包内容
				if os.path.exists(output):
					os.system(f"rm -rf {output}/*")
				# 安装依赖和打包
				os.system(f\'\'\'
					cd {frontend_path}
					npm install
					npm run build
				\'\'\')
				# 删除node_modules
				if os.path.exists(f"{frontend_path}/node_modules"):
					os.system(f"rm -rf {frontend_path}/node_modules")


	# 检查SSL证书
	if not (os.path.exists(application_config['file_certificate']) and os.path.exists(application_config['file_certificate_key'])):
		# 没有证书就自行生成
		os.system(f"openssl genrsa -out {application_config['file_certificate_key']} 2048")
		os.system(f\'\'\'openssl req -new -x509 -key {application_config['file_certificate_key']} -out {application_config['file_certificate']} \'\'\'+
			f\'\'\'-days 1095 -subj "/C=CN/ST=CQ/L=BB/O=SpiritLong/CN={application_config['domain']}"\'\'\')


	# nginx配置：变量替换，设置链接
	with open(application_config['template_nginx_config'], 'r') as f:
		content	= f.read()
	content	= content.replace('$PORT',			str(application_config['http_port']))
	content	= content.replace('$CERTIFICATE_FILE',		application_config['file_certificate'])
	content	= content.replace('$CERTIFICATE_KEY_FILE',	application_config['file_certificate_key'])
	content	= content.replace('$DOMAIN',			application_config['domain'])
	content	= content.replace('$FRONTEND_PATH',		application_config['path_frontend_runtime'])
	content	= content.replace('$UWSGI_MOUNT',		application_config['uWSGI_mount'])
	content	= content.replace('$UWSGI_SOCKET',		application_config['file_uWSGI_socket'])
	content	= content.replace('$WEBSOCKET_PORT',		str(application_config['websocket_port']))
	# 微信认证的MP_verify文件，如果config目录下有MP_verify开头的文件，则复制到runtime目录下
	for file in os.listdir(application_config['path_config']):
		if file.startswith('MP_verify'):
			os.system(f"cp {application_config['path_config']}/{file} {application_config['path_frontend_runtime']}/{file}")
	# 遍历前端源代码目录，子目录名作为访问路径
	for frontend in os.listdir(application_config['path_frontend']):
		frontend_path	= os.path.join(application_config['path_frontend'], frontend)
		if not os.path.isdir(frontend_path):
			continue
		replace_content	= textwrap.dedent(f\'\'\'
			location / {{
				root {application_config['path_frontend_runtime']};
				index index.html;
				try_files $uri $uri/ /index.html;
			}}
			
			location /{frontend} {{
				alias {application_config['path_frontend_runtime']}/{frontend};
				index index.html;
				try_files $uri $uri/ /{frontend}/index.html;
			}}
		\'\'\')
		replace_content	= '\\n'.join(['\\t' + line if line else line for line in replace_content.split('\\n')])
		replace_flag	= '# frontend'
		if replace_flag in content:
			content	= content.replace(replace_flag, replace_content)
	with open(application_config['file_nginx_config'], "w") as f:
		f.write(content)
	
	os.system(f"ln -snf {application_config['file_nginx_config']} {application_config['link_nginx_config']}")
	
	# 设置权限
	os.system(f"chown www-data {application_config['path_runtime']} -R")
	os.system(f"chgrp www-data {application_config['path_runtime']} -R")


	# 启动nginx
	if os.system("service nginx reload")!=0:
		print("failed")

## 停止
def webframe_run_stop():
	global application_config
	# 刷新redis
	redis_client.flushdb()
	# 停止 uWSGI
	os.system(f"uwsgi --stop {application_config['file_uWSGI_PID']}")

# ===================================== 视图表相关API =====================================
# 生成视图表的所有ID列表
#	view_name	视图名称
#	condition	条件
#	返回值		视图表ID列表规则字符串
def get_view_table_IDs(view_name, condition=None, controller={}):
	views_config		= view_table_config['view']
	meta_config		= view_table_config['meta']
	if view_name not in views_config:
		print(f"配置文件的VIEW中没有{view_name}视图")
		return {}

	view_table_IDs	= views_config[view_name]
	view_ID_info	= {}
	for view_table_ID in view_table_IDs:
		# meta表和element表单独处理
		if view_table_ID==0 or view_table_ID==1:
			continue
		# 调用controller中对应的函数获取到视图表的所有ID
		function_name	= f"VD_{view_table_ID}_get_IDs"
		if not hasattr(controller, function_name):
			print(f"controller中没有{view_name}的get_IDs函数{function_name}")
			continue
		function	= getattr(controller, function_name)
		parameters	= condition.get(str(view_table_ID))
		ID_list		= function(**parameters) if parameters else function()
		if not isinstance(ID_list, list):
			print(f"controller中函数get_{view_name}的返回值必须是列表")
			ID_list	= []
		# 该是视图表所有ID
		all_ID_string			= stringify_ID_list(ID_list)
		# 初始订阅ID
		initial_values			= meta_config[view_table_ID]['INITIAL_VALUES']
		initial_subscribe_ID_string	= initial_values if initial_values else ''
		# ;之前是所有ID，之后是初始订阅ID
		view_ID_info[view_table_ID]	= f"{all_ID_string};{initial_subscribe_ID_string}"
		# 调用controller中对应的函数生成ID对应的视图表数据存到redis中
		function_name	= f"VD_{view_table_ID}_get_data"
		if not hasattr(controller, function_name):
			print(f"controller中没有{view_name}的get_data函数{function_name}")
			continue
		function	= getattr(controller, function_name)
		parameters	= condition.get(str(view_table_ID))
		data		= function(**parameters) if parameters else function()
		if not isinstance(data, list):
			print(f"controller中函数{function_name}的返回值必须是列表")
			continue
		for data_item in data:
			for view_table_record_ID in data_item:
				record_name	= f"VD {view_table_ID} {view_table_record_ID}"
				redis_client.set(record_name, utility.object_to_json(data_item[view_table_record_ID]))
	return view_ID_info

# 更新订阅
#	view_name	视图名称，订阅视图中的哪些表
#	tables		存储需要订阅或者退订的表数据ID信息，是一个字典
#	websocket_code	websocket code
def update_subscription(view_name, tables, websocket_code):
	global view_table_config
	# 订阅视图表（修改此处将ID转换为字符串）
	view_table_IDs	= [str(ID) for ID in view_table_config['view'][view_name]]
	channels	= [f"VD 0 {ID}" for ID in view_table_IDs]
	message		= f"SUBSCRIBE {websocket_code} {','.join(channels)}"
	print(f"订阅消息：{message}")
	redis_client.publish("WEBSOCKET SERVER", message)
	
	# 订阅表单元素表（同样处理元素ID）
	element_IDs	= [str(element['ELEMENT_ID']) for element in view_table_config['element']]
	channels	= [f"VD 1 {element_ID}" for element_ID in element_IDs]
	message		= f"SUBSCRIBE {websocket_code} {','.join(channels)}"
	print(f"订阅消息：{message}")
	redis_client.publish("WEBSOCKET SERVER", message)


	# 订阅视图表记录
	for table_ID, ID_string in tables.items():
		# 按规则解析ID_string
		subscribe_ID_string, unsubscribe_ID_string = ID_string.split(';')
		subscribe_ID_list	= parse_ID_string(subscribe_ID_string)
		unsubscribe_ID_list	= parse_ID_string(unsubscribe_ID_string)
		redis_client.set(f"VD 0 {table_ID}", subscribe_ID_string)
		# 处理订阅
		if subscribe_ID_list:
			subscribe_channels	= [f"VD {table_ID} {ID}" for ID in subscribe_ID_list]
			channels		= ','.join(subscribe_channels)
			message			= f"SUBSCRIBE {websocket_code} {channels}"
			print(f"订阅消息：{message}")
			redis_client.publish("WEBSOCKET SERVER", message)

		# 处理取消订阅
		if unsubscribe_ID_list:
			unsubscribe_channels	= [f"VD {table_ID} {ID}" for ID in unsubscribe_ID_list]
			channels		= ','.join(unsubscribe_channels)
			message			= f"UNSUBSCRIBE {websocket_code} {channels}"
			print(f"取消订阅消息：{message}")
			redis_client.publish("WEBSOCKET SERVER", message)
	time.sleep(0.02)
	# 发布数据
	publish_data(tables)

# 发布数据
#	websocket_code	websocket code
#	channels	频道
def publish_data(tables):
	for table_ID, ID_string in tables.items():
		# 按规则解析ID_string
		subscribe_ID_string = ID_string.split(';')[0]
		subscribe_ID_list	= parse_ID_string(subscribe_ID_string)
		for record_ID in subscribe_ID_list:
			record_data	= redis_client.get(f"VD {table_ID} {record_ID}")
			if record_data:
				record_data	= utility.json_to_object(record_data)
			channel		= f"VD {table_ID} {record_ID}"
			message		= utility.object_to_json((channel, record_data))
			redis_client.publish(channel, message)

# 对表发布数据
#	table_ID	表ID
#	websocket_code	websocket code
#	channels	频道
def publish_table_data(table_ID):
	record_ID_list	= redis_client.keys(f"VD {table_ID} *")
	for record_ID in record_ID_list:
		record_data	= redis_client.get(f"VD {table_ID} {record_ID}")
		if record_data:
			record_data	= utility.json_to_object(record_data)
		channel		= f"VD {table_ID} {record_ID}"
		message		= utility.object_to_json((channel, record_data))
		redis_client.publish(channel, message)

# 按规则解析ID_string，ID_string由逗号隔开，如果包含-则表示范围
#   ID_string   ID字符串，格式如: "1,2,3-5"
#   返回值      一个ID列表
def parse_ID_string(ID_string):
	if not ID_string.strip():
		return []
	result	= []
	for part in ID_string.split(','):
		if '-' in part:
			start, end	= map(int, part.split('-'))
			result.extend(range(start, end + 1))
		else:
			result.append(int(part))
	return sorted(result)

# 按规则将ID列表转换为字符串
#   ID_list   ID列表
#   返回值     ID字符串，格式如: "1,2,3-5"
def stringify_ID_list(ID_list):
	if not ID_list:
		return ""
	ID_list	= sorted(set(ID_list))
	result	= []
	start	= ID_list[0]
	for i in range(1, len(ID_list)):
		if ID_list[i] != ID_list[i - 1] + 1:
			result.append(f"{start}-{ID_list[i - 1]}" if start != ID_list[i - 1] else str(start))
			start = ID_list[i]
	result.append(f"{start}-{ID_list[-1]}" if start != ID_list[-1] else str(start))
	return ",".join(result)

class Logger:
	def __init__(self, db_config=None, log_dir='logs'):
		self.db		= db_config if db_config else None
		self.log_dir	= log_dir

	def _write_file_log(self, level, module, message):
		try:
			log_file = os.path.join(self.log_dir, f"runtime.log")
			timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			
			with open(log_file, 'w', encoding='utf-8') as f:
				log_entry = f"[{timestamp}] [{level}] [{module}] {message}\\n"
				f.write(log_entry)
		except Exception as e:
			print(f"写入日志文件时发生错误：{str(e)}")

	def _write_db_log(self, log_data):
		self.db.insert('LOG', [log_data])
	
	def _log(self, level, module, message):
		self._write_file_log(level, module, message)
		
		log_data = {
			'TYPE'		: 'SYSTEM',
			'LEVEL'		: level,
			'MODULE'	: module,
			'MESSAGE'	: message,
		}
		self._write_db_log(log_data)

	def error(self, module, message):
		"""记录错误日志"""
		self._log('ERROR', module, message)

	def warn(self, module, message):
		"""记录警告日志"""
		self._log('WARN', module, message)

	def info(self, module, message):
		"""记录信息日志"""
		self._log('INFO', module, message)
	
	def debug(self, module, message):
		"""记录调试日志"""
		self._log('DEBUG', module, message)

log	= Logger(application_config['db'], application_config['path_log'])

if __name__ == '__main__':
	if os.getuid()!=0:
		print("ROOT only!")
		exit(1)
	if len(sys.argv)==1:
		# 无参数表示只启动后端（先停后启动）
		webframe_run_stop()
		webframe_run_start()
		# 打印配置参数
		for c in application_config:
			print(f"{c:>50}\\t{application_config[c]}")
	elif len(sys.argv)==2 and sys.argv[1] in ['stop']:
		# 只有这种情况停止
		webframe_run_stop()
	elif len(sys.argv)==2 and sys.argv[1] in ['start']:
		# 启动前端和后端（先停后启动）
		webframe_run_stop()
		webframe_run_start(backend_only=False)
		# 打印配置参数
		for c in application_config:
			print(f"{c:>50}\\t{application_config[c]}")
	else:
		print("参数错误")
		exit(1)
'''