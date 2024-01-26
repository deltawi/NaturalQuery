# Natural query

Natural query is a tool that leverages you favorite large language models (LLMs) to translate natural language queries into SQL. It further augments the answers using the same LLM. This tool is highly beneficial for those who need to interact with databases in natural language.

## Get started

Install the library:
```bash
git clone https://github.com/deltawi/NaturalQuery.git
cd NaturalQuery
pip install -e .
```
## Example

```python
from naturalquery.query_translator import QueryTranslator

# Initialize the translator with the configuration file
query_translator = QueryTranslator(config_path="config.yaml")

# Translate and get an answer to a natural language query
query_translator.answer("Who are the suppliers with products that have the most reviews from costumers ?")
```
```text
The supplier with products that has the most reviews from customers is "Global Supplies" with a review count of 1.
```

## Features

- **Natural Language to SQL Conversion:** Translates questions posed in natural language to SQL queries.
- **Answer Augmentation:** Enhances the responses using the same LLM.
- **Support for Multiple LLM Providers:** Compatible with Anyscale, Cohere, OpenAI, and Custom API endpoints.
- **Configurable:** Allows customization through a `config.yaml` file.

## Configuration

### LLM Providers
- `anyscale`, `cohere`, `openai`, or `custom` for custom endpoints.
- API keys and model specifications are defined in the `config.yaml` file.
```yaml
llm:
  provider: anyscale
  api_key: <your_api_key>
  model: mistralai/Mixtral-8x7B-Instruct-v0.1
  model_kwargs:
    temperature: 0.7
    #max_tokens: 8000
database:
  provider: postgres
  dbname: postgres
  host: localhost
  port: 5432
  user: postgres
  password: <your_password>
  # user_env: USR_ENV_VAR
  # password_env: PWD_ENV_VAR

```

### Database Configuration
- Currently supports `PostgreSQL`, `SQLite` and `SQLServer`.
- Database connection details (host, port, user, password) are specified in the configuration file.

### Custom Endpoint Configuration
- For custom LLM providers, specify the `url` and additional `model_kwargs` as needed.
```yaml
llm:
  provider: custom
  api_key: somekey
  url: http://localhost:1234/v1/chat/completions
  model_kwargs:
    temperature: 0.7
    stream: False
```
## Usage

1. Import the `QueryTranslator` class from the package.
2. Initialize `QueryTranslator` with the path to your configuration file.
3. Call the `answer` method with your natural language query.
4. The response will be printed, which includes the SQL translation and augmented answer.

## Example

```python
from query_translator.translator import QueryTranslator

# Initialize the translator with the configuration file
query_translator = QueryTranslator(config_path="config.yaml")

# Translate and get an answer to a natural language query
answer = query_translator.answer("Who are the suppliers with products that have the most reviews from costumers ?")
print(answer)
```
```text
The supplier with products that has the most reviews from customers is "Global Supplies" with a review count of 1.
```

## Using French language

```python
from query_translator.translator import QueryTranslator

# Initialize the translator with the configuration file
query_translator = QueryTranslator(config_path="config.yaml", language="Fr")
query_translator.answer("Quels sont les fournisseurs qui ont des produits les plus notés par les clients ?")
```

```text
 Le fournisseur avec le plus de produits évalués par les clients est Global Supplies (supplierid = 1, avec 1 évaluation). Il est suivi de Quality Goods Inc. (supplierid = 2, avec également 1 évaluation).
```