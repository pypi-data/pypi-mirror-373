#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试request_url方法的脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import request_url

def test_get_request():
    """测试GET请求"""
    print("=== 测试GET请求 ===")
    result = request_url("http://httpbin.org/get")
    if result:
        print("状态码:", result["status_code"])
        print("响应内容长度:", len(result["content"]))
        if result["json"]:
            print("服务器看到的请求头:")
            for key, value in result["json"].get("headers", {}).items():
                print(f"  {key}: {value}")
    else:
        print("GET请求失败")
    print()

def test_post_with_headers():
    """测试带请求头的POST请求"""
    print("=== 测试带请求头的POST请求 ===")
    headers = {
        "User-Agent": "FastMCP Test Client 1.0",
        "Accept": "application/json",
        "X-Custom-Header": "CustomValue"
    }
    
    data = {
        "name": "FastMCP",
        "version": "1.0",
        "test": "header_support"
    }
    
    result = request_url(
        "http://httpbin.org/post", 
        method="POST", 
        headers=headers,
        json=data
    )
    
    if result:
        print("状态码:", result["status_code"])
        if result["json"]:
            print("服务器接收到的请求头:")
            for key, value in result["json"].get("headers", {}).items():
                print(f"  {key}: {value}")
            print("服务器接收到的JSON数据:")
            print(" ", result["json"].get("json"))
    else:
        print("POST请求失败")
    print()

def test_put_request():
    """测试PUT请求"""
    print("=== 测试PUT请求 ===")
    data = {
        "update": "test data",
        "field": "value"
    }
    
    result = request_url(
        "http://httpbin.org/put",
        method="PUT",
        json=data
    )
    
    if result:
        print("状态码:", result["status_code"])
        if result["json"]:
            print("服务器接收到的数据:", result["json"].get("json"))
    else:
        print("PUT请求失败")
    print()

def test_custom_headers():
    """测试自定义请求头"""
    print("=== 测试自定义请求头 ===")
    headers = {
        "Authorization": "Bearer token123",
        "Content-Type": "application/json",
        "X-API-Key": "api_key_456"
    }
    
    result = request_url(
        "http://httpbin.org/headers",
        method="GET",
        headers=headers
    )
    
    if result:
        print("状态码:", result["status_code"])
        if result["json"]:
            print("服务器看到的请求头:")
            for key, value in result["json"].get("headers", {}).items():
                print(f"  {key}: {value}")
    else:
        print("自定义请求头测试失败")
    print()



 def test_request():
        # 测试GET请求
    result = request_url("http://httpbin.org/get")
    if result:
        print("GET请求成功，状态码:", result["status_code"])
        print("响应内容长度:", len(result["content"]))
    else:
        print("GET请求失败")
    
    # 测试带请求头的POST请求
    headers = {
        "User-Agent": "FastMCP Client 1.0",
        "Accept": "application/json"
    }
    
    data = {
        "name": "FastMCP",
        "version": "1.0"
    }
    
    result = request_url(
        "http://httpbin.org/post", 
        method="POST", 
        headers=headers,
        json=data
    )
    
    if result:
        print("POST请求成功，状态码:", result["status_code"])
        if result["json"]:
            print("JSON响应:", result["json"])
    else:
        print("POST请求失败")


    print("test boards api")


    url = "https://www.teambition.com/api/boards/soa1/project/665e8d6c692ed3670172116b/task/statistics"
    headers = {
        "Cookie": "X-Canary=prepub-dev-l",
        "userid": "621edaf3c74590c90e5b468d",
        "debug_mode": "true"
    }
    data = {
    "indicators": [
        {
            "column":"taskcount",
            "function": "count"
        }]
    }

    result = request_url(url, method="POST", headers=headers, json=data)  
    print(result)
    if result:
        print("POST请求成功，状态码:", result["status_code"])
        if result["json"]:
            print("JSON响应:", result["json"])
    else:
        print("POST请求失败")  
   

if __name__ == "__main__":
    test_get_request()
    test_post_with_headers()
    test_put_request()
    test_custom_headers()
    print("所有测试完成!")