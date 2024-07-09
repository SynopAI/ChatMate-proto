from dotenv import load_dotenv
import os
import openai
import webbrowser

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key: 
    raise ValueError("API key not found. Please set it in the .env file.")

client = openai.OpenAI(api_key=api_key)

GPT_MODEL = "gpt-4o"

def open_browser_search(query):
    # 使用Google搜索
    search_url = f"https://s.jina.ai/{query}"
    # 打开默认浏览器并进行搜索
    webbrowser.open(search_url)
    print(f"已执行打开浏览器搜索{query}")
    return f"Searched for {query} on Google."

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
    }
]

user_input = input()

messages = [{
    "role": "user",
    "content": user_input
}]

response = client.chat.completions.create(
    model=GPT_MODEL,
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

# Append the message to messages list
response_message = response.choices[0].message 
messages.append(response_message)

# print(response_message)

# Step 2: determine if the response from the model includes a tool call.   
tool_calls = response_message.tool_calls
if tool_calls:
    # If true the model will return the name of the tool / function to call and the argument(s)  
    tool_call_id = tool_calls[0].id
    tool_function_name = tool_calls[0].function.name
    tool_query_string = eval(tool_calls[0].function.arguments)['query']
    
    # Step 3: Call the function and retrieve results. Append the results to the messages list.      
    if tool_function_name == 'open_browser_search':
        results = open_browser_search(tool_query_string)
        
        messages.append({
            "role":"tool", 
            "tool_call_id":tool_call_id, 
            "name": tool_function_name, 
            "content":results
        })
        
        # Step 4: Invoke the chat completions API with the function response appended to the messages list
        # Note that messages with role 'tool' must be a response to a preceding message with 'tool_calls'
        model_response_with_function_call = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        print(model_response_with_function_call.choices[0].message.content)
    else: 
        print(f"Error: function {tool_function_name} does not exist")
else: 
    # Model did not identify a function to call, result can be returned to the user 
    print(response_message.content) 