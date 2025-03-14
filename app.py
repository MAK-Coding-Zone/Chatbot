from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import json
import os

app = Flask(__name__)

# Replace with your OpenRouter API key
# OPENROUTER_API_KEY = "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"
OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Folder to store chat history
CHAT_HISTORY_FOLDER = "chat_history"

# Ensure the chat history folder exists
if not os.path.exists(CHAT_HISTORY_FOLDER):
    os.makedirs(CHAT_HISTORY_FOLDER)

# Function to load chat history for a specific session
def load_chat_history(session_id):
    file_path = os.path.join(CHAT_HISTORY_FOLDER, f"{session_id}.json")
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Function to save chat history for a specific session
def save_chat_history(session_id, history):
    file_path = os.path.join(CHAT_HISTORY_FOLDER, f"{session_id}.json")
    with open(file_path, 'w') as file:
        json.dump(history, file, indent=4)

# Function to list all chat sessions with summaries
def list_chat_sessions():
    sessions = []
    for file_name in os.listdir(CHAT_HISTORY_FOLDER):
        if file_name.endswith(".json"):
            session_id = file_name[:-5]  # Remove .json extension
            chat_history = load_chat_history(session_id)
            summary = chat_history[0]['content'] if chat_history else "New Chat"
            sessions.append({"id": session_id, "summary": summary})
    return sessions

# Function to clear all chat history
def clear_all_chat_history():
    for file_name in os.listdir(CHAT_HISTORY_FOLDER):
        file_path = os.path.join(CHAT_HISTORY_FOLDER, file_name)
        os.remove(file_path)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    session_id = request.json.get('session_id')
    user_message = request.json.get('message')

    # Load existing chat history for the session
    chat_history = load_chat_history(session_id)

    # Add user message to history
    chat_history.append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # Prepare the payload for OpenRouter API
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "google/gemini-2.0-flash-lite-preview-02-05:free",  # You can change the model as needed
        "messages": chat_history[-10:]  # Send last 10 messages for context
    }

    # Send request to OpenRouter API
    response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        bot_reply = response.json()['choices'][0]['message']['content']

# Convert basic Markdown to HTML
        bot_reply = bot_reply.replace("**", "<b>").replace("*", "• ")

# Ensure proper closing tags for bold text
        bot_reply = bot_reply.replace("<b>", "<b>", 1).replace("<b>", "</b>", 1)

    else:
        bot_reply = "Sorry, I couldn't process your request."

    # Add bot reply to history
    chat_history.append({
        "role": "assistant",
        "content": bot_reply,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # Save updated chat history
    save_chat_history(session_id, chat_history)

    return jsonify({"reply": bot_reply})

@app.route('/chat-history')
def get_chat_history():
    session_id = request.args.get('session_id')
    if session_id:
        return jsonify(load_chat_history(session_id))
    else:
        return jsonify([])

@app.route('/chat-sessions')
def get_chat_sessions():
    return jsonify(list_chat_sessions())

@app.route('/clear-all-chats', methods=['POST'])
def clear_all_chats():
    clear_all_chat_history()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)




# from flask import Flask, render_template, request, jsonify, Markup
# import requests
# from datetime import datetime
# import json
# import os
# # import markdown  # For rendering markdown

# from markupsafe import Markup  # ✅ Correct import


# app = Flask(__name__)

# # Load API key from environment variable for security
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
# OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# # Folder to store chat history
# CHAT_HISTORY_FOLDER = "chat_history"

# # Ensure the chat history folder exists
# if not os.path.exists(CHAT_HISTORY_FOLDER):
#     os.makedirs(CHAT_HISTORY_FOLDER)

# # Function to load chat history for a specific session
# def load_chat_history(session_id):
#     file_path = os.path.join(CHAT_HISTORY_FOLDER, f"{session_id}.json")
#     try:
#         with open(file_path, 'r') as file:
#             return json.load(file)
#     except FileNotFoundError:
#         return []

# # Function to save chat history for a specific session
# def save_chat_history(session_id, history):
#     file_path = os.path.join(CHAT_HISTORY_FOLDER, f"{session_id}.json")
#     with open(file_path, 'w') as file:
#         json.dump(history, file, indent=4)

# # Function to list all chat sessions with summaries
# def list_chat_sessions():
#     sessions = []
#     for file_name in os.listdir(CHAT_HISTORY_FOLDER):
#         if file_name.endswith(".json"):
#             session_id = file_name[:-5]  # Remove .json extension
#             chat_history = load_chat_history(session_id)
#             summary = chat_history[0]['content'] if chat_history else "New Chat"
#             sessions.append({"id": session_id, "summary": summary})
#     return sessions

# # Function to clear all chat history
# def clear_all_chat_history():
#     for file_name in os.listdir(CHAT_HISTORY_FOLDER):
#         file_path = os.path.join(CHAT_HISTORY_FOLDER, file_name)
#         os.remove(file_path)

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/chat', methods=['POST'])
# def chat():
#     session_id = request.json.get('session_id')
#     user_message = request.json.get('message')

#     # Load existing chat history for the session
#     chat_history = load_chat_history(session_id)

#     # Add user message to history
#     chat_history.append({
#         "role": "user",
#         "content": user_message,
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     })

#     # Prepare the payload for OpenRouter API
#     headers = {
#         "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "model": "google/gemini-2.0-flash-lite-preview-02-05:free",  # You can change the model as needed
#         "messages": chat_history[-10:]  # Send last 10 messages for context
#     }

#     # Send request to OpenRouter API
#     response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
    
#     if response.status_code == 200:
#         bot_reply = response.json()['choices'][0]['message']['content']

# # Convert basic Markdown to HTML
#         bot_reply = bot_reply.replace("**", "<b>").replace("*", "• ")

# # Ensure proper closing tags for bold text
#         bot_reply = bot_reply.replace("<b>", "<b>", 1).replace("<b>", "</b>", 1)

#     else:
#         print("Error:", response.text)  # Log API errors
#         bot_reply = f"Error: {response.status_code}. {response.text}"

#     # Convert Markdown to HTML
#     bot_reply = markdown.markdown(bot_reply)

#     # Add bot reply to history
#     chat_history.append({
#         "role": "assistant",
#         "content": bot_reply,
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     })

#     # Save updated chat history
#     save_chat_history(session_id, chat_history)

#     return jsonify({"reply": Markup(bot_reply)})  # Send safe HTML response

# @app.route('/chat-history')
# def get_chat_history():
#     session_id = request.args.get('session_id')
#     if session_id:
#         return jsonify(load_chat_history(session_id))
#     else:
#         return jsonify([])

# @app.route('/chat-sessions')
# def get_chat_sessions():
#     return jsonify(list_chat_sessions())

# @app.route('/clear-all-chats', methods=['POST'])
# def clear_all_chats():
#     clear_all_chat_history()
#     return jsonify({"status": "success"})

# if __name__ == '__main__':
#     app.run(debug=True)
