from	redis				import Redis
from	urllib				import parse
from	datetime			import datetime, timedelta
from	wechatpy.oauth			import WeChatOAuth
from	wechatpy.session.redisstorage	import RedisStorage
import	wechatpy
import	functools
import	random
import	string

## 微信接口类
class  SpiritLongWechat(object):
	color_primary	= '#173177'	# 主要颜色
	color_warning	= '#8B0000'	# 警告颜色

	## 初始化
	#	appid			公众号APPID
	#	secret			公众号secret
	#	redis_session_url	REDIS连接url
	#	web_base_url		网页基础路径
	# ''
	def __init__(self, appid, secret, redis_session_url, web_base_url):
		# 微信公众号对象
		self.client	= wechatpy.client.WeChatClient(
			appid,
			secret,
			session	= RedisStorage(
				Redis.from_url(redis_session_url),
				prefix	= appid
			)
		)

		# 类属性
		self.appid		= appid
		self.web_base_url	= web_base_url
	
	## jssdk配置
	#	url	待签名的url
	# ''
	def jssdk_config(self, url):
		# 被使用一次的非重复的随机数值，15位的随机树字和ascii码
		nonce_str	= ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(15))
		# 当前时间
		timestamp	= int(datetime.now().timestamp())

		# 微信公众号调用微信JS接口的临时票据
		jsapi_ticket	= self.client.jsapi.get_jsapi_ticket()

		# 微信签名
		signature	= self.client.jsapi.get_jsapi_signature(
			nonce_str,
			jsapi_ticket,
			timestamp,
			url
		)

		# 返回对应的配置参数
		return {
			"url"		: url,
			"appid"		: self.appid,
			"nonceStr"	: nonce_str,
			"timestamp"	: timestamp,
			"signature"	: signature
		}
	
	## 装饰器：捕获发送模板消息异常
	#	method	方法
	# wrapper
	def template_exception(method):
		@functools.wraps(method)
		def wrapper(*args, **kwargs):
			try:
				return method(*args, **kwargs)
			except Exception as e:
				print("++++++ 微信公众号模板消息异常 ++++++", e)
				return None
		return wrapper

	## 发送模板消息
	#	openid		微信的openid
	#	template_id	发送模板的模板id
	#	data		发送的数据
	#	url		web页面链接
	#	pagepath	小程序页面路径
	# ''
	@template_exception
	def send_template(self, openid, template_id, data, url, pagepath):
		if url is not None:
			url	= self.web_base_url+url
		miniprogram	= None

		# 跳转小程序
		if pagepath is not None:
			miniprogram	= {
				"appid"		: self.appid,
				"pagepath"	: "pages/start/index?url=/"+parse.quote(pagepath)
			}

		return self.client.message.send_template(openid, template_id, data, url, miniprogram)

## 调试/测试代码
if __name__ == '__main__':
	WECHAT_APPID		= "wx"
	WECHAT_SECRET		= ""
	WECHAT_SESSION_URL	= "redis://127.0.0.1:6379/2"
	WECHAT_BASE_URL		= "https://spiritlong-exon.com"

	# 调用库
	SL_wechat		= SpiritLongWechat(WECHAT_APPID, WECHAT_SECRET, WECHAT_SESSION_URL, WECHAT_BASE_URL)

	############################## 模板消息配置函数 ###################################

	## 登录成功提醒通知
	#	openid		用户的openid
	#	username	用户名
	#	login_mode	登录模式
	#	remark		备注
	#	url		点进去的链接
	#	pagepath	
	# ''
	def login_success(openid, username, login_mode, remark="", url="", pagepath=None):
		data	= {
			"first"		: {
				"value"	: "您已成功登录系统！",
				"color"	: SL_wechat.color_primary
			},
			"keyword1"	: {
				"value"	: username,
				"color"	: SL_wechat.color_primary
			},
			"keyword2"	: {
				"value"	: login_mode,
				"color"	: SL_wechat.color_primary
			},
			"keyword3"	: {
				"value"	: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
				"color"	: SL_wechat.color_warning
			},
			"remark"	: {
				"value"	: remark+"点击查看详情",
				"color"	: SL_wechat.color_primary
			}
		}

		template_id	= "r5X0x7oooq09uGkDdmzc832kYJkcMs-dvRDPgRoTKeE"
		
		return SL_wechat.send_template(openid, template_id, data, url, pagepath)

	login_success("", "测试", "账号")