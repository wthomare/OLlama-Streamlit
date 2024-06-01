# -*- coding: utf-8 -*-
import streamlit as st
from ollama import Client
import yaml


# -----------------------------------------------------------------------------
class MainThread:

    def __init__(self):
        with open('parameters.yml', 'r') as file:
            self.parameters = yaml.safe_load(file)

        # parameters and options : https://github.com/ollama/ollama/blob/main/docs/modelfile.md
        self.client = Client(host=f"{self.parameters['ollama']['url']}:{self.parameters['ollama']['port']}")

        self.MODEL_IMAGES = {
            "llama3": "https://em-content.zobj.net/source/twitter/376/llama_1f999.png",  # Add the emoji for the Meta-Llama model
            "llama3:70b":"https://em-content.zobj.net/source/twitter/376/llama_1f999.png",
            "codellama": "https://em-content.zobj.net/source/twitter/376/llama_1f999.png",
            "mistral": "https://em-content.zobj.net/source/twitter/376/tornado_1f32a-fe0f.png"
        }

        self.selected_formatted_name = st.sidebar.radio(
            "Select LLM Model",
            list(self.MODEL_IMAGES.keys()))

        self.selected_model = self.selected_formatted_name

        if self.MODEL_IMAGES[self.selected_model].startswith("http"):
            st.image(self.MODEL_IMAGES[self.selected_model], width=90)
        else:
            st.write(f"Model Icon: {self.MODEL_IMAGES[self.selected_model]}", unsafe_allow_html=True)

        st.sidebar.markdown('---')

        # Adjust the title based on the selected model
        st.header(f"`{self.selected_formatted_name}` Model")

        with st.expander("About this app"):
            st.write("""
            This Chatbot app allows users to interact with various models including the new LLM models availabme on OLlama.
            For more info, you can refer to [OLlama's documentation](https://github.com/ollama/ollama).
        
            💡 For decent answers, you'd want to increase the `Max Tokens` value from `100` to `500`.
        
            💡 For more or less creative answer, you'd want to change the `temperatire` value from `-1` to `1`. 
            """)

        with st.sidebar:
            max_tokens = st.slider('Max Tokens', 10, 500, 100)
            top_p = st.slider('Top P', 0.0, 1.0, 0.5, 0.05)
            temperature = st.slider("Temperature", -1.0, 1.0, 0.8, 0.1)

            if "messages" not in st.session_state:
                st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
                
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response, error = self.get_response(self.selected_formatted_name, prompt, max_tokens, top_p, temperature)
                    if error:
                        st.error(f"Error: {error}") 
                    else:
                        placeholder = st.empty()
                        placeholder.markdown(response)
                        message = {"role": "assistant", "content": response}
                        st.session_state.messages.append(message)

    # -------------------------------------------------------------------------
    def get_response(self, model, user_input, max_tokens, top_p, temperature):
        try:
            # Existing setup for other models       
            chat_completion = self.client.chat(model = model,
                                          messages = [{"role": "user",
                                                       "content": user_input}],
                                          options={"temperature":temperature,
                                                   "top_p": top_p,
                                                   "num_predict":max_tokens}
                                          )

            return chat_completion['message']['content'], None
        except Exception as e:
            return None, str(e)

    # -------------------------------------------------------------------------
    def clear_chat_history(self):
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]


if __name__ == '__main__':
    main = MainThread()