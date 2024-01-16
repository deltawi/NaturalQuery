# llm_interface.py
import json
import requests
from abc import ABC, abstractmethod

class LLMInterface(ABC):
    def __init__(self, api_key: str, endpoint_url: str, offline: bool=True):
        self.api_key = api_key
        self.endpoint_url = endpoint_url
        self.offline = offline
    
    def query_llm(self):
        pass

class MixtralInterface(LLMInterface):

    def query_llm(self, prompt, system_prompt="You are a helpful coding AI assistant"):
        # Here you would implement the actual call to the LLM API.
        # This is a placeholder implementation.
        # For example, if using OpenAI's GPT-3, you would use their API here.
        if self.offline:
            return self.prompt_llm_offline(user_prompt=prompt, system_prompt=system_prompt)
        else:
            return self.prompt_llm_online(user_prompt=prompt, system_prompt=system_prompt)

    def prompt_llm_offline(self, user_prompt, system_prompt):
        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": -1,
            "stream": False
        }

        response = requests.post(self.endpoint_url, headers=headers, data=json.dumps(data))
        return response.json()['choices'][0]['message']['content']
    
    def prompt_llm_online(self, user_prompt, system_prompt):
        import os
        s = requests.Session()

        api_base = os.getenv("OPENAI_BASE_URL", "https://api.endpoints.anyscale.com/v1")
        token = os.getenv("OPENAI_API_KEY", "esecret_pt7pwklepatz6w5dt7eflrharn")
        url = f"{api_base}/chat/completions"
        body = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [{"role": "system", "content": system_prompt}, 
                    {"role": "user", "content": user_prompt}],
        "temperature": 0.7
        }

        with s.post(url, headers={"Authorization": f"Bearer {token}"}, json=body) as resp:
            return resp.json()['choices'][0]['message']['content']
        
        return None