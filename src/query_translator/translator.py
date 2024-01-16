# translator.py

from cache.ddl_cache import DDLCache
from query_translator.llm_interface import LLMInterface, MixtralInterface
from query_translator.language_translator import LanguageTranslator
import hashlib
from connectors.base_connector import DatabaseConnector

SUPPORTED_LANGUAGES = ['En', 'Ar', 'Fr']

class QueryTranslator:
    def __init__(self, llm_api_key: str, 
                 llm_endpoint_url: str, 
                 db_connector: DatabaseConnector,
                 llm_offline: bool = True,
                 language: str="En"):
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language. Supported languages are: {SUPPORTED_LANGUAGES}")
        self.language = language
        self.language_translator = LanguageTranslator(llm_api_key, llm_endpoint_url)
        self.llm_interface = LLMInterface(llm_api_key, llm_endpoint_url, llm_offline)
        self.cacher = DDLCache()
        self.db_connector = db_connector

    def __hash_text(self, text: str):
        """ Hash a given text using SHA256 and return the hexadecimal hash. """
        return hashlib.sha256(text.encode()).hexdigest()
    
    def __extract_sql_code(self, text: str):
        import re
        # Regular expression pattern to match text between ```sql and ```
        sql_pattern = r'```sql(.*?)```'
        
        # Using re.DOTALL to make '.' match any character including newline
        sql_matches = re.findall(sql_pattern, text, re.DOTALL)

        # Check if SQL matches are found
        if sql_matches:
            return sql_matches[0]
        else:
            # If no SQL matches, look for VB.NET code blocks
            vbnet_pattern = r'```vbnet(.*?)```'
            vbnet_matches = re.findall(vbnet_pattern, text, re.DOTALL)
            if vbnet_matches:
                return vbnet_matches[0]
            else:
                return None
    
    def enrich_ddl_with_comments(self, database_ddl: str, force=False) -> str:
        # Get unique hash key
        hash_key = self.__hash_text(database_ddl)
        # If it's foreced then we delete the cach if exists
        if force:
            self.cacher.invalidate_cache(hash_key)
        # We check if it's cached already
        enriched_ddl = self.cacher.get_cached_ddl(hash_key)
        if enriched_ddl is not None:
            print("Using cached ddl...")
            return enriched_ddl
        # If not cached we create a new cache
        prompt = f"Enhance the following SQL DDL with comments:\n{database_ddl}"
        system_prompt="You are a helpful coding assistant. Add comments to all columns to describe them, do it for all tables provided."
        enriched_ddl = self.llm_interface.query_llm(prompt, system_prompt=system_prompt)
        # We cache the ddl to avoid calling llm twice
        self.cacher.cache_ddl(hash_key, enriched_ddl)
        return enriched_ddl
    
    def correct_sql_query(self, error: str):
        response = self.llm_interface.query_llm(
        system_prompt="You are a helpful SQL developer.",
        prompt=f"Fix the SQL query based on the error \n {error}.\nSQL DDL is the following:\n {self.enrich_ddl_with_comments(self.db_connector.get_all_schemas_ddl())}"
        )
        return self.__extract_sql_code(response)
    
    def translate_question_to_sql(self, question: str):
        database_ddl = self.enrich_ddl_with_comments(self.db_connector.get_all_schemas_ddl())
        database_type = self.db_connector.db_type
        prompt = f"Depending on the following SQL DDL answer the question in SQL for {database_type}: {question}\n {database_ddl}"
        sql_query = self.llm_interface.query_llm(prompt, system_prompt="You are a helpful SQL develper.\n-Reply with SQL code snippet.\n-If the question provided cannot be answered in the database return ```sql\n SELECT 'Answer is not in the database' AS Response;```")
        return self.__extract_sql_code(sql_query)

    def interpret_query_results(self, query: str, query_results, question: str):
        # Assuming query_results is a string or a format that LLM can interpret
        interpretation_prompt = f"Answer the following question based on this query {query} and the results of the execution of the query: {query_results}\n{question}.\nDon't give explanations, just answer the question."
        interpretation = self.llm_interface.query_llm(
            prompt=interpretation_prompt,
            system_prompt="You are a helpful assistant")
        return interpretation
    
    def answer(self, question: str) -> str:
        # Translate the question to English if necessary
        original_language = self.language
        if original_language != 'En':
            question = self.language_translator.translate_to_english(question, original_language)

        # Translate the question to sql statement
        sql_query = self.translate_question_to_sql(question)
        from pandas.errors import DatabaseError
        # Execute the query and get the final results
        try:
            exec_results = self.db_connector.query_to_dataframe(sql_query)
        except DatabaseError as exc:
            print("Trying to fix the query...")
            sql_query = self.correct_sql_query(exc)
            try:
                exec_results = self.db_connector.query_to_dataframe(sql_query)
            except:
                raise ValueError("Coulnd't find a valid sql to it.")
        # With the help of the LLM get a response in natural language
        response=self.interpret_query_results(
            query=sql_query, query_results=exec_results, question=question)
        
        # Translate the response back to the original language if necessary
        if original_language != 'En':
            response = self.language_translator.translate_from_english(response, original_language)

        return response
        
class MixtralQueryTranslator(QueryTranslator):
    def __init__(self, llm_api_key: str, llm_endpoint_url: str, db_connector: DatabaseConnector, llm_offline: bool = True, language: str="En"):
        super().__init__(
            llm_api_key=llm_api_key,
            llm_endpoint_url=llm_endpoint_url,
            db_connector=db_connector,
            llm_offline=llm_offline,
            language=language)
        self.llm_interface = MixtralInterface(llm_api_key, llm_endpoint_url, offline=llm_offline)