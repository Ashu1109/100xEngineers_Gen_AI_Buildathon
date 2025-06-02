import streamlit as st
import requests
import os
import json

# Path to conversations directory
conv_dir = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "api", "conversations"
)

# Initialize chat history in session state if not already present
if "messages" not in st.session_state:
    st.session_state.messages = []
if "loaded_conversation_file" not in st.session_state:
    st.session_state.loaded_conversation_file = None


# Function to render chat messages
def render_chat(messages):
    # First pass: Collect all tool calls and results
    tool_calls = []
    tool_results_by_id = {}
    
    # Find all tool calls and results in the conversation
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, list):
            for part in content:
                # Collect tool results by ID
                if isinstance(part, dict) and part.get("type") == "tool_result":
                    tool_id = part.get("tool_use_id", "")
                    if tool_id:
                        tool_results_by_id[tool_id] = part
                
                # Collect all tool calls
                if isinstance(part, dict) and part.get("type") == "tool_use":
                    tool_calls.append({
                        "id": part.get("id", ""),
                        "name": part.get("name", "Unknown Tool"),
                        "input": part.get("input", {}),
                        "message_index": messages.index(msg)
                    })

    # Add a dedicated section to display all tools used in the conversation
    if tool_calls:
        st.markdown("""
        <style>
        .tool-header {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .tool-name {
            color: #1E88E5;
            font-size: 18px;
        }
        .tool-divider {
            border-top: 1px solid #e0e0e0;
            margin: 15px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.header("🧰 Tools Used in This Conversation")
        st.markdown("*Expand each section to see tool details and results*")
        
        for i, tool in enumerate(tool_calls):
            tool_id = tool.get("id")
            tool_name = tool.get("name")
            tool_input = tool.get("input")
            
            with st.expander(f"**{i+1}. {tool_name}**", expanded=False):
                st.markdown(f"<div class='tool-header'><span class='tool-name'>{tool_name}</span></div>", unsafe_allow_html=True)
                st.markdown(f"**Tool ID:** `{tool_id}`")
                st.markdown("**Input Parameters:**")
                st.json(tool_input)
                
                # If we have a result for this tool call, display it
                if tool_id in tool_results_by_id:
                    result = tool_results_by_id[tool_id]
                    st.markdown("<div class='tool-divider'></div>", unsafe_allow_html=True)
                    st.markdown("**📋 Result:**")
                    content_data = result.get('content', [])
                    if content_data:
                        for item in content_data:
                            if isinstance(item, dict) and item.get("type") == "text":
                                st.code(item.get("text", ""), language="json")
    
    # Second pass: Render the conversation with organized tool calls and results
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        
        # Handle user messages
        if role == "user":
            with st.chat_message(role):
                if isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            st.markdown(part.get("text", ""))
                        elif isinstance(part, str):
                            st.markdown(part)
                else:
                    st.markdown(content)
        
        # Handle assistant messages - simplified for clean conversation view
        elif role == "assistant":
            with st.chat_message(role):
                text_parts = []
                
                # Extract only text content for the main conversation view
                if isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            text_parts.append(part.get("text", ""))
                        elif isinstance(part, str):
                            text_parts.append(part)
                else:
                    text_parts.append(content)
                
                # Display all text content
                for text in text_parts:
                    st.markdown(text)
        
        # Handle tool results that weren't matched to a tool call
        elif role == "tool":
            with st.chat_message("system"):
                st.markdown("**Tool Result:**")
                if isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict):
                            st.json(part)
                        else:
                            st.markdown(str(part))
                else:
                    st.markdown(content)


selected_option = "New Chat"  # Initialize with a default value


def load_conversation_from_file(conv_file_name):
    conv_path = os.path.join(conv_dir, conv_file_name)
    try:
        with open(conv_path, "r") as f:
            conv_data = json.load(f)
        st.session_state.messages = conv_data.get("messages", [])
        st.session_state.loaded_conversation_file = conv_file_name
    except Exception as e:
        st.sidebar.error(f"Failed to load conversation: {e}")
        st.session_state.messages = []
        st.session_state.loaded_conversation_file = None


if os.path.exists(conv_dir):
    conv_files = sorted(
        [
            f
            for f in os.listdir(conv_dir)
            if f.startswith("conversation_") and f.endswith(".json")
        ],
        reverse=True,
    )
    options = ["New Chat"] + conv_files

    current_selection_index = 0  # Default to "New Chat"
    if (
        st.session_state.loaded_conversation_file
        and st.session_state.loaded_conversation_file in options
    ):
        current_selection_index = options.index(
            st.session_state.loaded_conversation_file
        )
    elif (
        not st.session_state.loaded_conversation_file and st.session_state.messages
    ):  # In a new chat with messages
        current_selection_index = 0  # Stay on "New Chat"

    selected_option = st.sidebar.selectbox(
        "Select or Start New Chat", options, index=current_selection_index
    )

    if selected_option == "New Chat":
        if (
            st.session_state.loaded_conversation_file is not None
        ):  # If a file was previously loaded
            st.session_state.messages = []
            st.session_state.loaded_conversation_file = None
            st.rerun()
    elif (
        selected_option and selected_option != st.session_state.loaded_conversation_file
    ):
        load_conversation_from_file(selected_option)
        st.rerun()
elif (
    not st.session_state.messages
):  # If conv_dir doesn't exist and no messages in session
    st.sidebar.write("No conversation history found.")
    st.session_state.messages = []
    st.session_state.loaded_conversation_file = None

# Main chat area
st.title("GPT Query Interface")
render_chat(
    st.session_state.messages
)  # Use the existing render_chat with session state

# Chat input at the bottom
if prompt := st.chat_input("Type your message and press Enter..."):
    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)

    # If a historical chat was loaded, interacting means it's now a new/modified chat
    if st.session_state.loaded_conversation_file is not None:
        st.session_state.loaded_conversation_file = None
        # This will cause the selectbox to default to "New Chat" on the next full rerun if not handled by index logic

    # Display the user's message immediately (Streamlit reruns on chat_input, so render_chat above will show it)
    # For an even more immediate feel without waiting for the full rerun logic for the new user message:
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Getting response..."):
        try:
            response = requests.post(
                "http://localhost:8000/query", json={"query": prompt}
            )
            response.raise_for_status()
            data = response.json()

            api_response_messages = data.get("messages", [])
            final_assistant_message_object = None
            for msg_content in reversed(api_response_messages):
                if msg_content.get("role") == "assistant":
                    final_assistant_message_object = msg_content
                    break

            if final_assistant_message_object:
                st.session_state.messages.append(final_assistant_message_object)
                # Force a complete re-render with our enhanced render_chat function
                # This is the most reliable way to ensure consistent display
                st.rerun()

            else:
                st.warning("No assistant message found in the latest API response.")
        except Exception as e:
            st.error(f"Error: {e}")

    # After processing, if loaded_conversation_file became None, ensure UI updates if needed
    # st.chat_input already triggers a rerun. If selectbox needs to reflect "New Chat",
    # the index logic for selectbox should handle it on the rerun.
    if (
        st.session_state.loaded_conversation_file is None
        and selected_option != "New Chat"
    ):
        st.rerun()  # Force rerun to update sidebar if needed
