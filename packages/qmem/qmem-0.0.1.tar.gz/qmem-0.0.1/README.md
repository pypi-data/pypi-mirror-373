qmem — Qdrant Memory Wrapper

qmem is a lightweight wrapper around Qdrant
 for easy ingestion and retrieval with embeddings.
Supports both CLI and Python API.

🚀 Install
pip install -e .

⚙️ CLI Usage
1. Init (set config)
qmem init

2. Ingest data
qmem ingest


You’ll be prompted for:

collection_name

data file path (JSON or JSONL)

field to embed (e.g. query, response, sql_query, doc_id)

payload fields (comma-separated, leave empty to keep all)

3. Retrieve results
qmem retrieve


You’ll be prompted for:

collection_name

query

top_k (number of results to return)

🐍 Python API
import qmem as qm

# Create collection
qm.create(collection_name="test_learn", dim=1536, distance_metric="cosine")

# Ingest data from file
qm.ingest(
    file="/home/aniruddha/Desktop/QMEM_PIP/qmem_pip/qmem/data.jsonl",
    embed_field="sql_query",
    payload_field="query,response",  # keep these in payload (optional)
)

# Retrieve results (pretty table by default)
table = qm.retrieve(query="list customers", top_k=5)
print(table)

📄 License

MIT