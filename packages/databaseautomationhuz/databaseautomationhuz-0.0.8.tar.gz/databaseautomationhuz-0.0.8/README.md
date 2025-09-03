# databseautomationhuz

This is a lightweight Python package that simplifies working with MongoDB. It provides an easy-to-use interface for creating clients, connecting to databases, managing collections, inserting single or multiple records, and performing bulk inserts directly from CSV or Excel files. With built-in type safety checks and automatic handling of database/collection creation, it reduces boilerplate code and prevents common errors when interacting with MongoDB. Ideal for data engineering, ETL pipelines, and machine learning projects that require structured data storage and quick dataset imports into MongoDB.

## Example Usage

```python
# Import the class
from databseautomationhuz.mongo_crud import MongoOperation

# Step 1: Initialize MongoDB connection
db = MongoOperation("client_url", "db_name", "collection_name")

# Step 2: Insert a single record
db.insert_record({"name": "Huzaifa", "age": 25}, "Users")

# Step 3: Insert multiple records
db.insert_record(
    [
        {"name": "Sara", "age": 30},
        {"name": "John", "age": 40}
    ],
    "Users"
)

# Step 4: Bulk insert from CSV
db.bulk_insert("employees.csv", "Employees")

# Step 5: Bulk insert from Excel
db.bulk_insert("sales_data.xlsx", "Sales")
