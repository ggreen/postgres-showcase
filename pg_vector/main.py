import gradio as gr
import psycopg2
import os
import numpy as np
from openai import OpenAI
import ollama
from sentence_transformers import SentenceTransformer

# --- Environment Variables ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_PORT = os.getenv("DB_PORT", "5436")

# OpenAI API key (optional)
# export OPENAI_API_KEY="your_openai_api_key"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ollama embedding model name (ensure this model is downloaded and running locally)
# export OLLAMA_EMBEDDING_MODEL="nomic-embed-text"
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

# Hugging Face Sentence Transformer model name
# IMPORTANT: Most common HF models (like all-mpnet-base-v2) output 768 dimensions.
# Your database expects 1536 dimensions. If you use a 768-dim model,
# you will get a dimension mismatch error unless you re-embed your data
# and change your DB schema to vector(768).
# For direct compatibility with your 1536-dim DB, OpenAI is the recommended choice.
# If you proceed with a HF model, be aware of the dimension implications.
HF_EMBEDDING_MODEL = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2")

# Expected vector dimension based on your database schema
EXPECTED_VECTOR_DIMENSION = 1536

# --- Global Model Loaders (to avoid reloading on every request) ---
# Initialize SentenceTransformer model globally
# It will download the model the first time it's used if not cached locally.
try:
    hf_model = SentenceTransformer(HF_EMBEDDING_MODEL)
    print(f"Loaded Hugging Face model: {HF_EMBEDDING_MODEL} (Dimension: {hf_model.get_sentence_embedding_dimension()})")
except Exception as e:
    hf_model = None
    print(f"Could not load Hugging Face model {HF_EMBEDDING_MODEL}: {e}")
    print("Ensure 'sentence-transformers' is installed and the model name is correct.")


# --- Database Connection ---
def get_db_connection():
    """Establishes and returns a PostgreSQL database connection."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# --- Embedding Functions ---
def get_ollama_embedding(text):
    """
    Generates an embedding for the given text using a local Ollama model.
    Requires Ollama server to be running and the specified model to be pulled.
    """
    try:
        # Call Ollama to get embeddings
        response = ollama.embeddings(model=OLLAMA_EMBEDDING_MODEL, prompt=text)
        return response['embedding']
    except Exception as e:
        print(f"Error getting Ollama embedding: {e}")
        return None

def get_openai_embedding(text):
    """
    Generates an embedding for the given text using OpenAI's API.
    Requires OPENAI_API_KEY environment variable to be set.
    Uses 'text-embedding-ada-002' to match the 1536-dimension vector in the database.
    """
    if not OPENAI_API_KEY:
        print("OpenAI API key not set. Cannot use OpenAI embedding.")
        return None
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(
            input=text,
            model="text-embedding-ada-002" # This model produces 1536-dimension embeddings
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting OpenAI embedding: {e}")
        return None

def get_huggingface_embedding(text):
    """
    Generates an embedding for the given text using a Hugging Face Sentence Transformer model.
    """
    if hf_model is None:
        print("Hugging Face model not loaded. Cannot generate embedding.")
        return None
    try:
        # SentenceTransformer returns a numpy array, convert to list for PostgreSQL
        embedding = hf_model.encode(text).tolist()
        return embedding
    except Exception as e:
        print(f"Error getting Hugging Face embedding: {e}")
        return None

# --- Semantic Search Function ---
def semantic_search(query_text, model_choice, top_k=5):
    """
    Performs a semantic search on the public.articles table.
    Generates an embedding for the query and finds the most similar articles
    based on their 'content_vector'.
    """
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return "Failed to connect to the database. Please check your DB environment variables."

        embedding = None
        if model_choice == "Ollama":
            embedding = get_ollama_embedding(query_text)
        elif model_choice == "OpenAI":
            embedding = get_openai_embedding(query_text)
        elif model_choice == "HuggingFace":
            embedding = get_huggingface_embedding(query_text)
        else:
            return "Invalid model choice. Please select 'Ollama', 'OpenAI', or 'HuggingFace'."

        if embedding is None:
            return f"Failed to get embedding for the query using {model_choice}. Check model setup or API key."

        # --- Dimension Check ---
        if len(embedding) != EXPECTED_VECTOR_DIMENSION:
            return (
                f"Embedding dimension mismatch! Your chosen model ({model_choice}) "
                f"produced a {len(embedding)}-dimension vector, but the database "
                f"expects {EXPECTED_VECTOR_DIMENSION}-dimension vectors. "
                f"Please ensure your embedding model matches the database's vector dimension. "
                f"OpenAI's 'text-embedding-ada-002' provides 1536-dim vectors. "
                f"Most common Hugging Face models (like '{HF_EMBEDDING_MODEL}') provide 768-dim vectors."
            )

        # Convert the embedding list (from Python) to a string format
        # that PostgreSQL's pg_vector extension understands.
        # Example: [0.1, 0.2, ...] becomes '[0.1, 0.2, ...]'
        embedding_str = str(embedding)

        # SQL query to find semantically similar articles.
        # The '<=>' operator calculates the L2 distance (Euclidean distance) between vectors.
        # Ordering by L2 distance in ascending order finds the closest (most similar) vectors.
        # 1 - (vector <=> query_vector) converts L2 distance to cosine similarity (0 to 1).
        sql_query = f"""
        SELECT
            id,
            url,
            title,
            SUBSTRING(content FROM 1 FOR 300) || '...' AS truncated_content,
            1 - (content_vector <=> '{embedding_str}') AS similarity_score
        FROM
            public.articles
        ORDER BY
            content_vector <=> '{embedding_str}'
        LIMIT %s;
        """
        
        cur = conn.cursor()
        cur.execute(sql_query, (top_k,)) # Use parameterized query for LIMIT
        results = cur.fetchall()
        cur.close()

        if not results:
            return "No similar articles found for your query."

        output_markdown = "### Search Results:\n\n"
        for res_id, res_url, res_title, res_content_truncated, similarity in results:
            output_markdown += (
                f"**Title:** [{res_title}]({res_url})\n"
                f"**ID:** {res_id}\n"
                f"**Similarity Score:** {similarity:.4f}\n"
                f"**Content Snippet:** {res_content_truncated}\n\n"
                f"---\n\n"
            )
        return output_markdown

    except Exception as e:
        print(f"An unexpected error occurred during search: {e}")
        return f"An error occurred: {e}"
    finally:
        # Ensure the database connection is closed even if an error occurs
        if conn:
            conn.close()

# --- Gradio Web Interface Setup ---
iface = gr.Interface(
    fn=semantic_search,
    inputs=[
        gr.Textbox(lines=2, placeholder="Enter your search query here...", label="Search Query"),
        gr.Radio(["Ollama", "OpenAI", "HuggingFace"], label="Choose Embedding Model", value="Ollama")
    ],
    outputs=gr.Markdown(),
    title="Wikipedia Semantic Search",
    description=(
        "Search Wikipedia articles semantically using vector embeddings. "
        "Enter a query, choose an embedding model (Ollama, OpenAI, or HuggingFace), and get relevant articles. "
        "Ensure your PostgreSQL database is running, the 'articles' table is populated, "
        f"and your chosen embedding model produces {EXPECTED_VECTOR_DIMENSION}-dimension vectors. "
        "OpenAI's 'text-embedding-ada-002' provides 1536-dim vectors, matching your database. "
        "Most common Hugging Face models (like 'sentence-transformers/all-mpnet-base-v2') "
        "provide 768-dim vectors, which will cause a dimension mismatch error unless your "
        "database schema is updated or you use a 1536-dim Hugging Face model. "
        "Necessary environment variables (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT, "
        "OPENAI_API_KEY, OLLAMA_EMBEDDING_MODEL, HF_EMBEDDING_MODEL) must be set."
    ),
    live=False # Set to True if you want live updates as user types (can be resource intensive)
)

# --- Launch the Gradio App ---
if __name__ == "__main__":
    # Launch the Gradio interface.
    # The 'share=True' option generates a public link (useful for testing, but expires).
    # For local development, 'share=False' is typical.
    iface.launch(share=False)









# import gradio as gr
# import psycopg2
# import os
# import numpy as np
# from openai import OpenAI
# import ollama

# # --- Environment Variables ---
# DB_HOST = os.getenv("DB_HOST", "localhost")
# DB_NAME = os.getenv("DB_NAME", "postgres")
# DB_USER = os.getenv("DB_USER", "postgres")
# DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
# DB_PORT = os.getenv("DB_PORT", "5436")

# # OpenAI API key (optional)
# # export OPENAI_API_KEY="your_openai_api_key"
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# # Ollama embedding model name (ensure this model is downloaded and running locally)
# # export OLLAMA_EMBEDDING_MODEL="nomic-embed-text"
# OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

# # Expected vector dimension based on your database schema
# EXPECTED_VECTOR_DIMENSION = 1536

# # --- Database Connection ---
# def get_db_connection():
#     """Establishes and returns a PostgreSQL database connection."""
#     try:
#         conn = psycopg2.connect(
#             host=DB_HOST,
#             database=DB_NAME,
#             user=DB_USER,
#             password=DB_PASSWORD,
#             port=DB_PORT
#         )
#         return conn
#     except Exception as e:
#         print(f"Error connecting to database: {e}")
#         return None

# # --- Embedding Functions ---
# def get_ollama_embedding(text):
#     """
#     Generates an embedding for the given text using a local Ollama model.
#     Requires Ollama server to be running and the specified model to be pulled.
#     """
#     try:
#         # Call Ollama to get embeddings
#         response = ollama.embeddings(model=OLLAMA_EMBEDDING_MODEL, prompt=text)
#         return response['embedding']
#     except Exception as e:
#         print(f"Error getting Ollama embedding: {e}")
#         return None

# def get_openai_embedding(text):
#     """
#     Generates an embedding for the given text using OpenAI's API.
#     Requires OPENAI_API_KEY environment variable to be set.
#     Uses 'text-embedding-ada-002' to match the 1536-dimension vector in the database.
#     """
#     if not OPENAI_API_KEY:
#         print("OpenAI API key not set. Cannot use OpenAI embedding.")
#         return None
#     try:
#         client = OpenAI(api_key=OPENAI_API_KEY)
#         response = client.embeddings.create(
#             input=text,
#             model="text-embedding-ada-002" # This model produces 1536-dimension embeddings
#         )
#         return response.data[0].embedding
#     except Exception as e:
#         print(f"Error getting OpenAI embedding: {e}")
#         return None

# # --- Semantic Search Function ---
# def semantic_search(query_text, model_choice, top_k=5):
#     """
#     Performs a semantic search on the public.articles table.
#     Generates an embedding for the query and finds the most similar articles
#     based on their 'content_vector'.
#     """
#     conn = None
#     try:
#         conn = get_db_connection()
#         if not conn:
#             return "Failed to connect to the database. Please check your DB environment variables."

#         embedding = None
#         if model_choice == "Ollama":
#             embedding = get_ollama_embedding(query_text)
#         elif model_choice == "OpenAI":
#             embedding = get_openai_embedding(query_text)
#         else:
#             return "Invalid model choice. Please select 'Ollama' or 'OpenAI'."

#         if embedding is None:
#             return f"Failed to get embedding for the query using {model_choice}. Check model setup or API key."

#         # --- Dimension Check ---
#         if len(embedding) != EXPECTED_VECTOR_DIMENSION:
#             return (
#                 f"Embedding dimension mismatch! Your chosen model ({model_choice}) "
#                 f"produced a {len(embedding)}-dimension vector, but the database "
#                 f"expects {EXPECTED_VECTOR_DIMENSION}-dimension vectors. "
#                 f"Please ensure your embedding model matches the database's vector dimension. "
#                 f"OpenAI's 'text-embedding-ada-002' provides 1536-dim vectors."
#             )

#         # Convert the embedding list (from Python) to a string format
#         # that PostgreSQL's pg_vector extension understands.
#         # Example: [0.1, 0.2, ...] becomes '[0.1, 0.2, ...]'
#         embedding_str = str(embedding)

#         # SQL query to find semantically similar articles.
#         # The '<=>' operator calculates the L2 distance (Euclidean distance) between vectors.
#         # Ordering by L2 distance in ascending order finds the closest (most similar) vectors.
#         # 1 - (vector <=> query_vector) converts L2 distance to cosine similarity (0 to 1).
#         sql_query = f"""
#         SELECT
#             id,
#             url,
#             title,
#             SUBSTRING(content FROM 1 FOR 300) || '...' AS truncated_content,
#             1 - (content_vector <=> '{embedding_str}') AS similarity_score
#         FROM
#             public.articles
#         ORDER BY
#             content_vector <=> '{embedding_str}'
#         LIMIT %s;
#         """
        
#         cur = conn.cursor()
#         cur.execute(sql_query, (top_k,)) # Use parameterized query for LIMIT
#         results = cur.fetchall()
#         cur.close()

#         if not results:
#             return "No similar articles found for your query."

#         output_markdown = "### Search Results:\n\n"
#         for res_id, res_url, res_title, res_content_truncated, similarity in results:
#             output_markdown += (
#                 f"**Title:** [{res_title}]({res_url})\n"
#                 f"**ID:** {res_id}\n"
#                 f"**Similarity Score:** {similarity:.4f}\n"
#                 f"**Content Snippet:** {res_content_truncated}\n\n"
#                 f"---\n\n"
#             )
#         return output_markdown

#     except Exception as e:
#         print(f"An unexpected error occurred during search: {e}")
#         return f"An error occurred: {e}"
#     finally:
#         # Ensure the database connection is closed even if an error occurs
#         if conn:
#             conn.close()

# # --- Gradio Web Interface Setup ---
# iface = gr.Interface(
#     fn=semantic_search,
#     inputs=[
#         gr.Textbox(lines=2, placeholder="Enter your search query here...", label="Search Query"),
#         gr.Radio(["Ollama", "OpenAI"], label="Choose Embedding Model", value="Ollama")
#     ],
#     outputs=gr.Markdown(),
#     title="Wikipedia Semantic Search",
#     description=(
#         "Search Wikipedia articles semantically using vector embeddings. "
#         "Enter a query, choose an embedding model (Ollama or OpenAI), and get relevant articles. "
#         "Ensure your PostgreSQL database is running, the 'articles' table is populated, "
#         f"and your chosen embedding model produces {EXPECTED_VECTOR_DIMENSION}-dimension vectors. "
#         "Necessary environment variables (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT, "
#         "OPENAI_API_KEY, OLLAMA_EMBEDDING_MODEL) must be set."
#     ),
#     live=False # Set to True if you want live updates as user types (can be resource intensive)
# )

# # --- Launch the Gradio App ---
# if __name__ == "__main__":
#     # Launch the Gradio interface.
#     # The 'share=True' option generates a public link (useful for testing, but expires).
#     # For local development, 'share=False' is typical.
#     iface.launch(share=False)




# # import gradio as gr
# # import psycopg2
# # import os
# # import numpy as np
# # from openai import OpenAI
# # import ollama

# # # --- Environment Variables ---
# # DB_HOST = os.getenv("DB_HOST", "localhost")
# # DB_NAME = os.getenv("DB_NAME", "postgres")
# # DB_USER = os.getenv("DB_USER", "postgres")
# # DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
# # DB_PORT = os.getenv("DB_PORT", "5436")

# # # OpenAI API key (optional)
# # # export OPENAI_API_KEY="your_openai_api_key"
# # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# # # Ollama embedding model name (ensure this model is downloaded and running locally)
# # # export OLLAMA_EMBEDDING_MODEL="nomic-embed-text"
# # OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

# # # --- Database Connection ---
# # def get_db_connection():
# #     """Establishes and returns a PostgreSQL database connection."""
# #     try:
# #         conn = psycopg2.connect(
# #             host=DB_HOST,
# #             database=DB_NAME,
# #             user=DB_USER,
# #             password=DB_PASSWORD,
# #             port=DB_PORT
# #         )
# #         return conn
# #     except Exception as e:
# #         print(f"Error connecting to database: {e}")
# #         return None

# # # --- Embedding Functions ---
# # def get_ollama_embedding(text):
# #     """
# #     Generates an embedding for the given text using a local Ollama model.
# #     Requires Ollama server to be running and the specified model to be pulled.
# #     """
# #     try:
# #         # Call Ollama to get embeddings
# #         response = ollama.embeddings(model=OLLAMA_EMBEDDING_MODEL, prompt=text)
# #         return response['embedding']
# #     except Exception as e:
# #         print(f"Error getting Ollama embedding: {e}")
# #         return None

# # def get_openai_embedding(text):
# #     """
# #     Generates an embedding for the given text using OpenAI's API.
# #     Requires OPENAI_API_KEY environment variable to be set.
# #     Uses 'text-embedding-ada-002' to match the 1536-dimension vector in the database.
# #     """
# #     if not OPENAI_API_KEY:
# #         print("OpenAI API key not set. Cannot use OpenAI embedding.")
# #         return None
# #     try:
# #         client = OpenAI(api_key=OPENAI_API_KEY)
# #         response = client.embeddings.create(
# #             input=text,
# #             model="text-embedding-ada-002" # This model produces 1536-dimension embeddings
# #         )
# #         return response.data[0].embedding
# #     except Exception as e:
# #         print(f"Error getting OpenAI embedding: {e}")
# #         return None

# # # --- Semantic Search Function ---
# # def semantic_search(query_text, model_choice, top_k=5):
# #     """
# #     Performs a semantic search on the public.articles table.
# #     Generates an embedding for the query and finds the most similar articles
# #     based on their 'content_vector'.
# #     """
# #     conn = None
# #     try:
# #         conn = get_db_connection()
# #         if not conn:
# #             return "Failed to connect to the database. Please check your DB environment variables."

# #         embedding = None
# #         if model_choice == "Ollama":
# #             embedding = get_ollama_embedding(query_text)
# #         elif model_choice == "OpenAI":
# #             embedding = get_openai_embedding(query_text)
# #         else:
# #             return "Invalid model choice. Please select 'Ollama' or 'OpenAI'."

# #         if embedding is None:
# #             return f"Failed to get embedding for the query using {model_choice}. Check model setup or API key."

# #         # Convert the embedding list (from Python) to a string format
# #         # that PostgreSQL's pg_vector extension understands.
# #         # Example: [0.1, 0.2, ...] becomes '[0.1, 0.2, ...]'
# #         embedding_str = str(embedding)

# #         # SQL query to find semantically similar articles.
# #         # The '<=>' operator calculates the L2 distance (Euclidean distance) between vectors.
# #         # Ordering by L2 distance in ascending order finds the closest (most similar) vectors.
# #         # 1 - (vector <=> query_vector) converts L2 distance to cosine similarity (0 to 1).
# #         sql_query = f"""
# #         SELECT
# #             id,
# #             url,
# #             title,
# #             SUBSTRING(content FROM 1 FOR 300) || '...' AS truncated_content,
# #             1 - (content_vector <=> '{embedding_str}') AS similarity_score
# #         FROM
# #             public.articles1
# #         ORDER BY
# #             content_vector <=> '{embedding_str}'
# #         LIMIT %s;
# #         """
        
# #         cur = conn.cursor()
# #         cur.execute(sql_query, (top_k,)) # Use parameterized query for LIMIT
# #         results = cur.fetchall()
# #         cur.close()

# #         if not results:
# #             return "No similar articles found for your query."

# #         output_markdown = "### Search Results:\n\n"
# #         for res_id, res_url, res_title, res_content_truncated, similarity in results:
# #             output_markdown += (
# #                 f"**Title:** [{res_title}]({res_url})\n"
# #                 f"**ID:** {res_id}\n"
# #                 f"**Similarity Score:** {similarity:.4f}\n"
# #                 f"**Content Snippet:** {res_content_truncated}\n\n"
# #                 f"---\n\n"
# #             )
# #         return output_markdown

# #     except Exception as e:
# #         print(f"An unexpected error occurred during search: {e}")
# #         return f"An error occurred: {e}"
# #     finally:
# #         # Ensure the database connection is closed even if an error occurs
# #         if conn:
# #             conn.close()

# # # --- Gradio Web Interface Setup ---
# # iface = gr.Interface(
# #     fn=semantic_search,
# #     inputs=[
# #         gr.Textbox(lines=2, placeholder="Enter your search query here...", label="Search Query"),
# #         gr.Radio(["Ollama", "OpenAI"], label="Choose Embedding Model", value="Ollama")
# #     ],
# #     outputs=gr.Markdown(),
# #     title="Wikipedia Semantic Search",
# #     description=(
# #         "Search Wikipedia articles semantically using vector embeddings. "
# #         "Enter a query, choose an embedding model (Ollama or OpenAI), and get relevant articles. "
# #         "Ensure your PostgreSQL database is running, the 'articles' table is populated, "
# #         "and necessary environment variables (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, "
# #         "OPENAI_API_KEY, OLLAMA_EMBEDDING_MODEL) are set."
# #     ),
# #     live=False # Set to True if you want live updates as user types (can be resource intensive)
# # )

# # # --- Launch the Gradio App ---
# # if __name__ == "__main__":
# #     # Launch the Gradio interface.
# #     # The 'share=True' option generates a public link (useful for testing, but expires).
# #     # For local development, 'share=False' is typical.
# #     iface.launch(share=False)



