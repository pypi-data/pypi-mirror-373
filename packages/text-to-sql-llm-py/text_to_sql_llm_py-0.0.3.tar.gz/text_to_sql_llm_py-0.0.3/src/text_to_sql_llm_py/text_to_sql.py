from huggingface_hub import hf_hub_download
from llama_cpp import Llama

def download_model(model_name, model_file):
    """
    Downloads the model from Hugging Face Hub based on user input.
    
    Args:
        model_name: The name of the model on Hugging Face Hub.
        model_file: The filename of the model to download.
    
    Returns:
        model_path: Path to the downloaded model.
    """
    model_path = hf_hub_download(model_name, filename=model_file)
    print(f"Model downloaded to: {model_path}")
    return model_path

def initialize_llama(model_path, n_ctx=512, n_threads=8, n_gpu_layers=40):
    """
    Initializes a Llama model object with the given configuration.
    
    Args:
        model_path: Path to the downloaded model.
        n_ctx: Number of context tokens (default is 512).
        n_threads: Number of threads to use (default is 8).
        n_gpu_layers: Number of GPU layers to use (default is 40).
    
    Returns:
        Llama object: Initialized Llama object ready for inference.
    """
    llm = Llama(
        model_path=model_path,
        n_ctx=n_ctx,
        n_threads=n_threads,
        n_gpu_layers=n_gpu_layers
    )
    print("Llama object initialized successfully.")
    return llm

def chat_template(question, context):
    """
    Creates a chat template for the Llama model to generate an SQL query.
    
    Args:
        question: The question to be answered.
        context: The context information to be used for generating the answer.
    
    Returns:
        A string containing the formatted chat template.
    """
    template = f"""\
    <|im_start|>user
    Given the context, generate an SQL query for the following question
    context:{context}
    question:{question}
    <|im_end|>
    <|im_start|>assistant 
    """
    # Clean up the whitespace.
    template = "\n".join([line.lstrip() for line in template.splitlines()])
    return template

def generate_sql_query(llm, question, context):
    """
    Uses the Llama model to generate an SQL query based on the question and context.
    
    Args:
        llm: The initialized Llama object.
        question: The question to be answered.
        context: The context information to be used for generating the answer.
    
    Returns:
        The generated SQL query.
    """
    output = llm(
        chat_template(question, context),
        max_tokens=512,
        stop=["</s>"],
    )
    return output['choices'][0]['text']

# Generalized execution example:

# 1. Get user input for model and file
model_name = input("Enter the Hugging Face model name: (e.x.: TheBloke/Mistral-7B-Instruct-v0.1-GGUF) ")
model_file = input("Enter the model file name (e.g., 'mistral-7b-instruct-v0.1.Q8_0.gguf'): ")

# 2. Download the model
model_path = download_model(model_name, model_file)

# 3. Initialize the Llama model
llm = initialize_llama(model_path)

# 4. Ask user for context and question
question = input("Enter the SQL query question: ")
context = input("Enter the context (e.g., table schema): ")
print("Processing... please wait")
# 5. Generate SQL query using the model
sql_query = generate_sql_query(llm, question, context)

# 6. Print the result
print("Generated SQL Query:")
print(sql_query)

# ------------------------------------------------------
