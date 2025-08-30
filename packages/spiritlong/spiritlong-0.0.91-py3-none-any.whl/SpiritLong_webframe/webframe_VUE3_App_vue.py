content	= '''<!--------------------------------------------------------------------
-              ____     _     _ __  __                 
-             / __/__  (_)___(_) /_/ /  ___  ___  ___ _
-            _\\ \\/ _ \\/ / __/ / __/ /__/ _ \\/ _ \\/ _ `/
-           /___/ .__/_/_/ /_/\\__/____/\\___/_//_/\\_, / 
-              /_/                              /___/  
- 
- Copyright (c) 2025 Chongqing Spiritlong Technology Co., Ltd.
- All rights reserved.
- @author	arthuryang
- @brief	主框架
--------------------------------------------------------------------->

<template>
	<!-- 登录 -->
	<div :style="[style_fullscreen, style_login]" v-show="login_enabled">
		<Login :title='login_title' :QR_code_string="QR_code_string" @login-button="login_button_handler"/>
	</div>

	<!-- 全局消息 -->
	<div :style="[style_fullscreen, style_viewport_message]" v-show="viewport_message_show">
		<p>message{{ store.viewport_message }}</p>
		<button type="button" @click="viewport_message_show	= false" style="height:30px;width:200px">隐藏全局消息</button>
	</div>

	<!-- 页面 -->
	<div :style="[style_PC]">
		<header :style="[style_PC_header]">
			<webframe_header :title="heading_text" :logo="logo_filename"/>
		</header>
		<aside :style="[style_PC_aside]">
			<webframe_sider :menu_items="menu_items" active_menu="1"/>
		
		</aside>
		<main :style="[style_PC_main]">
			<router-view></router-view>
		</main>
	</div>
</template>

<script setup>
// VUE基本
import	{ reactive }		from 'vue'
import	{ ref, onMounted }	from 'vue'
// store
import	{ storeToRefs }		from "pinia"
import	{ main_store }		from './main.js'
// webframe
import	{API}			from './webframe'
import	application_config	from './application_config'
// 框架组件
import	Login			from './components/login.vue'
import	webframe_header		from './components/webframe_header.vue'
import	webframe_sider		from './components/webframe_sider.vue'

const	store			= main_store();
const	{
	login_enabled, 
	viewport_message_show, 
}				= storeToRefs(store);

// 登录二维码
// TODO 随时间变化
const	QR_code_string		= ref('')
const base_URL		= application_config.base_URL;
const app_ID		= application_config.wechat_app_ID;
const websocket_code	= localStorage.getItem('websocket_code');
const redirect_URL	= encodeURIComponent(base_URL + '/API/authorize_scan?websocket_code=' + websocket_code + '&app_ID=' + app_ID);
QR_code_string.value	= base_URL + '/API/authorize_redirect?redirect_URL=' + redirect_URL + '&app_ID=' + app_ID;

let	login_title		= ref('登录提示')
let	heading_text		= ref(application_config.heading_text)
let	logo_filename		= ref(application_config.logo_filename)

// 登录处理
const	login_button_handler	= (username, password)=>{
	API('/login_password', {
		username,
		password
	}).then((data)=>{
		login_enabled.value	= false
		console.log('登录成功', data)
	})
}

// 菜单数据
// 菜单数据结构：
// [{
// 	name		: 菜单名称，必传
// 	icon		: 菜单图标，可选
// 	children	: 子菜单，可选
// 	icon_width	: 菜单图标宽度，可选
// 	icon_margin	: 菜单图标外边距，可选
// 	icon_color	: 菜单图标颜色，可选
// }]

const menu_items = reactive([
	{
		name: '任务',
		path: '/task'
	},
	{
		name: '事务',
		path: '/job'
	},
	{
		name: '用户管理',
		path: '/user'
	},
	{
		name: '权限管理',
		path: '/permission'
	},
	{
		name: '审批管理',
		path: '/approval'
	},
	{
		name: '日志管理',
		path: '/log'
	}
])

// ------------ style ---------------
// 注意：style应用时后面的属性会覆盖前面
const	style_login	= reactive({
	justifyContent	: 'center',
	alignItems	: 'center',
	zIndex		: '1',
});

const	style_viewport_message	= reactive({
	justifyContent	: 'center',
	alignItems	: 'center',
	zIndex		: '2',
});

const	style_fullscreen	= reactive({
	display		: 'flex',
	position	: 'absolute',
	left		: '0px',
	width		: '100%',
	top		: '0px',
	height		: '100%',
	backgroundColor	: 'white',
	zIndex		: '0',
});

const	style_PC	= reactive({
	width		: '100%',
	height		: '100vh',
	display		: 'grid',
	gridTemplateAreas	: `
		"header header"
		"aside main"
	`,
	gridTemplateRows	: 'auto 1fr',
	gridTemplateColumns	: 'auto 1fr',
	padding		: '0px',
	margin		: '0px',
	zIndex		: '0',
	overflow	: 'hidden'
});

const	style_PC_header	= reactive({
	width		: '100%',
	gridArea	: 'header'
});

// 新增 PC 布局的 aside 和 main 样式
const style_PC_aside = reactive({
	gridArea	: 'aside',
	height		: '100%',
	overflow	: 'hidden'
});

const style_PC_main = reactive({
	gridArea	: 'main',
	background	: '#f5f5f5',
	overflow	: 'auto',
	height		: '100%',
	boxSizing	: 'border-box',
});
</script>
'''