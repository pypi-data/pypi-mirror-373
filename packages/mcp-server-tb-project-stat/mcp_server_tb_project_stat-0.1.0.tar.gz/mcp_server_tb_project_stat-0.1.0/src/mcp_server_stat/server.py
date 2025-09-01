from fastmcp import FastMCP
import os
import requests

mcp = FastMCP(name="My First MCP Server")

@mcp.tool
def add(a: int, b: int) -> int:
    """Adds two integer numbers together."""
    return a + b


@mcp.tool
def multiply(a: int, b: int) -> int:
    """multiply two integer numbers together."""
    return a * b    

# @mcp.tool(name="bye", description="Say bye")
# def bye(name: str):
#     print(f"Bye {name}")

# @mcp.tool(name="echo", description="Echo")
# def echo(text: str):
#     print(text)


@mcp.tool(name="getProjectData", description="Get project data")
def getProjectData(projectId: str, userId: str, data: dict) -> dict:
    """Get project data."""
    url = "https://www.teambition.com/api/boards/soa1/project/" + projectId + "/task/statistics"
    headers = {
        "Cookie": "X-Canary=prepub-dev-l",
        "userid": userId,
        "debug_mode": "true"
    }
    # data = {
    #     "indicators": [{
    #     "column":"taskcount",
    #     "function": "count"
    #     }]
    # }

    result = request_url(url, method="POST", headers=headers, json=data)
    return result["json"] 
      

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

def run_server():
    mode = os.getenv("MODE", "").lower()
    if mode == "sse":
        mcp.run(transport="sse", port=8000, path="/sse")
    elif mode == "streamable-http":
        mcp.run(transport="streamable-http", port=8000, path="/mcp")
    else:
        mcp.run()




def main():
    ####test_request()

    ####projectData = getProjectData("665e8d6c692ed3670172116b", "621edaf3c74590c90e5b468d")

    # print("-------------------------------------------------")
    # print(projectData)
#    print("Hello from uv-python-mcp!")
    run_server()


if __name__ == "__main__":
    main()