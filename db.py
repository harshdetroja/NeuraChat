import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
db_params = {
    "dbname": os.getenv("POSTGRES_DB_NAME"),
    "user": os.getenv("POSTGRES_DB_USER"),
    "password": os.getenv("POSTGRES_DB_PASSWORD"),
    "host": os.getenv("POSTGRES_DB_HOST"),
    "port": os.getenv("POSTGRES_DB_PORT")
}

# Connect to the database
conn = psycopg2.connect(**db_params)
cursor = conn.cursor()

# Enable pgvector extension
cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
conn.commit()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS document_tags (
    id SERIAL PRIMARY KEY,
    document_id INT REFERENCES documents(id) ON DELETE CASCADE,
    tag_id INT REFERENCES tags(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS document_information_chunks (
    id SERIAL PRIMARY KEY,
    document_id INT REFERENCES documents(id) ON DELETE CASCADE,
    chunk TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL
);
""")

# Create HNSW index for vector search
cursor.execute("""
CREATE INDEX IF NOT EXISTS vector_index
ON document_information_chunks USING hnsw (embedding vector_cosine_ops);
""")

# Commit changes
conn.commit()

def set_diskann_query_rescore(query_rescore: int):
    cursor.execute("SET diskann.query_rescore = %s;", (query_rescore,))
    conn.commit()

def set_openai_api_key():
    cursor.execute(
        """
        SET ai.openai_api_key = %s;
        SELECT pg_catalog.current_setting('ai.openai_api_key', true) AS api_key;
        """,
        (os.getenv("OPENAI_API_KEY"),)
    )
    conn.commit()

# Close connection
cursor.close()
conn.close()
