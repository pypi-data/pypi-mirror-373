#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
独立测试request_url方法的脚本
不依赖fastmcp库，只测试网络请求功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 简化版本的request_url函数，只保留核心功能
import requests

def request_url(url, method='GET', cookie=None, headers=None, data=None, params=None, json=None, timeout=30):
    """
    定义一个方法，请求任意网络URL，支持多种HTTP方法和完整的请求头配置
    
    Args:
        url (str): 要请求的URL
        method (str, optional): HTTP请求方法，默认为'GET'
        cookie (str, optional): Cookie字符串
        headers (dict, optional): 请求头字典
        data (dict, optional): 表单数据
        params (dict, optional): URL查询参数
        json (dict, optional): JSON数据，用于发送JSON请求
        timeout (int, optional): 请求超时时间（秒），默认为30秒
    
    Returns:
        dict: 包含响应信息的字典，包括状态码、响应头和响应内容
              失败时返回None
    """
    try:
        # 构建请求头
        request_headers = headers.copy() if headers else {}
        
        # 如果提供了Cookie，将其添加到请求头中
        if cookie:
            request_headers['Cookie'] = cookie
            
        # 如果提供了JSON数据且未设置Content-Type，则设置默认Content-Type
        if json is not None and 'Content-Type' not in request_headers:
            request_headers['Content-Type'] = 'application/json'
        
        # 打印请求信息
        print(f"请求URL: {url}")
        print(f"请求方法: {method}")
        print(f"请求头: {request_headers}")
        if params:
            print(f"查询参数: {params}")
        if data:
            print(f"表单数据: {data}")
        if json is not None:
            print(f"JSON数据: {json}")
        print("-" * 50)
        
        # 支持的HTTP方法
        method = method.upper()
        
        # 根据不同方法发送请求
        if method == 'GET':
            response = requests.get(url, headers=request_headers, params=params, timeout=timeout)
        elif method == 'POST':
            if json is not None:
                response = requests.post(url, headers=request_headers, json=json, params=params, timeout=timeout)
            else:
                response = requests.post(url, headers=request_headers, data=data, params=params, timeout=timeout)
        elif method == 'PUT':
            if json is not None:
                response = requests.put(url, headers=request_headers, json=json, timeout=timeout)
            else:
                response = requests.put(url, headers=request_headers, data=data, timeout=timeout)
        elif method == 'DELETE':
            response = requests.delete(url, headers=request_headers, timeout=timeout)
        elif method == 'HEAD':
            response = requests.head(url, headers=request_headers, timeout=timeout)
        elif method == 'OPTIONS':
            response = requests.options(url, headers=request_headers, timeout=timeout)
        elif method == 'PATCH':
            if json is not None:
                response = requests.patch(url, headers=request_headers, json=json, timeout=timeout)
            else:
                response = requests.patch(url, headers=request_headers, data=data, timeout=timeout)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")
        
        # 打印响应信息
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print("-" * 50)
        
        # 构建返回结果
        result = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.text,
            "encoding": response.encoding,
            "url": response.url
        }
        
        # 如果响应是JSON格式，也解析JSON内容
        try:
            result["json"] = response.json()
        except:
            result["json"] = None
            
        return result
    except requests.exceptions.Timeout:
        print(f"请求URL超时: {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"请求URL失败: {e}")
        return None
    except ValueError as e:
        print(f"参数错误: {e}")
        return None

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

if __name__ == "__main__":
    test_get_request()
    test_post_with_headers()
    test_custom_headers()
    print("所有测试完成!")