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
# @brief	SpringBoot相关工具
##################################################################

import	os
import	SpiritLong_utility
import	webframe_SpringBoot_pom_xml

## 准备SpringBoot基本框架
def generate_basic_frame(path, project_name='webframe'):
	# 创建该目录
	os.makedirs(path, exist_ok=True)

	# --------------------- .vscode ---------------------
	os.makedirs(f"{path}/.vscode", exist_ok=True)

	# .vscode/lauch.json
	with open(f"{path}/.vscode/lauch.json", "w") as f:
		f.write('''{
	"configurations": [
		{
			"type"		: "java",
			"name"		: "WebframeApplication",
			"request"	: "launch",
			"mainClass"	: "webframe.WebframeApplication",
			"projectName"	: "webframe"
		},
		{
			"type"		: "java",
			"name"		: "WebframeApplication",
			"request"	: "launch",
			"mainClass"	: "WebframeApplication",
			"projectName"	: "webframe"
		},
		{
			"type"		: "java",
			"name"		: "Spring Boot-WebframeApplication<webframe>",
			"request"	: "launch",
			"cwd"		: "${workspaceFolder}",
			"mainClass"	: "com.spiritlong.webframe.WebframeApplication",
			"projectName"	: "webframe",
			"args"		: "",
			"envFile"	: "${workspaceFolder}/.env"
		}
	]
}
''')
	# .vscode/settings.json
	with open(f"{path}/.vscode/settings.json", "w") as f:
		f.write('''{
	"java.configuration.updateBuildConfiguration": "interactive",
	"java.compile.nullAnalysis.mode": "disabled"
}
''')
	
	# --------------------- src/main ---------------------
	os.makedirs(f"{path}/src/main/java/webframe/DTO", 		exist_ok=True)
	os.makedirs(f"{path}/src/main/java/webframe/mapper", 		exist_ok=True)
	os.makedirs(f"{path}/src/main/java/webframe/service",		exist_ok=True)
	os.makedirs(f"{path}/src/main/java/webframe/controller",	exist_ok=True)

	# /src/main/java/webframe/DTO/DTO_demo.java
	# 示范DTO
	with open(f"{path}/src/main/java/webframe/DTO/DTO_demo.java", "w") as f:
		f.write(r'''
package webframe.DTO;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class DTO_demo {
	public	Integer	group_ID;
	public	String	abc_DEF;
	public	String	fghCDEF;
	public	String	DEF_aaa;
}
''')
	# /src/main/java/webframe/controller/Controller.java
	# 这是路由所在
	with open(f"{path}/src/main/java/webframe/controller/Routes.java", "w") as f:
		f.write(r'''
package webframe.controller;

import	org.springframework.web.bind.annotation.PostMapping;
import	org.springframework.web.bind.annotation.RequestBody;
import	org.springframework.web.bind.annotation.ResponseBody;
import	org.springframework.web.bind.annotation.RestController;
import	webframe.DTO.*;  

@RestController
public class Routes {
	@PostMapping("/test_DTO")
	@ResponseBody
	public DTO_demo test_DTO(@RequestBody DTO_demo test_parameter) {
		System.out.printf("DTO get: %s\n", test_parameter.toString());
		return test_parameter;
	}
}
''')
		
	# /src/main/java/webframe/service/ServiceDemo.java
	# 服务示范
	with open(f"{path}/src/main/java/webframe/service/ServiceDemo.java", "w") as f:
		f.write('''	
package webframe.service;
	    
import org.springframework.stereotype.Service;

@Service
public class ServiceDemo {
	// 示范服务
	public String service_convert(String s)
	{
		return s.toUpperCase();
	}
}
''')

	# /src/main/java/webframe/Application.java
	# 框架入口，main所在
	with open(f"{path}/src/main/java/webframe/Application.java", "w") as f:
		f.write('''	
package webframe;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
	public static void main(String[] args){
		SpringApplication.run(Application.class, args);
	}

}
''')
	
	# /src/main/java/webframe/ApplicationConfig.java
	# 配置使用的Bean定义
	with open(f"{path}/src/main/java/webframe/ApplicationConfig.java", "w") as f:
		f.write('''
package webframe;

import	org.springframework.context.annotation.Bean;
import	org.springframework.context.annotation.Configuration;
import	org.springframework.context.annotation.Primary;
import	org.springframework.http.converter.json.Jackson2ObjectMapperBuilder;
import	com.fasterxml.jackson.databind.MapperFeature;
import	com.fasterxml.jackson.databind.ObjectMapper;

// 通过定义Bean来实现配置，Bean的含义是获得唯一的全局对象，修饰的名字并不重要
@Configuration
public class ApplicationConfig {
	// ObjectMapper的手动定义，按推荐使用builder来实现
	@Bean
	@Primary
	public ObjectMapper	object_mapper(Jackson2ObjectMapperBuilder builder)
	{
		return builder
			// 转换时可以不提供全部属性
			.failOnEmptyBeans(false)
			// 忽略未知的属性
			.failOnUnknownProperties(false)
			// 接收属性时忽略大小写，这使得JSON中的key名称都被考虑而不是被SpringBoot的大小写要求丢弃
			.featuresToEnable(MapperFeature.ACCEPT_CASE_INSENSITIVE_PROPERTIES)
			// 禁止自动转换getter/setter
			.autoDetectGettersSetters(false)
			.build();
	}
}

''')
	
	os.makedirs(f"{path}/src/main/resources",	exist_ok=True)	
	# /src/main/application.properties
	# 全局配置文件
	with open(f"{path}/src/main/resources/application.properties", "w") as f:
		f.write(f'''# 配置
# 应用服务WEB 访问端口
server.port	= 8080
''')
	os.makedirs(f"{path}/src/test/java/webframe", exist_ok=True)
	# /src/test/ApplicationTests
	# 单元测试
	with open(f"{path}/src/test/java/webframe/ApplicationTests.java", "w") as f:
		f.write(r'''
package webframe;

import	org.junit.jupiter.api.Test;
import	org.springframework.beans.factory.annotation.Autowired;
import	org.springframework.boot.test.context.SpringBootTest;
import	webframe.service.*;
	  
@SpringBootTest
class ApplicationTests {
	@Test
	void contextLoads() {

	}
	
	// 自动创建对象
	@Autowired
	private	ServiceDemo	service_DEMO;

	// 单元测试示范
	@Test
	public	void test_DTO_demo()
	{
		String result	= service_DEMO.service_convert("fdsafdFDFd");
		System.out.printf("hello %s\n", result);
	}
}
''')
	
	# pom.xml
	with open(f"{path}/pom.xml", "w") as f:
		f.write(webframe_SpringBoot_pom_xml.content.replace("{project_name}", f"{project_name}"))
			
	
	# /src/main/java/webframe/DTO/DTO_demo
	# DTO示范
	with open(f"{path}/src/main/resources/application.properties", "w") as f:
		f.write('''package webframe.DTO;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class DTO_demo {
	public	String	 cdeFgh;
	public	String	 FdeFgh;
	public	String	 VIN;
	public	Integer	 car_model_ID;
	public	Integer	 material_ID;
	public	String	 product_time;
	public	String	 Abc;
}
''')	
		
# 脚本执行
if __name__ == '__main__':
	generate_basic_frame("./backend", 'OTA')

	
	# # 给文件增加版权说明
	# SpiritLong_utility.copyright(__file__, author='arthuryang')
