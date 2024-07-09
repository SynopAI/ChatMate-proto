import requests
from concurrent.futures import ThreadPoolExecutor
import tiktoken

# Provided functions for chunking and threading
def split_into_chunks(text, tokens, llm, overlap):
    try:
        encoding = tiktoken.encoding_for_model(llm.model)
        tokenized_text = encoding.encode(text)
        chunks = []
        for i in range(0, len(tokenized_text), tokens - overlap):
            chunk = encoding.decode(tokenized_text[i : i + tokens])
            chunks.append(chunk)
    except Exception:
        chunks = []
        for i in range(0, len(text), tokens * 4 - overlap):
            chunk = text[i : i + tokens * 4]
            chunks.append(chunk)
    return chunks

def chunk_responses(responses, tokens, llm):
    try:
        encoding = tiktoken.encoding_for_model(llm.model)
        chunked_responses = []
        current_chunk = ""
        current_tokens = 0

        for response in responses:
            tokenized_response = encoding.encode(response)
            new_tokens = current_tokens + len(tokenized_response)

            if new_tokens > tokens:
                if current_tokens == 0 or len(tokenized_response) > tokens:
                    chunked_responses.append(response)
                else:
                    chunked_responses.append(current_chunk)
                    current_chunk = response
                    current_tokens = len(tokenized_response)
                continue

            current_chunk += "\n\n" + response if current_chunk else response
            current_tokens = new_tokens

        if current_chunk:
            chunked_responses.append(current_chunk)
    except Exception:
        chunked_responses = []
        current_chunk = ""
        current_chars = 0

        for response in responses:
            new_chars = current_chars + len(response)

            if new_chars > tokens * 4:
                if current_chars == 0 or len(response) > tokens * 4:
                    chunked_responses.append(response)
                else:
                    chunked_responses.append(current_chunk)
                    current_chunk = response
                    current_chars = len(response)
                continue

            current_chunk += "\n\n" + response if current_chunk else response
            current_chars = new_chars

        if current_chunk:
            chunked_responses.append(current_chunk)
    return chunked_responses

def fast_llm(llm, system_message, user_message):
    old_messages = llm.interpreter.messages
    old_system_message = llm.interpreter.system_message
    try:
        llm.interpreter.system_message = system_message
        llm.interpreter.messages = []
        response = llm.interpreter.chat(user_message)
    finally:
        llm.interpreter.messages = old_messages
        llm.interpreter.system_message = old_system_message
        return response[-1].get("content")

def query_map_chunks(chunks, llm, query):
    with ThreadPoolExecutor() as executor:
        responses = list(
            executor.map(lambda chunk: fast_llm(llm, query, chunk), chunks)
        )
    return responses

def query_reduce_chunks(responses, llm, chunk_size, query):
    while len(responses) > 1:
        chunks = chunk_responses(responses, chunk_size, llm)

        with ThreadPoolExecutor() as executor:
            summaries = list(
                executor.map(lambda chunk: fast_llm(llm, query, chunk), chunks)
            )

    return summaries[0]

class Ai:
    def __init__(self, computer):
        self.computer = computer

    def chat(self, text):
        messages = [
            {
                "role": "system",
                "type": "message",
                "content": "You are a helpful AI assistant.",
            },
            {"role": "user", "type": "message", "content": text},
        ]
        response = ""
        for chunk in self.computer.interpreter.llm.run(messages):
            if "content" in chunk:
                response += chunk.get("content")
        return response

    def query(self, text, query, custom_reduce_query=None):
        if custom_reduce_query == None:
            custom_reduce_query = query

        chunk_size = 2000
        overlap = 50

        chunks = split_into_chunks(
            text, chunk_size, self.computer.interpreter.llm, overlap
        )

        responses = query_map_chunks(chunks, self.computer.interpreter.llm, query)

        response = query_reduce_chunks(
            responses, self.computer.interpreter.llm, chunk_size, custom_reduce_query
        )

        return response

    def summarize(self, text):
        query = "You are a highly skilled AI trained in language comprehension and summarization. I would like you to read the following text and summarize it into a concise abstract paragraph. Aim to retain the most important points, providing a coherent and readable summary that could help a person understand the main points of the discussion without needing to read the entire text. Please avoid unnecessary details or tangential points."
        custom_reduce_query = "You are tasked with taking multiple summarized texts and merging them into one unified and concise summary. Maintain the core essence of the content and provide a clear and comprehensive summary that encapsulates all the main points from the individual summaries."
        return self.query(text, query, custom_reduce_query)

# Functions to fetch content using Reader API
def get_llm_friendly_content(url):
    reader_url = f"https://r.jina.ai/{url}"
    response = requests.get(reader_url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch content: {response.status_code}")

def search_and_get_top_results(query):
    search_url = f"https://s.jina.ai/{query.replace(' ', '%20')}"
    response = requests.get(search_url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch search results: {response.status_code}")

# Example usage
try:
    url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    content = get_llm_friendly_content(url)
    computer = YourComputerClass()  # Replace with your actual computer class
    ai = Ai(computer)
    summary = ai.summarize(content)
    print(summary)
except Exception as e:
    print(e)