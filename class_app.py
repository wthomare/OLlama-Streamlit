# -*- coding: utf-8 -*-
import streamlit as st
from ollama import Client
import yaml
import logging


# -----------------------------------------------------------------------------
class MainThread:

    # -------------------------------------------------------------------------
    def __init__(self):
        # Load parameters from yaml file (not provided on github obviously)
        with open('parameters.yml', 'r') as file:
            self.parameters = yaml.safe_load(file)
            
        logging.basicConfig()
        if self.parameters["APP"]["DEBUG"] == "True":
            self.logger = logging.getLogger().setLevel(logging.DEBUG)
        else:
            self.logger = logging.getLogger()

        # parameters and options : https://github.com/ollama/ollama/blob/main/docs/modelfile.md
        self.client = Client(host=f"{self.parameters['ollama']['url']}:{self.parameters['ollama']['port']}")
        

        self.MODEL_IMAGES = {
            "llama3": "https://em-content.zobj.net/source/twitter/376/llama_1f999.png",  # Add the emoji for the Meta-Llama model
            "llama3:70b":"https://em-content.zobj.net/source/twitter/376/llama_1f999.png",
            "codellama": "https://em-content.zobj.net/source/twitter/376/llama_1f999.png",
            "mistral": "https://em-content.zobj.net/source/twitter/376/tornado_1f32a-fe0f.png"
        }

        self.selected_name = st.sidebar.radio(
            "Select LLM Model",
            list(self.MODEL_IMAGES.keys()))
        
        self.check_local_model(self.selected_name)

        if self.MODEL_IMAGES[self.selected_name].startswith("http"):
            st.image(self.MODEL_IMAGES[self.selected_name], width=90)
        else:
            st.write(f"Model Icon: {self.MODEL_IMAGES[self.selected_name]}", unsafe_allow_html=True)

        st.sidebar.markdown('---')

        # Adjust the title based on the selected model
        st.header(f"`{self.selected_name}` Model")

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
                st.session_state.messages = [{"role": "assistant",
                                              "content": "How may I assist you today?"}]
                
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user",
                                              "content": prompt})
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response, error = self.get_response(self.selected_name,
                                                        prompt,
                                                        max_tokens,
                                                        top_p,
                                                        temperature)
                    if error:
                        st.error(f"Error: {error}") 
                    else:
                        placeholder = st.empty()
                        placeholder.markdown(response)
                        message = {"role": "assistant", "content": response}
                        st.session_state.messages.append(message)

    # -------------------------------------------------------------------------
    def check_local_model(self, request_model:str):
        """
        Check if the requested model is already loaded locally by OLlama
        Otherwise, the app try to pull it.

        Parameters
        ----------
        request_model : str
            Name of the model to check on Ollama.

        Returns
        -------
        None.

        """
        models = self.client.list()["models"]
        models_names = [model["name"].split(":")[0] for model in models]
        self.logger.error(models_names)
        if request_model not in models_names:
            res = self.client.pull(request_model, stream=False)
            
            if res["status"] != "success":
                self.logger.error(f"Failed to pull the requested model {request_model}")
            else:
                self.logger.exception(f"Pulling of {request_model} over")

    # -------------------------------------------------------------------------
    def get_response(self, model, user_input, max_tokens, top_p, temperature):
        try:
            
            # If the model name is changed by the user
            if model != self.selected_name:
                self.check_local_model(model)
                self.selected_name = model
            
            # Existing setup for other models       
            chat_completion = self.client.chat(model = self.selected_name,
                                          messages = [{"role": "user",
                                                       "content": user_input}],
                                          options={"temperature":temperature,
                                                   "top_p": top_p,
                                                   "num_predict":max_tokens}
                                          )

            return chat_completion['message']['content'], None
        except ollama.ResponseError as e:
            return None, str(e)

    # -------------------------------------------------------------------------
    def clear_chat_history(self):
        st.session_state.messages = [{"role": "assistant",
                                      "content": "How may I assist you today?"}]


if __name__ == '__main__':
    main = MainThread()