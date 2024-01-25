
import yaml
import openai

# Step 1: Parse YAML Configuration
def parse_yaml_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

# Step 2: Provider Interface
class ProviderInterface:
    def send_prompt(self, prompt):
        raise NotImplementedError

# Step 3: Provider-Specific Classes
class OpenAIProvider(ProviderInterface):
    def __init__(self, config):
        self.model = config['llm']['model']
        self.model_kwargs = config['llm'].get('model_kwargs', {})
        self.client = openai.OpenAI(
            api_key = config['llm']['api_key']
        )

    def send_prompt(self, prompt):
        try:
            mandatory_params = {
                'model': self.model,
                'messages': prompt,
            }
            final_params = {**mandatory_params, **self.model_kwargs}

            response = self.client.chat.completions.create(
                **final_params
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

class CohereProvider(ProviderInterface):
    def __init__(self, config):
        import cohere
        self.model = config['llm']['model']
        self.model_kwargs = config['llm'].get('model_kwargs', {})
        self.client = cohere.Client(
            api_key = config['llm']['api_key']
        )
    
    def send_prompt(self, prompt):
        try:
            mandatory_params = {
                'model': self.model,
                'message': prompt,
            }
            final_params = {**mandatory_params, **self.model_kwargs}

            response = self.client.chat(
                **final_params
            )
            return response.text
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

class AnyscaleProvider(OpenAIProvider):
    def __init__(self, config):
        super().__init__(config)
        self.client = self.client = openai.OpenAI(
            base_url="https://api.endpoints.anyscale.com/v1",
            api_key = config['llm']['api_key']
        )

# Custom Provider Class
class CustomProvider(ProviderInterface):
    """
        Sends a prompt to a specified language model endpoint and returns the response.

        The method expects 'prompt' in the following format:
        {
          "messages": [
            {"role": "system", "content": "<System message content>"},
            {"role": "user", "content": "<User message content>"}
          ],
          "temperature": <float>,  // Optional: controls randomness
          "max_tokens": <int>,     // Optional: limits the response length
          "stream": <bool>         // Optional: streaming mode flag
        }

        The response is expected in the format:
        {
          "choices": [
            {
              "message": {
                "content": "<Response content from the language model>"
              }
            }
          ]
        }
    """
    def __init__(self, config):
        self.url = config['llm']['url']
        self.api_key = config['llm']['api_key']
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

    def send_prompt(self, prompt) -> str:
        """
        Args:
            prompt (dict): A dictionary containing the prompt details as specified above.

        Returns:
            str or None: The content of the language model's response if successful, None if an error occurs.
        """
        import requests
        data = {'messages': prompt}
        try:
            response = requests.post(self.url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

class LangChainProvider(ProviderInterface):
    # Implement LangChain specific methods
    pass

# Step 4: Factory Method
def get_provider(config):
    provider_name = config['llm']['provider']
    if provider_name == 'openai':
        return OpenAIProvider(config)
    elif provider_name == 'cohere':
        return CohereProvider(config)
    elif provider_name == 'anyscale':
        return AnyscaleProvider(config)
    elif provider_name == 'langchain':
        return LangChainProvider(config)
    elif provider_name == 'custom':
        return CustomProvider(config)
    else:
        raise ValueError("Unsupported provider")

# Step 5: Main Client Class
class LLMClient:
    def __init__(self, config_path):
        self.config = parse_yaml_config(config_path)
        self.provider = get_provider(self.config)

    def ask_question(self, prompt):
        return self.provider.send_prompt(prompt)
