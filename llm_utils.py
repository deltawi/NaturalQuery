import torch
import re
from transformers import AutoTokenizer, AutoModelForCausalLM
import pandas as pd

HG_CHAT_LLM_MODEL_PATH = "meta-llama/Llama-2-7b-chat-hf"
HG_SQL_LLM_MODEL_PATH = "defog/sqlcoder-7b"
MANIFEST_CLIENT_URL = "http://127.0.0.1:5001"

def get_llm_model(model_name: str="meta-llama/Llama-2-7b-chat-hf", device: str="gpu"):
    return  AutoModelForCausalLM.\
        from_pretrained(model_name, torch_dtype=torch.float16).\
        to(device)

def get_tokenizer(model_name: str="meta-llama/Llama-2-7b-chat-hf"):
    return AutoTokenizer.from_pretrained(model_name)

def find_device() -> str:
    # Check if CUDA (GPU support) is available
    if torch.cuda.is_available():
        device = torch.device("cuda")
    # If not, check for Metal Performance Shaders (MPS) for Apple Silicon
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    # Fallback to CPU if neither CUDA nor MPS is available
    else:
        device = torch.device("cpu")

    return device


def extract_sql_code(text):
    # Regular expression pattern to match text between ```sql and ```
    pattern = r'```sql(.*?)```'
    
    # Using re.DOTALL to make '.' match any character including newline
    matches = re.findall(pattern, text, re.DOTALL)

    return matches[0]

def prompt_llm_offline(prompt: str, max_length: int=2000, model_name: str=HG_CHAT_LLM_MODEL_PATH) -> str:
    print("Loading model...")
    device = find_device()
    print(f"Using device {device}.")
    tokenizer = get_tokenizer(model_name=model_name)
    model = get_llm_model(model_name=model_name, device=device)
    print("Tokenizing....")
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids

    # Move the input to the MPS device
    input_ids = input_ids.to(device)

    print("Generating...")
    generated_ids = model.generate(input_ids, max_length=max_length)
    response = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
    return response

def prompt_llm_online(prompt: str, max_length: int=2000):
    manifest_client = Manifest(client_name="huggingface", client_connection=MANIFEST_CLIENT_URL)
    response = manifest_client.run(prompt, max_tokens=max_length)
    return response

def add_comment_to_sql(table_str: str, debug=False):
    """Add SQL comments to SQL DDL using LLM"""
    # Update the prompt with the specific format including INST tags, BOS and EOS tokens
    system_prompt = f'You are an assistant to a SQL developer. He gives a SQL database definition and you give him back the same SQL with comments that explain each column. For example : "company_id SERIAL PRIMARY KEY," becomes "company_id SERIAL PRIMARY KEY, -- company_id is the company unique ID". \n- It is important to keep all existing comments in the given SQL.\n- Do not remove something from the SQL, just add to it.\n- Add comments to all columns of each table.\n- If a column name is an abreviation try to give a description of it.'
    user_message = f"Below is an SQL table definition: \n```sql\n{table_str}\n```"
    formatted_prompt = f"""
<s>[INST] <<SYS>>
{ system_prompt }
<</SYS>>

{ user_message } [/INST]
"""
    if debug:
        print(formatted_prompt)
    response = prompt_llm_offline(prompt=formatted_prompt)
    return extract_sql_code(response.split("[/INST]")[-1])

def interpret_sql_results(table_str: str, df: pd.DataFrame) -> str:
    system_prompt = f'You are an assistant to a SQL developer, you will help him interpret results of query execution. He gives a SQL database definition, SQL query he ran and the result it returns.\n- You go through the database definition for context.\n- You go through the SQL query and the question to prepare the response.\n- You use the response to provide a short sentence interpreting the results.'
    user_message = f"Below is an SQL table definition: \n```sql\n{table_str}\n```"
    formatted_prompt = f"""
    <s>[INST] <<SYS>>
    { system_prompt }
    <</SYS>>

    { user_message } [/INST]
    """
    response = prompt_llm_offline(prompt=formatted_prompt)
    return response