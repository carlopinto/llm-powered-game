'''
Prerequisites:
    DEPRECATED: Run start_windows.bat in text-generation-webui
    Load a model
    or look at one_click.py (launch_webui) and run command with flags
    
    * Launch LM Studio and start the server
    * No prerequisites for OpenAI - (as long as the API key is in the 
      .env file and there's credit in the account)
'''

import json
import requests
# import sseclient  # pip install sseclient-py
import openai
from openai import OpenAI

# LM Studio
HOST = "http://127.0.0.1:1234"
URL = HOST + "/v1/chat/completions"

headers = {
    "Content-Type": "application/json"
}


def check_llm_server_status(): # pragma: no cover
    """ Check status of LLM server"""   
    try:
        response = requests.get(HOST + "/v1/models", timeout=10)

        if response.status_code != 200:
            return 0
        return 1
    except requests.exceptions.RequestException:
        return 0


def single_query_llm(instruction, message, system_message=""): # pragma: no cover
    """ Send a single query to LLM """
    prompt = instruction + " " + message
    msgs = [{"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
    ]
    return query_llm(msgs)


def query_llm(messages): # pragma: no cover
    """ Send query to LLM \n
    Format for messages is:\n
    [{"role": "system", "content": system_message},
    {"role": "user", "content": prompt}]
    """
    try:
        data = {
            "mode": "chat",
            "messages": messages
        }
        response = requests.post(URL, headers=headers, json=data, verify=False)
        response_json = json.loads(response.text)
        return response_json['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print("An exception occurred: ", e)
        return None


def single_query_openai(instruction, message, system_message=""): # pragma: no cover
    """ Send a single query to OpenAI """
    prompt = instruction + " " + message
    msgs = [{"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
    ]
    return query_openai(msgs)


def query_openai(messages): # pragma: no cover
    """ Send query to OpenAI \n
    Format for messages is:\n
    [{"role": "system", "content": system_message},
    {"role": "user", "content": prompt}]
    """
    client = OpenAI()
    try:
        completion = client.chat.completions.create(
            # model="gpt-3.5-turbo",
            model="gpt-4",
            messages=messages
        )
        return completion.choices[0].message.content
    except openai.APIConnectionError:
        print("The server could not be reached")
    except openai.RateLimitError:
        print("A 429 status code was received; we should back off a bit.")
    except openai.APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e.status_code)
        print(e.response)
    return None


def get_query_response(event, offline, system_message, instruction) -> str: # pragma: no cover
    """ Helper function to call the correct function based on offline flag """
    if offline:
        return single_query_llm(instruction, event, system_message)

    return single_query_openai(instruction, event, system_message)


def chat(system, user_assistant, offline=True): # pragma: no cover
    """ Send query to LLM (OpenSource or OpenAI) - support for chat history """
    assert isinstance(system, str), "`system` should be a string"
    assert isinstance(user_assistant, list), "`user_assistant` should be a list"

    system_msg = [{"role": "system", "content": system}]
    user_assistant_msgs = [
        {"role": "assistant", "content": user_assistant[i]} if i % 2
        else {"role": "user", "content": user_assistant[i]}
        for i in range(len(user_assistant))]

    msgs = system_msg + user_assistant_msgs
    return query_llm(msgs) if offline else query_openai(msgs)
