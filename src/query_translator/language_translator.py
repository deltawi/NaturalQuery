# query_translator/language_translator.py
from query_translator.llm_interface import LLMClient

class LanguageTranslator:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    def translate_to_english(self, text, source_language):
        # Implement translation logic
        # This is a placeholder
        prompt = f"Translate this text from {source_language} to English:\n{text}"
        return self.llm_client.ask_question(
            [{"role": "system", "content": "You are a helpful assistant translating to english the provided text. Provide only the translated text as response."}, 
              {"role": "user", "content": prompt}])

    def translate_from_english(self, text, target_language):
        # Implement translation logic
        # This is a placeholder
        prompt = f"Translate this text from English to {target_language}:\n{text}"
        return self.llm_client.ask_question(
            [{"role": "system", "content": f"You are a helpful assistant translating to\
               {target_language} the provided text. Provide only the translated text as response."}, 
              {"role": "user", "content": prompt}])