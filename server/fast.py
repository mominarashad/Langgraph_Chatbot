# # server/fast.py
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import StreamingResponse
# from pydantic import BaseModel
# from typing import List, Union, Any

# from langchain_core.messages import HumanMessage, AIMessage
# from Chatbot.chatbot import graph  # adjust if path is different

# app = FastAPI()

# # Allow frontend to access API
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class ChatInput(BaseModel):
#     message: str
#     history: Union[List[List[str]], Any]  # Accepts list of lists or fallback to raw

# @app.post("/chat/")
# async def stream_chat(chat_input: ChatInput):
#     messages = []

#     # Debugging: Print incoming history format
#     print("📩 Raw history received:", chat_input.history)

#     # Handle both structured [["user", "bot"]] and raw message dicts if needed
#     try:
#         for pair in chat_input.history:
#             if isinstance(pair, list) and len(pair) == 2:
#                 user, bot = pair
#                 messages.append(HumanMessage(content=user))
#                 messages.append(AIMessage(content=bot))
#     except Exception as e:
#         print(f"⚠️ Failed to parse history: {e}")
    
#     # Add latest user message
#     messages.append(HumanMessage(content=chat_input.message))

#     def event_stream():
#         try:
#             response = graph.invoke({"messages": messages})
#             answer = response["messages"][-1].content

#             for char in answer:
#                 yield char

#             # Optional: If tool outputs include sources
#             # if hasattr(response["messages"][-1], "tool_calls"):
#             #     yield "\n\nSources:\n"
#             #     for tool_call in response["messages"][-1].tool_calls:
#             #          ...
#         except Exception as e:
#             yield f"\n❌ Error: {str(e)}"

#     return StreamingResponse(event_stream(), media_type="text/plain")

# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import StreamingResponse, JSONResponse
# from pydantic import BaseModel
# from typing import List, Union, Any
# from langchain_core.messages import HumanMessage, AIMessage
# from Chatbot.chatbot import graph
# from mongo.memory import save_chat, get_chat_history
# import uuid

# app = FastAPI()

# # CORS settings
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # === Pydantic Input Schema ===
# class ChatInput(BaseModel):
#     message: str
#     history: Union[List[List[str]], Any] = []
#     session_id: str = None

# # === Main Chat Endpoint ===
# @app.post("/chat/")
# async def stream_chat(chat_input: ChatInput):
#     session_id = chat_input.session_id or str(uuid.uuid4())
#     print(f"📩 Session ID: {session_id}")
    
#     # Load memory from MongoDB
#     past = get_chat_history(session_id)
#     messages = []

#     for pair in past:
#         if isinstance(pair, list) and len(pair) == 2:
#             messages.append(HumanMessage(content=pair[0]))
#             messages.append(AIMessage(content=pair[1]))

#     # Add current user message
#     messages.append(HumanMessage(content=chat_input.message))

#     def event_stream():
#         try:
#             response = graph.invoke({"messages": messages})
#             answer = response["messages"][-1].content

#             # Save both messages
#             save_chat(session_id, "user", chat_input.message)
#             save_chat(session_id, "assistant", answer)

#             for char in answer:
#                 yield char

#         except Exception as e:
#             yield f"\n❌ Error: {str(e)}"

#     return StreamingResponse(event_stream(), media_type="text/plain")

# # === Load Previous History ===
# @app.get("/history/{session_id}")
# def load_history(session_id: str):
#     try:
#         history = get_chat_history(session_id)
#         return JSONResponse(content={"history": history})
#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Union, Any
from langchain_core.messages import HumanMessage, AIMessage
from Chatbot.chatbot import graph
from mongo.memory import get_chat_history
from Manager.langfuser import run_langfuse_chat, log_prompt_trace  # ✅ Langfuse log functions
import uuid

app = FastAPI()

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Pydantic Input ===
class ChatInput(BaseModel):
    message: str
    history: Union[List[List[str]], Any] = []
    session_id: str = None

# === Chat Endpoint ===
@app.post("/chat/")
async def stream_chat(chat_input: ChatInput):
    session_id = chat_input.session_id or str(uuid.uuid4())
    print(f"📩 Session ID: {session_id}")

    past = get_chat_history(session_id)
    messages = []

    for pair in past:
        if isinstance(pair, list) and len(pair) == 2:
            messages.append(HumanMessage(content=pair[0]))
            messages.append(AIMessage(content=pair[1]))

    messages.append(HumanMessage(content=chat_input.message))

    def event_stream():
        try:
            # ✅ Corrected: include session_id in graph state
            response = graph.invoke({
                "messages": messages,
                "session_id": session_id
            })

            answer = response["messages"][-1].content

            # ✅ Log to Langfuse
            run_langfuse_chat(session_id=session_id, user_msg=chat_input.message, output=answer)

            # ✅ Stream the response
            for char in answer:
                yield char

        except Exception as e:
            run_langfuse_chat(session_id=session_id, user_msg=chat_input.message, output=str(e), status="error")
            yield f"\n❌ Error: {str(e)}"

    return StreamingResponse(event_stream(), media_type="text/plain")

# === Get Chat History ===
@app.get("/history/{session_id}")
def load_history(session_id: str):
    try:
        history = get_chat_history(session_id)
        return JSONResponse(content={"history": history})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
