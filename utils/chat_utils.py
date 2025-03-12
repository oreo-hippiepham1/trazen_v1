import streamlit as st

def display_single_message(message, role):
    """
    Display a single message in the chat UI.
    mainly for user messages
    """
    st.session_state['messages'].append(
        {
            'role': role,
            'content': message
        }
    )
    with st.chat_message(role):
        st.write(message)

#decorator for any chat UI
def enable_chat_history(func):
    """
    Decorator to enable chat history for a function.
    """
    # clear chat history after swtching pages
    current_page = func.__qualname__
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = current_page
        st.write(st.session_state["current_page"])
    if st.session_state["current_page"] != current_page:
        try:
            st.cache_resource.clear()
            del st.session_state["current_page"]
            del st.session_state["messages"]
        except:
            pass

    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
        st.session_state['messages'].append(
            {
                'role': 'assistant',
                'content': "Hello! How can I help you?"
            }
        )
        # writes all history messages to chat
        # this is a workaround for the chat UI
        # because Streamlit reruns top to bottom
    for message in st.session_state['messages']:
        with st.chat_message(message['role']):
            st.write(message['content'])

    def wrapper(*args, **kwargs):
        # Call the original function
        result = func(*args, **kwargs)
        return result
    return wrapper