# Import the required libraries
from flask import Flask, request, jsonify
from phi.assistant import Assistant
from phi.tools.duckduckgo import DuckDuckGo
from phi.llm.openai import OpenAIChat
from dotenv import load_dotenv
import os
import openai
from openai import OpenAI
import ai

# Load environment variables
load_dotenv()

# Replace with your OpenAI API key
openai.api_key = "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"

os.environ["OPENAI_API_KEY"] = "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"
os.environ["SERPER_API_KEY"] = "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"

# Replace with your assistant ID
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create a Flask app
app = Flask(__name__)

# Hardcoded OpenAI API key
OPENAI_ACCESS_TOKEN = "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"  # Replace with your actual OpenAI API key

# Create an instance of the Assistant
assistant = Assistant(
    llm=OpenAIChat(
        model="gpt-4o-mini",
        max_tokens=1024,
        temperature=0.9,
        api_key=OPENAI_ACCESS_TOKEN
    ),
    tools=[DuckDuckGo()],
    show_tool_calls=False
)


# OpenAI assistant prompt generation function
def get_best_response(user_message, response):
    prompt = f'''
You are a customer service specialist at a company named LXME.
LXME is India's first investment and financial platform specifically designed for women. The platform aims to empower women to achieve financial freedom and confidence in managing their finances. It offers various resources including:

1. **Investment Opportunities**: The LXME app provides options for mutual fund investments, allowing women to invest systematically in line with their financial goals.
2. **Educational Resources**: The site features blogs, guides, and live sessions to enhance financial literacy among women.
3. **Financial Tools**: LXME includes user-friendly financial calculators to assist in personal financial planning.
4. **Community Support**: The platform fosters a community where women can learn, discuss, and share experiences related to finance.

This is more information: {response}
Answer the user query: {user_message}

If the data doesn't have an answer to the user query, tell them you can't find anything related to the query.
Do not remove any reference or link in the information.
If LXME don't have any service or platform user aksed, or the question is not relevant to LXME just let the user know.
'''
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    response = response.choices[0].message.content.strip()
    
    return response


def handle_conversation(agent, messages):
    for message in messages:
        if message["role"] == "system":
            continue
    prompt = messages[-1]["content"] if messages else ""
    if prompt:
        response = agent(messages)  # Call the AI agent with the conversation history
        messages.append({"role": "assistant", "content": response})
        return response
    return None

@app.route('/search', methods=['POST'])
def search():
    # Get the search query from the request
    data = request.get_json()
    messages = data.get("messages", [])

    if messages:
        # Search the web using the AI Assistant
        response = handle_conversation(ai.agent1, messages)

        # Return the response as JSON
        return jsonify({'response': response})
    else:
        return jsonify({'error': 'No query provided'}), 400

if __name__ == '__main__':
    app.run(debug=True)
