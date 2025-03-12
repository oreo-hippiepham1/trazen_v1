## Source: https://github.com/shashankdeshpande/langchain-chatbot/blob/master/streaming.py

from langchain_core.callbacks import BaseCallbackHandler

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs):
        """
        Everytime LLM generates a new token,
            current text is updated, and the container is refreshed.
        """
        self.text += token
        self.container.markdown(self.text)