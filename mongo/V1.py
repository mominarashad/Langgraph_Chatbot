# from pymongo import MongoClient
# from datetime import datetime
# from settings import MONGO_URI  # Assuming you have a settings.py with MONGO_URI defined

# client = MongoClient(MONGO_URI)
# db = client["chatbot_db"]
# chats = db["chats"]

# def save_chat(session_id: str, role: str, content: str):
#     chats.insert_one({
#         "session_id": session_id,
#         "role": role,
#         "content": content,
#         "timestamp": datetime.utcnow()
#     })

# def get_chat_history(session_id: str):
#     records = list(chats.find({"session_id": session_id}).sort("timestamp", 1))
#     history = []
#     i = 0
#     while i < len(records) - 1:
#         if records[i]["role"] == "user" and records[i + 1]["role"] == "assistant":
#             history.append([records[i]["content"], records[i + 1]["content"]])
#             i += 2
#         else:
#             i += 1
#     return history
from pymongo import MongoClient
from datetime import datetime
from settings import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["chatbot_db"]
collection = db['chat_history']

def save_chat(session_id: str, role: str, content: str):
    """
    Save a chat message to MongoDB.

    Args:
        session_id (str): Unique session ID.
        role (str): 'user' or 'ai'.
        content (str): The message content.
    """
    collection.insert_one({
        "session_id": session_id,
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow()
    })


def get_chat_history(session_id: str):
    """
    Retrieve chat history from MongoDB and return it in user/ai pairs.

    Returns:
        List[List[str]]: [['user1', 'ai1'], ['user2', 'ai2'], ...]
    """
    messages = list(collection.find({"session_id": session_id}).sort("timestamp", 1))
    
    history_pairs = []
    temp_pair = []

    for msg in messages:
        if msg["role"] == "user":
            if temp_pair:
                history_pairs.append(temp_pair)
                temp_pair = []
            temp_pair.append(msg["content"])
        elif msg["role"] == "ai":
            if not temp_pair:
                temp_pair.append("")  # Edge case: AI before user
            temp_pair.append(msg["content"])
            history_pairs.append(temp_pair)
            temp_pair = []

    # Append any leftover user message without AI response
    if temp_pair:
        history_pairs.append(temp_pair)

    return history_pairs


def delete_history(session_id: str):
    """
    Delete all messages in a session.
    """
    result = collection.delete_many({"session_id": session_id})
    return result.deleted_count
