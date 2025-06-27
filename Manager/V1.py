
# from langfuse import observe
# from mongo.memory import save_chat
# from settings import langfuse_client


# # === Log conversation + store in Mongo ===
# @observe()
# def run_langfuse_chat(session_id: str, user_msg: str, output: str, tool_used: str = None, status: str = "success"):
#     save_chat(session_id, "user", user_msg)
#     save_chat(session_id, "ai", output)

   
#     return {
#         "session_id": session_id,
#         "input": user_msg,
#         "output": output,
#         "tool": tool_used,
#         "status": status
#     }

# # === Log prompt usage (optional tracing) ===
# @observe()
# def log_prompt_trace(prompt_name: str, user_input: str, prompt_text: str):
#     return {
#         "prompt_name": prompt_name,
#         "input": user_input,
#         "prompt_used": prompt_text
#     }
# from langfuse import observe
# from mongo.memory import save_chat


# @observe()
# def run_langfuse_chat(
#     session_id: str,
#     user_msg: str,
#     output: str,
#     tool_used: str = None,
#     status: str = "success",
#     trace=None  # ✅ Langfuse injects this
# ):
#     # ✅ Save to MongoDB
#     save_chat(session_id, "user", user_msg)
#     save_chat(session_id, "ai", output)

#     # ✅ Log LLM observation to Langfuse
#     if trace:
#         trace.add_observation(
#             name="LLM Response Observation",
#             input={"session_id": session_id, "user_message": user_msg},
#             output=output,
#             metadata={
#                 "tool": tool_used,
#                 "status": status
#             }
#         )

#     return {
#         "session_id": session_id,
#         "input": user_msg,
#         "output": output,
#         "tool": tool_used,
#         "status": status
#     }


# @observe()
# def log_prompt_trace(
#     prompt_name: str,
#     user_input: str,
#     prompt_text: str,
#     trace=None  # ✅ Langfuse injects this
# ):
#     # ✅ Log prompt details
#     if trace:
#         trace.add_observation(
#             name="Prompt Usage Trace",
#             input={"prompt_name": prompt_name, "user_input": user_input},
#             output=prompt_text,
#             metadata={"type": "prompt"}
#         )

#     return {
#         "prompt_name": prompt_name,
#         "input": user_input,
#         "prompt_used": prompt_text
#     }
from langfuse import observe, Langfuse
from mongo.memory import save_chat
from settings import langfuse_client

@observe()
def run_langfuse_chat(
    session_id: str,
    user_msg: str,
    output: str,
    tool_used: str = None,
    status: str = "success",
    trace=None  # ✅ Langfuse injects this
):
    # ✅ Save to MongoDB
    save_chat(session_id, "user", user_msg)
    save_chat(session_id, "ai", output)

    # ✅ Log LLM observation to Langfuse
    if trace:
        trace.add_observation(
            name="LLM Response Observation",
            input={"session_id": session_id, "user_message": user_msg},
            output=output,
            metadata={
                "tool": tool_used,
                "status": status
            }
        )

    return {
        "session_id": session_id,
        "input": user_msg,
        "output": output,
        "tool": tool_used,
        "status": status
    }


@observe()
def log_prompt_trace(
    prompt_name: str,
    user_input: str,
    prompt_text: str,
    trace=None  # ✅ Langfuse injects this
):
    # ✅ Register the prompt so it shows up in Prompts tab
    langfuse_client.prompt(
        name=prompt_name,
        type="text",
        prompt=prompt_text,
        metadata={"source": "logged-from-agent"}
    )

    # ✅ Log prompt usage in trace
    if trace:
        trace.add_observation(
            name="Prompt Usage Trace",
            input={"prompt_name": prompt_name, "user_input": user_input},
            output=prompt_text,
            metadata={"type": "prompt"}
        )

    return {
        "prompt_name": prompt_name,
        "input": user_input,
        "prompt_used": prompt_text
    }
