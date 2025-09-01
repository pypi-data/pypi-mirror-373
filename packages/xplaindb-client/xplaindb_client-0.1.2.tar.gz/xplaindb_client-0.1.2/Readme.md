# XplainDB-Client - The Python Client for the XplainDB
[![PyPI version](https://img.shields.io/pypi/v/XplainDB-client.svg)](https://pypi.python.org/pypi/XplainDB-client)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL_v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

**`XplainDB-client`** is the official Python client for the **XplainDB**. It provides a simple, intuitive, and powerful interface for interacting with a XplainDB server, handling everything from database creation and security management to complex multi-model queries.

This client abstracts away the complexity of HTTP requests, allowing you to work with your SQL, NoSQL, Graph, and Vector data using clean, Pythonic code.

---
## Account Creation:
Get your account created at [XplainDB](https://xplaindb.xplainnn.com/signup/) and in [Dashboard](https://xplaindb.xplainnn.com/dashboard/), Check for the **Tenant Domain**
This is your **BASE_URL**.
## Installation

Install the client library directly from PyPI (once published) or locally from your project.

```bash
# Install using pip
pip install xplaindb-client
````

-----

## 📖 Getting Started: A Complete Walkthrough

This guide will walk you through creating a new database, managing its security, and using all four of its powerful data models.

### Step 1: Connecting and Creating a Database

The first step is always to connect to the XplainDB server and bootstrap your database. The `XplainDBClient.create_db()` class method handles this in one simple command. It will create the database if it doesn't exist and retrieve the root admin key.

```python
from xplaindb_client import XplainDBClient

# Configuration
BASE_URL = "http://127.0.0.1:8000"
DB_NAME = "my_new_application"

# Connect to the server. This creates 'my_new_application.XplainDB' and gets the admin key.
try:
    admin_client = XplainDBClient.create_db(base_url=BASE_URL, db_name=DB_NAME)
    #admin_client = XplainDBClient(base_url=BASE_URL, db_name=DB_NAME, api_key=API_KEY) if the database #already exists
    print("✅ Successfully connected as admin!")
    # In a real app, you would now save this key securely.
    my_admin_key = admin_client.api_key
except ConnectionError as e:
    print(f"❌ Error: {e}")
```

### Step 2: Access Management (RBAC)

With your `admin_client`, you can now create less-privileged keys for different parts of your application. This is a critical security practice.

```python
# Create a 'writer' key for your application's backend
writer_key_info = admin_client.create_api_key(permissions="writer")
writer_key = writer_key_info.get("api_key")
print(f"Created 'writer' key: {writer_key[:8]}...")

# Create a 'reader' key for an analytics dashboard
reader_key_info = admin_client.create_api_key(permissions="reader")
reader_key = reader_key_info.get("api_key")
print(f"Created 'reader' key: {reader_key[:8]}...")

# Now, create new clients to act as these roles
writer_client = XplainDBClient(base_url=BASE_URL, db_name=DB_NAME, api_key=writer_key)
reader_client = XplainDBClient(base_url=BASE_URL, db_name=DB_NAME, api_key=reader_key)
```

### Step 3: Using the Relational (SQL) Model

Use the `.sql()` method to execute any standard SQL command. This is ideal for your structured, transactional data.

```python
# The writer can create tables and insert data
writer_client.sql("CREATE TABLE IF NOT EXISTS customers (id INT, name TEXT, city TEXT)")
writer_client.sql("INSERT INTO customers VALUES (1, 'Alice', 'New York')")
print("\n--- SQL Operations ---")
print("✅ Writer added a customer.")

# The reader can select data
customers = reader_client.sql("SELECT * FROM customers WHERE city = 'New York'")
print(f"   Reader found customers: {customers}")

# The reader CANNOT write data (this would raise a ConnectionError: 403 Forbidden)
try:
    reader_client.sql("INSERT INTO customers VALUES (2, 'Bob', 'London')")
except ConnectionError as e:
    print("✅ Reader was correctly denied write access.")
```

### Step 4: Using the Document (NoSQL) Model

Use the `.nosql()` method for flexible, schema-less JSON documents.

```python
# The writer can insert complex documents
writer_client.nosql({
    "type": "insert",
    "collection": "product_reviews",
    "data": {
        "product_id": "laptop-123",
        "user_id": 1,
        "rating": 5,
        "comments": [{"user": "Bob", "text": "Great product!"}]
    }
})
print("\n--- NoSQL Operations ---")
print("✅ Writer added a product review.")

# The reader can search for documents
reviews = reader_client.nosql({
    "type": "search",
    "collection": "product_reviews",
    "query": {"rating": 5}
})
print(f"   Reader found reviews: {reviews}")
```

### Step 5: Using the Graph Model

Use the `.graph()` method to manage nodes and edges, perfect for modeling relationships.

```python
# The writer can build the graph
writer_client.graph({"type": "add_node", "node_id": "user:1", "properties": {"name": "Alice"}})
writer_client.graph({"type": "add_node", "node_id": "product:laptop-123", "properties": {"price": 1200}})
writer_client.graph({
    "type": "add_edge",
    "source": "user:1",
    "target": "product:laptop-123",
    "label": "PURCHASED"
})
print("\n--- Graph Operations ---")
print("✅ Writer created nodes and an edge.")

# The reader can query the relationships
purchases = reader_client.graph({"type": "get_neighbors", "node_id": "user:1"})
print(f"   Reader found what Alice purchased: {purchases}")
```

### Step 6: Using the Vector (AI) Model

Use the `.vector()` method to leverage the database's native AI capabilities for semantic search.

```python
# The writer (or admin) can add documents to be embedded by the server
documents_to_embed = [
    {"id": "doc1", "text": "A guide to high-performance computing"},
    {"id": "doc2", "text": "The history of deep learning models"},
    {"id": "doc3", "text": "An introduction to quantum physics"}
]
writer_client.vector({
    "type": "embed_and_add",
    "documents": documents_to_embed
})
print("\n--- Vector Operations ---")
print("✅ Writer sent text to the server for native embedding.")

# The reader can perform a semantic search using just text
# The server will create the query vector automatically
similar_docs = reader_client.vector({
    "type": "find_similar",
    "query_text": "AI and neural networks",
    "k": 1
})
print(f"   Reader searched for 'AI and neural networks' and found: {similar_docs}")
```

-----