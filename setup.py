from setuptools import setup, find_packages

setup(
    name='natural-query',
    version='0.0.1',
    author='Mehdi Tantaoui',
    author_email='tantaoui.mehdi@gmail.com',
    description='A tool to translate natural language queries to SQL using LLMs.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/deltawi/NaturalQuery',
    packages=find_packages(),
    package_dir={'': 'src'},
    install_requires=[
        'pandas>=2.0.0',
        'sqlalchemy<2.0.0',
        'transformers==4.36.2',
        'datasets==2.11.0',
        'jsonlines>=3.1.0',
        'sqlglot==11.5.5',
        'psycopg2-binary==2.9.9',
        'pydantic==2.5.3',
        'pyodbc==5.0.1',
        'openai==1.9.0',
        'cohere==4.44',
        'gradio',
        'typing-extensions',
        'pyyaml'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)
