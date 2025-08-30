content	= '''#!/usr/bin/python3
# coding=utf-8
##################################################################
#               ____     _     _ __  __                 
#              / __/__  (_)___(_) /_/ /  ___  ___  ___ _
#             _\ \/ _ \/ / __/ / __/ /__/ _ \/ _ \/ _ `/
#            /___/ .__/_/_/ /_/\__/____/\___/_//_/\_, / 
#               /_/                              /___/  
# 
# Copyright (c) 2025 Chongqing Spiritlong Technology Co., Ltd.
# All rights reserved.
# @author	arthuryang
# @brief	webframe框架路由
##################################################################

# route和uwsgi入口需要分成两个文件来实现，因为application/route.py将会import全局实例routes
# 如果将routes放在webframe.py中，而webframe.py又引用了application/ruote.py，从而会导致循环引用卡死

import	datetime
import	time
import	json
import	secrets
import	string
import	crypt
import	jwt	# pip install pyjwt
import	requests
from	werkzeug	import Request
import	redis as redis_package
from	permission import get_login_user_permission

redis_client	= redis_package.Redis(connection_pool=redis_package.ConnectionPool(db=0, decode_responses=True))

## JsonEncoder处理datetime、Decimal
class BackendJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime.datetime):
			return obj.strftime('%Y-%m-%d %H:%M:%S')
		elif isinstance(obj, datetime.date):
			return obj.strftime('%Y-%m-%d')
		elif isinstance(obj, decimal.Decimal):
			return str(obj).rstrip("0").rstrip(".")
		else:
			return json.JSONEncoder.default(self, obj)
## 路由类和实例
class Routes():
	def __init__(self):
		self.routes		= {}
		# 需要在外部初始化这些成员变量
		self.redis		= None
		self.db			= None
		
		# 默认TOKEN算法
		self.token_algorithm	= 'HS256'
		# token的超期天数
		self.token_expire_days	= 7
		# token的更新天数
		self.token_update_days	= 1
		# 默认token key
		self.token_secret_key	= ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))

	## 装饰器，增加路由
	#       str     route_name	      路由名称
	#       list    parameters_required     参数列表
	#       bool    authorization_required  是否需要认证
	# decorator
	def add(self, route_name, parameters_required=[], authorization_required=True, **options):
		def decorator(f):
			# 增加路由规则
			self.routes[route_name] = {
				'function'			: f,				# 返回字节数组body
				'parameters_required'		: parameters_required,		# 必须要有的参数列表
				'authorization_required'	: authorization_required,       # 此路由是否需要认证才可访问
			}
			
			return f
		return decorator
	
	## 获取路由规则的内容
	def get(self, route_string):
		return self.routes.get(route_string)

	## 生成TOKEN
	def generate_token(self, user_ID):
		# 查询用户的JWT_KEY
		result	= self.db.query_redis('USER', [user_ID])
		if not result:
			# 没找到用户
			return ''
		
		# TOKEN所用的KEY如果在JWT_KEY字段，则可以通过更新该字段来使得该用户的所有TOKEN都失效
		secret_key	= result[0]['JWT_KEY'] if 'JWT_KEY' in result[0] else self.token_secret_key
		return jwt.encode(key=secret_key, algorithm=self.token_algorithm, headers={
				'alg'	: self.token_algorithm,
				'typ'	: 'JWT',
			},
			payload={
				'user_ID'		: user_ID,		# 用户ID，必须有
				'timestamp'		: time.time(),		# 签发时间戳
			})
	
	## 路由查找
	#	environment	从uWSGI传入的环境参数
	#	use_websocket	是否使用websocket
	# 返回data
	def query(self, environment, use_websocket=True):
		# 返回值data的默认值，全部键的定义都在此
		data    = {
			'request'	: Request(environment),
			'route'		: None,
			'route_name'	: environment.get('PATH_INFO'),
			'user_ID'	: 0,	# 0 表示未指定用户
			'message'	: '',	# （路由设置）响应详细消息，供前端参考
			'result'	: 'OK',	# （路由设置）响应结果字符串，供前端参考
			'return_data'	: {},	# （路由设置）返回数据：可以是bytes（直接发给前端）或对象（打包到JSON发给前端）
			'form'		: {},	# 来自表单的参数
			'files'		: {},	# 上传的文件
			'json'		: {},	# 来自JSON的参数 
			'args'		: {},	# 来自URL的参数
			'data'		: None,	# 请求中附带的原始数据
			'parameters'	: {},	# 处理后的实际传入参数，包括表单和JSON，JSON优先
			'token'		: '',	# 非空则为返回的TOKEN，供前端更新
			'response_code'	: '200',# http状态码
			'response_type'	: 'application/json',# 响应类型
		}

		# 查找路由
		data['route']		= self.get(data['route_name'])
		
		# 没找到路由
		if data['route'] is None:
			data['message'] = f"找不到路由：{data['route_name']}"
			data['result']  = 'ERROR'
			return data
		
		# 该路由无法执行
		if not callable(data['route']["function"]):
			data['message'] = f"路由[{data['route_name']}]函数无法执行"
			data['result']  = 'ERROR'
			return data
		
		# -------- 参数解析 -----------
		data['args']	= data['request'].args
		data['headers']	= data['request'].headers
		data['cookies']	= data['request'].cookies
		data['stream']	= data['request'].stream

		# 解析Content-Type
		content_type	= data['request'].headers.get('Content-Type')
		if content_type.startswith('application/x-www-form-urlencoded'):
			# 只有表单数据
			data['form']	= data['request'].form
		elif content_type.startswith('multipart/form-data'):
			# 表单数据和文件
			data['form']	= data['request'].form
			data['files']	= data['request'].files
		elif content_type.startswith('application/json'):
			# JSON
			data['json']	= data['request'].json

		# 获取websocket_code
		data['parameters']['websocket_code']	= data['request'].headers.get('Websocket-Code')
		# 总是获取附带的原始数据
		data['data']	= data['request'].get_data()

		# json和form合并到parameters，JSON的优先。注意form和json都是ImmutableMultiDict，是不可修改的
		data['parameters'].update(data['form'])
		data['parameters'].update(data['json'])

		# 检查接口所要求的参数
		parameter_missing       = []
		for p in data['route']['parameters_required']:
			if data['parameters'] and p not in data['parameters'].keys():
				parameter_missing.append(p)
		if parameter_missing:
			data['message'] = f"缺少必需的参数：{','.join(parameter_missing)}"
			data['result']  = 'PARAMETER MISSING'
			# 缺少参数
			data['response_code']	= '400'
			return data

		# ------------- 认证处理 -------------
		# 认证的本质是获得user_ID
		if data['route']['authorization_required']:
			# 此路由需要认证
			authorization   = data['request'].headers.get('Authorization')
			
			if use_websocket:
				if 'websocket_code' not in data['parameters']:
					# 需要认证的必须上传websock_code
					data['message'] = f"认证必须要有参数websocket_code"
					data['result']  = 'ERROR'
					# 认证失败
					data['response_code']	= '401'
					return data
				websocket_code  = data['parameters']['websocket_code']

			if not authorization:
				# 不包含Authorization域
				data['message'] = f"认证Header未包含Authorziation"
				data['result']  = 'ERROR'
				# 认证失败
				data['response_code']	= '401'
				return data
			
			authorization   = authorization.split()
			if authorization[0] != 'Bearer' or len(authorization)==1:
				# 必须是Bearer类型的认证，且包含内容
				data['message'] = f"认证Authorziation未包含Bearer"
				data['result']  = 'ERROR'
				# 认证失败
				data['response_code']	= '401'
				return data
			
			# 解析TOKEN，其中必须包含user_ID
			token   = authorization[1] if len(authorization)>1 else None
			try:
				payload = jwt.decode(token, self.token_secret_key, [self.token_algorithm])
				# 解析TOKEN
				data['user_ID']		= payload['user_ID']
								
				# 判断是否超期失效
				expire_seconds	= time.time()-payload['timestamp']
				if expire_seconds>self.token_expire_days*86400:
					# 已经超期失效了
					data['message'] = f"认证TOKEN已失效"
					data['result']  = 'TOKEN EXPIRE'
					# 认证失败
					data['response_code']	= '401'
					return data
				elif expire_seconds>self.token_update_days:
					# 定期更换token
					data['token']	= self.generate_token(data['user_ID'])

			# 解析失败：TOKEN签名错误
			except jwt.ExpiredSignatureError:
				data['message'] 	= f"认证TOKEN签名错误"
				data['result']  	= 'TOKEN ERROR'
				data['response_code']	= '401'
				return data
			
			# 解析失败：非法TOKEN
			except jwt.InvalidTokenError:
				data['message'] 	= f"认证TOKEN非法"
				data['result']  	= 'TOKEN INVALID'
				# 认证失败
				data['response_code']	= '401'
				return data

			# user_ID绑定到websocket_code，redis中WEBSOCKET USER是一个hash类型，每个键是一个websocket_code，对应值为user_ID，0表示未绑定
			if use_websocket:
				# 更新
				self.redis.hset('WEBSOCKET USER', websocket_code, data['user_ID'])
		return data

	## 执行路由，返回响应
	#	data	来自query的返回值
	def response(self, data, start_response):
		# 执行路由, data中的result/message/return_data将会被修改
		print(f"==============response_code: {data['response_code']}")
		if data['route'] and data['response_code']=='200':
			data['route']["function"](data)

		# return_data是返回的数据
		if isinstance(data['return_data'], bytes):
			body	= data['return_data']
		elif data['response_type'] == 'text/html':
			body	= data['return_data'].encode('utf8')
		else:
			return_data	= {
				'result'	: data['result'],
				'message'       : data['message'],
				'data'		: data['return_data'],
			}
			return_data['token']	= data['token']
			body    = bytes(json.dumps(return_data, cls=BackendJsonEncoder), encoding='utf8')

		headers	 = []
		# 增加头部中的body长度字节数
		headers.append(('Content-Length', str(len(body))))
		
		# 使用路由指定的内容类型
		headers.append(('Content-Type', data['response_type']))
		
		# 总是返回状态200
		start_response(data['response_code'], headers)
		return body

# 全局的路由实例
routes = Routes()

# ###################################### 默认路由 ########################################

## 使用密码登录，用户名尝试依次在NAME、IDENTITY、MOBILE、EMAIL、USER里面搜索
@routes.add('/login_password', authorization_required=False, parameters_required=[
	'username',	# 用户名
	'password',	# 密码
])
def API_login_password(route_data):
	global routes

	parameters	= route_data['parameters']

	# 先假定登录失败
	route_data['message']	= "登录失败"
	route_data['result']	= "LOGIN_FAILED"

	# 搜索数据库表获得user_ID
	for field in ['NAME', 'IDENTITY', 'MOBILE', 'EMAIL', 'USER']:
		SQL_string	= f\'\'\'
			SELECT ID, PASSWORD
			FROM USER
			WHERE {field}='{parameters['username']}'
			AND DELETE_TIMESTAMP IS NULL
		\'\'\'
		result	= routes.db.query(SQL_string)
		if result:
			break
	if not result:
		# 没找到结果
		return
	
	salt_shadow	= result[0]['PASSWORD']
	salt		= salt_shadow[:12]
	shadow		= salt_shadow[12:]
	crypted		= crypt.crypt(parameters['password'], salt)
	if crypted==salt_shadow:
		# 密码验证通过
		user_ID	= result[0]['ID']
		route_data['token']	= routes.generate_token(user_ID)
		route_data['message']	= '登录成功'

## 使用微信登录
@routes.add('/login_wechat', authorization_required=False, parameters_required=[
	'wechat_code',		# 微信code
	'websocket_code',	# websocket code
])
def API_login_wechat(route_data):
	global routes

	parameters	= route_data['parameters']
	wechat_code	= parameters['wechat_code']
	websocket_code	= parameters['websocket_code']
	app_ID		= 'wx439a3874a5b28c4f'
	app_secret	= '613bcdf2937396290a9a550aedfcb2d7'

	url		= f\'\'\'https://api.weixin.qq.com/sns/oauth2/access_token?appid={app_ID}&secret={app_secret}&code={wechat_code}&grant_type=authorization_code\'\'\'
	response	= requests.get(url)
	if 'openid' not in response.json():
		print(f'获取openid失败: {response.json()}')
		route_data['response_code']	= '401'
		route_data['result']		= 'LOGIN_FAILED'
		route_data['message']		= '获取openid失败'
		return
	open_ID	= response.json()['openid']
	# 是否已有该用户的open_ID
	exist_user	= routes.db.query(f\'\'\'
		SELECT
			*
		FROM USER
		WHERE
			OPENID='{open_ID}'
		AND
			DELETE_TIMESTAMP IS NULL
	\'\'\')
	if not exist_user:
		# 创建用户信息
		exist_user	= routes.db.insert('USER', {
			'OPENID'	: open_ID,
			'NAME'		: '无',
			'IDENTITY'	: '无',
			'REGION'	: '无',
			'MOBILE'	: '无',
			'EMAIL'		: '无',
			'TYPE'		: '无',
		})
	user_information	= exist_user[0]

	# 获取用户组和权限
	get_login_user_permission(user_information['ID'])

	# 生成token
	timestamp				= time.time()
	token					= jwt.encode({
		'timestamp'		: timestamp,
		'user_ID'		: user_information['ID']
	}, routes.token_secret_key, algorithm=routes.token_algorithm)
	# 推送token到客户端
	message	= f"TOKEN {websocket_code} {token}"
	redis_client.publish('WEBSOCKET SERVER', message)
	
	# 推送用户信息到客户端
	data	= json.dumps({
		'ID'		: user_information['ID'],
		'NAME'		: user_information['NAME'],
	}, ensure_ascii=False)
	message	= f"USER {websocket_code} {data}"
	redis_client.publish('WEBSOCKET SERVER', message)

	route_data['data']	= {}
	route_data['message']	= '登录成功'
	route_data['result']	= 'LOGIN_SUCCESS'
	
## 微信扫码获取wechat_code
@routes.add('/authorize_redirect', authorization_required=False)
def API_authorize_redirect(route_data):
	redirect_URL	= route_data['args'].get('redirect_URL', '')
	app_ID		= route_data['args'].get('app_ID', '')

	# 读取template/authorize_redirect.html
	with open('template/authorize_redirect.html', 'r', encoding='utf-8') as f:
		html_content	= f.read()
		html_content	= html_content.replace('$$redirect_URL$$', redirect_URL)
		html_content	= html_content.replace('$$app_ID$$', app_ID)
		route_data['return_data']	= html_content
	print(f'redirect_URL: {redirect_URL}')
	print(f'app_ID: {app_ID}')

	route_data['response_type']	= 'text/html'
	
## 微信扫码返回授权页面
@routes.add('/authorize_scan', authorization_required=False)
def API_authorize_scan(route_data):
	websocket_code	= route_data['args'].get('websocket_code', '')
	app_ID		= route_data['args'].get('app_ID', '')

	# 读取template/authorize_scan_page.html
	with open('template/authorize_scan_page.html', 'r', encoding='utf-8') as f:
		html_content	= f.read()
		html_content	= html_content.replace('$$websocket_code$$', websocket_code)
		html_content	= html_content.replace('$$app_ID$$', app_ID)
		route_data['return_data']	= html_content
	route_data['response_type']	= 'text/html'
'''
