# from langfuse import Langfuse, observe
# import os
# from dotenv import load_dotenv
# from mongo.memory import save_chat

# # === Load API keys from .env ===
# load_dotenv()

# langfuse = Langfuse(
#     public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
#     secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
#     host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
# )

# # === Trace chat interactions ===
# @observe()
# def run_langfuse_chat(session_id: str, user_msg: str, output: str, tool_used: str = None, status: str = "success"):
#     """
#     Logs the chat interaction to Langfuse and also stores it to MongoDB.
#     """
#     # Store to MongoDB
#     save_chat(session_id, "user", user_msg)
#     save_chat(session_id, "ai", output)

#     # Langfuse trace summary
#     return {
#         "session_id": session_id,
#         "input": user_msg,
#         "output": output,
#         "tool": tool_used,
#         "status": status
#     }

# # === Optional: Wrap prompt templates if using LangChain prompts ===
# @observe()
# def trace_prompt(prompt_name: str, user_input: str, prompt_text: str):
#     """
#     For logging structured prompt calls if you're formatting prompts separately.
#     """
#     return {
#         "prompt_name": prompt_name,
#         "input": user_input,
#         "prompt_used": prompt_text
#     }
from langfuse import Langfuse, observe
import os
from dotenv import load_dotenv
from mongo.memory import save_chat

# === Load Langfuse API keys ===
load_dotenv()

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)

# === Log conversation + store in Mongo ===
@observe()
def run_langfuse_chat(session_id: str, user_msg: str, output: str, tool_used: str = None, status: str = "success"):
    save_chat(session_id, "user", user_msg)
    save_chat(session_id, "ai", output)

    return {
        "session_id": session_id,
        "input": user_msg,
        "output": output,
        "tool": tool_used,
        "status": status
    }

# === Log prompt usage (if formatting prompt separately) ===
@observe()
def log_prompt_trace(prompt_name: str, user_input: str, prompt_text: str):
    return {
        "prompt_name": prompt_name,
        "input": user_input,
        "prompt_used": prompt_text
    }
