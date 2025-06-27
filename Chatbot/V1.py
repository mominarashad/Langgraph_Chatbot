# from typing import Annotated
# from langchain_tavily import TavilySearch
# from langchain_core.messages import BaseMessage
# from typing_extensions import TypedDict
# from langgraph.graph import StateGraph, START, END
# from langgraph.graph.message import add_messages
# from langgraph.prebuilt import ToolNode, tools_condition
# from langchain.chat_models import init_chat_model
# from dotenv import load_dotenv
# class State(TypedDict):
#     messages: Annotated[list, add_messages]

# load_dotenv()
# graph_builder = StateGraph(State)

# llm=init_chat_model('google_genai:gemini-2.0-flash')

# tool = TavilySearch(max_results=2)
# tools = [tool]
# llm_with_tools = llm.bind_tools(tools)

# def chatbot(state: State):
#     return {"messages": [llm_with_tools.invoke(state["messages"])]}

# graph_builder.add_node("chatbot", chatbot)

# tool_node = ToolNode(tools=[tool])
# graph_builder.add_node("tools", tool_node)

# graph_builder.add_conditional_edges(
#     "chatbot",
#     tools_condition,
# )
# # Any time a tool is called, we return to the chatbot to decide the next step
# graph_builder.add_edge("tools", "chatbot")
# graph_builder.add_edge(START, "chatbot")
# graph = graph_builder.compile()


from typing import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_tavily import TavilySearch
from typing_extensions import TypedDict
from dotenv import load_dotenv
from Manager.langfuser import run_langfuse_chat  
from mongo.memory import get_chat_history, save_chat  
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder 
from langchain_core.prompts.chat import ChatPromptValue
import os
from settings import LLM_PROVIDER


# === Define LangGraph State ===
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    session_id: str

# === Init Chat Model & Tools ===
llm = init_chat_model(LLM_PROVIDER)
tool = TavilySearch(max_results=2)
tools = [tool]
llm_with_tools = llm.bind_tools(tools)

# === Create Prompt Template (with agent_scratchpad) ===
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="chat_history"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
    ("human", "{input}")
])

# === Create Agent and AgentExecutor ===
agent = create_tool_calling_agent(llm_with_tools, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    input_keys=["input", "chat_history"]  # ✅ Accepts structured dict input
)

# === Custom Chatbot Function ===
def chatbotfunc(state: State) -> State:
    user_msg = state["messages"][-1].content
    session_id = state["session_id"]

    print(f"\n📩 Session ID: {session_id}")
    print(f"📨 User message: {user_msg}")

    save_chat(session_id, "user", user_msg)

    try:
        # 1. Load previous history (user-assistant pairs)
        history_pairs = get_chat_history(session_id)  # [['hi', 'hello'], ...]
        print(f"🧠 Loaded history: {history_pairs}")

        # ✅ Convert list of [user, ai] to LangChain message objects
        chat_history = []
        for pair in history_pairs:
            if len(pair) == 2:
                chat_history.append(HumanMessage(content=pair[0]))
                chat_history.append(AIMessage(content=pair[1]))

        # 2. Send to AgentExecutor
        result = agent_executor.invoke({
            "input": user_msg,
            "chat_history": chat_history
        })

        if not isinstance(result, dict) or "output" not in result:
            raise ValueError("AgentExecutor did not return expected dict with 'output' key")

        output_text = result["output"]
        save_chat(session_id, "ai", output_text)

        run_langfuse_chat(
            session_id=session_id,
            user_msg=user_msg,
            output=output_text,
            tool_used="TavilySearch",
            status="success"
        )

        # Return full updated message state
        return {
            "messages": state["messages"] + [AIMessage(content=output_text)],
            "session_id": session_id
        }

    except Exception as e:
        err_msg = f"❌ Error: {str(e)}"
        print(err_msg)
        save_chat(session_id, "ai", err_msg)
        run_langfuse_chat(session_id, user_msg, err_msg, tool_used="TavilySearch", status="failure")

        return {
            "messages": state["messages"] + [AIMessage(content=err_msg)],
            "session_id": session_id
        }


# === Build LangGraph ===
graph_builder = StateGraph(State)

# Add chatbot logic node
graph_builder.add_node("chatbot", chatbotfunc)

# Add tool node
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

# Add routing and edges
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")

# === Compile Graph ===
graph = graph_builder.compile()
