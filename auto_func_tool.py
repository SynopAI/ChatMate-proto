import json
import webbrowser
from flask import Flask, request, jsonify

app = Flask(__name__)

def open_browser_search(query):
    # 使用Google搜索
    search_url = f"https://www.google.com/search?q={query}"
    # 打开默认浏览器并进行搜索
    webbrowser.open(search_url)
    return f"Searched for {query} on Google."

@app.route('/')
def index():
    return "Welcome to the Auto Function Tool API. Use the /tool/open_browser_search endpoint to perform searches."

@app.route('/tool/open_browser_search', methods=['POST'])
def api_open_browser_search():
    data = request.get_json()
    query = data.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    result = open_browser_search(query)
    return jsonify({'result': result})

if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(host='0.0.0.0', port=5001)