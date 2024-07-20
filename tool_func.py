import requests
import webbrowser
import urllib.parse

def open_browser_search(query):
    # 对查询字符串进行URL编码
    encoded_query = urllib.parse.quote(query, encoding='utf-8')
    # 使用Google搜索
    search_url = f"https://www.google.com/search?q={encoded_query}"
    # 打开默认浏览器并进行搜索
    webbrowser.open(search_url)
    print(f"已执行打开浏览器搜索{query}")
    return f"Searched for {query} on Google."

def grab_web(query):
    # 检查输入是否为URL
    if query.startswith("http://") or query.startswith("https://"):
        # 使用Reader的Read功能
        reader_url = f"https://r.jina.ai/{query}"
    else:
        # 对查询字符串进行URL编码
        encoded_query = urllib.parse.quote(query, encoding='utf-8')
        # 使用Reader的Search功能
        reader_url = f"https://s.jina.ai/{encoded_query}"
    
    # 发起HTTP请求
    response = requests.get(reader_url)
    
    if response.status_code == 200:
        return response.text
    else:
        return f"Error: Unable to fetch data, status code {response.status_code}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "open_browser_search",
            "description": "Open a browser and search the query on Google",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to use on Google",
                    },
                },
                "required": ["query"],
            },
        }
    },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "grab_web",
    #         "description": "Fetches LLM-friendly string data from a URL or search query using Jina Reader API",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "query": {
    #                     "type": "string",
    #                     "description": "The URL or search query to fetch LLM-friendly data from",
    #                 },
    #             },
    #             "required": ["query"],
    #         },
    #     }
    # }
]

def call_tool_function(tool_function_name, tool_query_string):
    if tool_function_name == 'open_browser_search':
        return open_browser_search(tool_query_string)
    if tool_function_name == 'grab_web':
        return grab_web(tool_query_string)
    else:
        return f"Error: function {tool_function_name} does not exist"