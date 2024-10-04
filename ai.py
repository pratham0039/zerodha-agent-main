import sys
import json
from openai import OpenAI
import chromadb
import os
import requests
import time
import re

os.environ["TOKENIZERS_PARALLELISM"] = "false"
api_key = 
client = OpenAI(api_key=api_key)
assistant1 = "asst_fyIp1cXXJVKwdfYyBrvdXNXM"
assistant2 = "asst_NWmIKGZK3eyzyNxsY2uDJaU3"

# Session storage (instead of streamlit)
session_state = {}


def rag(question):
    chroma_client = chromadb.PersistentClient("database/")
    collection = chroma_client.get_or_create_collection(name="zerodhadb")
    results = collection.query(
        query_texts=[question],
        n_results=3
    )
    doc_string = [f"Document {i+1}\n{doc}" for i, doc in enumerate(results['documents'][0])]
    return '\n\n'.join(doc_string)


def check_run(thread_id, run_id):
    endpoint = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}"
    try:
        response = requests.get(endpoint, headers={"Authorization": f"Bearer {api_key}", "OpenAI-Beta": "assistants=v2"}, timeout=5)
        response.raise_for_status()
        response_data = response.json()
        print(response.json())
        print(response_data)
        return response.json()["completed_at"] is not None
    except requests.exceptions.RequestException:
        return False


def run_thread(thread_id, assistant_id):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    done = False
    while not done:
        time.sleep(1)
        done = check_run(thread_id, run.id)

    return client.beta.threads.messages.list(thread_id).data[0].content[0].text.value


def agent1(messages):
    if "agent1_thread" not in session_state:
        # Create a new thread and store it in session_state
        session_state["agent1_thread"] = client.beta.threads.create(messages=messages)
    else:
        # Add the new message to the existing thread
        client.beta.threads.messages.create(
            thread_id=session_state["agent1_thread"].id,
            role="user",
            content=messages[-1]["content"]
        )

    return run_thread(session_state["agent1_thread"].id, assistant1)


def agent2(messages):
    # Use the response from agent1 as the next user message for agent2
    messages.append({"role": "user", "content": agent1(messages)})
    
    if "agent2_thread" not in session_state:
        # Create a new thread for agent2
        session_state["agent2_thread"] = client.beta.threads.create(messages=messages)
    else:
        # Add the new message to the existing thread for agent2
        client.beta.threads.messages.create(
            thread_id=session_state["agent2_thread"].id,
            role="user",
            content=messages[-1]["content"]
        )
    assistant_message = run_thread(session_state["agent2_thread"].id, assistant2)
    cleaned_message = re.sub(r'【\d+:\d+†source】', '', assistant_message).strip()
    return cleaned_message
