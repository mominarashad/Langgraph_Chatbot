from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["chatbot_db"]
chats = db["chats"]

def save_chat(session_id: str, role: str, content: str):
    chats.insert_one({
        "session_id": session_id,
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow()
    })

def get_chat_history(session_id: str):
    records = list(chats.find({"session_id": session_id}).sort("timestamp", 1))
    history = []
    i = 0
    while i < len(records) - 1:
        if records[i]["role"] == "user" and records[i + 1]["role"] == "assistant":
            history.append([records[i]["content"], records[i + 1]["content"]])
            i += 2
        else:
            i += 1
    return history
