# query_translator/language_translator.py
from query_translator.llm_interface import MixtralInterface

class LanguageTranslator:
    def __init__(self, llm_api_key, llm_api_url):
        self.llm = MixtralInterface(llm_api_key, llm_api_url)
    def translate_to_english(self, text, source_language):
        # Implement translation logic
        # This is a placeholder
        prompt = f"Translate this text from {source_language} to English:\n{text}"
        return self.llm.query_llm(prompt, system_prompt="You are a helpful assistant translating to english the provided text. Provide only the translated text as response.")

    def translate_from_english(self, text, target_language):
        # Implement translation logic
        # This is a placeholder
        prompt = f"Translate this text from English to {target_language}:\n{text}"
        return self.llm.query_llm(prompt, system_prompt=f"You are a helpful assistant translating to {target_language} the provided text. Provide only the translated text as response.")

