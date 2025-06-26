
# import uuid
# import gradio as gr
# import requests
# import time

# API_URL = "http://127.0.0.1:8000/chat/"
# SESSION_ID = str(uuid.uuid4())

# def stream_chat(message, history):
#     payload = {
#         "message": message,
#         "history": history,
#         "session_id": SESSION_ID
#     }

#     try:
#         with requests.post(API_URL, json=payload, stream=True) as response:
#             response.raise_for_status()
#             full_reply = ""
#             for line in response.iter_lines(decode_unicode=True):
#                 if line:
#                     full_reply += line

#             partial = ""
#             for ch in full_reply:
#                 partial += ch
#                 time.sleep(0.01)
#                 yield partial

#     except Exception as e:
#         yield f"❌ Error: {str(e)}"


# demo = gr.ChatInterface(
#     fn=stream_chat,
#     type="messages",
#     flagging_mode="manual",
#     flagging_options=["Like", "Spam", "Inappropriate", "Other"],
#     save_history=True,
#     title="📚 LangGraph Tavily Chatbot",
#     description="Chatbot with Tavily + Gemini + FastAPI backend",
# )

# if __name__ == "__main__":
#     demo.launch()
# import uuid
# import gradio as gr
# import requests
# import time

# API_URL = "http://127.0.0.1:8000/chat/"
# API_HISTORY = "http://127.0.0.1:8000/history/"
# SESSION_ID = str(uuid.uuid4())

# # Load history from MongoDB
# def load_chat_history(session_id):
#     try:
#         res = requests.get(API_HISTORY + session_id)
#         res.raise_for_status()
#         data = res.json()
#         return data.get("history", [])
#     except Exception as e:
#         print(f"❌ Failed to load history: {e}")
#         return []

# # Stream chat response
# def stream_chat(message, history):
#     payload = {
#         "message": message,
#         "history": history,
#         "session_id": SESSION_ID
#     }

#     try:
#         with requests.post(API_URL, json=payload, stream=True) as response:
#             response.raise_for_status()
#             full_reply = ""
#             for line in response.iter_lines(decode_unicode=True):
#                 if line:
#                     full_reply += line

#             partial = ""
#             for ch in full_reply:
#                 partial += ch
#                 time.sleep(0.01)
#                 yield partial
#     except Exception as e:
#         yield f"❌ Error: {str(e)}"

# # === Gradio Launch ===
# def init_interface():
#     history = load_chat_history(SESSION_ID)

#     demo = gr.ChatInterface(
#         fn=stream_chat,
#         chatbot=gr.Chatbot(value=history),
#         type="messages",
#         flagging_mode="manual",
#         flagging_options=["Like", "Spam", "Inappropriate", "Other"],
#         save_history=True,
#         title="📚 LangGraph Tavily Chatbot",
#         description="Chatbot with MongoDB memory",
#     )

#     return demo

# if __name__ == "__main__":
#     init_interface().launch()
import uuid
import gradio as gr
import requests
import time

# === API Endpoints ===
API_CHAT = "http://127.0.0.1:8000/chat/"
API_HISTORY = "http://127.0.0.1:8000/history/"

# === Global session (can persist via file or cookie in future)
SESSION_ID = str(uuid.uuid4())

# === Fetch history from backend
def load_chat_history(session_id):
    try:
        res = requests.get(API_HISTORY + session_id)
        res.raise_for_status()
        data = res.json()
        return data.get("history", [])
    except Exception as e:
        print(f"❌ Failed to load history: {e}")
        return []

# === Send new message and stream back response
def stream_chat(message, history):
    payload = {
        "message": message,
        "history": history,
        "session_id": SESSION_ID
    }

    try:
        with requests.post(API_CHAT, json=payload, stream=True) as response:
            response.raise_for_status()
            full_reply = ""
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    full_reply += line

            # Typing effect
            partial = ""
            for ch in full_reply:
                partial += ch
                time.sleep(0.01)
                yield partial

            # Add to frontend memory
            history.append([message, full_reply])
            yield history  # Gradio v4 expects new history as final yield

    except Exception as e:
        yield f"❌ Error: {str(e)}"

# === Launch UI
def init_interface():
    # Load previous session history
    history = load_chat_history(SESSION_ID)

    demo = gr.ChatInterface(
        fn=stream_chat,
        chatbot=gr.Chatbot(value=history),
        type="messages",
        flagging_mode="manual",
        flagging_options=["Like", "Spam", "Inappropriate", "Other"],
        save_history=True,
        title="📚 LangGraph Tavily Chatbot",
        description="Chatbot with persistent memory using MongoDB + FastAPI",
    )

    return demo

# === Run
if __name__ == "__main__":
    init_interface().launch()
