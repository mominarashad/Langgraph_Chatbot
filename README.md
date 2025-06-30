# 🤖 LangGraph Chatbot with FastAPI, Gradio, MongoDB, Tavily & Langfuse

A powerful AI chatbot built using:

- **LangGraph** for stateful conversational logic
- **Langchain + TavilySearch** for tool-augmented answers
- **MongoDB** for persistent memory
- **FastAPI** as backend API
- **Gradio** for frontend UI
- **Langfuse** for observability and tracing

---

## 🚀 Features

✅ Streaming AI responses  
✅ Tool usage with Tavily Web Search  
✅ Persistent memory stored in MongoDB  
✅ Session-based chat history  
✅ Langfuse observability  
✅ Gradio UI + FastAPI backend

---

## 🏗️ Project Structure

Langgraph_Chatbot/
├── frontend.py # Gradio-based UI
├── main.py # FastAPI backend
├── Chatbot/
│ └── chatbot.py # LangGraph chat logic
├── mongo/
│ └── memory.py # MongoDB chat memory functions
├── Manager/
│ └── langfuser.py # Langfuse logging/tracing
├── .env # Environment variables (not committed)
├── .gitignore # Git exclusions
└── requirements.txt # Python dependencies

## 🛠️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/mominarashad/Langgraph_Chatbot.git
cd Langgraph_Chatbot
```


2.Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

3.Install dependencies
```bash
pip install -r requirements.txt
```

4.Create .env file
MONGO_URI=mongodb://localhost:27017/
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com


Running the App
1. Start the FastAPI backend

```bash
python main.py
```
Runs at: http://127.0.0.1:8000

2.Start the Gradio frontend
```bash
python frontend.py
```
Opens at: http://127.0.0.1:7860

API Endpoints
POST /chat/: Send a message and receive a streamed response

GET /history/{session_id}: Fetch saved chat history




