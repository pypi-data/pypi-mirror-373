This is a simple Python package to help generate a SQL query from a given human understandable text.

you can call the function as below: 

from text_to_sql_llm_py.text_to_sql import generate_sql_query

generate_sql_query(llm, question, context)

llm: the llm model name.
question : the sql query needed.
context : additional information the model can use to generate query of higher accuracy.

Note: This project is open for improvements and the owner of this package is working on optimizing it. feel free to provide suggestions.