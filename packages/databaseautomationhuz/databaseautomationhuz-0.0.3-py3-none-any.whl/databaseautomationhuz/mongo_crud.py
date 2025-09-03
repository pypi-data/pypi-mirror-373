from typing import Any
import pandas as pd
from pymongo.mongo_client import MongoClient
import json
from ensure import ensure_annotations


class MongoOperation:
    def __init__(self, client_url: str, database_name: str, collection_name: str = None):
        self.client_url = client_url
        self.database_name = database_name
        self.collection_name = collection_name
        self._client = None
        self._database = None
        self._collection = None

    def create_mongo_client(self):
        if self._client is None:
            self._client = MongoClient(self.client_url)
        return self._client

    def create_database(self):
        if self._database is None:
            client = self.create_mongo_client()
            self._database = client[self.database_name]
        return self._database

    def create_collection(self, collection_name: str = None):
        if collection_name:
            self.collection_name = collection_name

        if not self.collection_name:
            raise ValueError("Collection name must be provided.")

        if self._collection is None or self._collection.name != self.collection_name:
            database = self.create_database()
            self._collection = database[self.collection_name]

        return self._collection

    @ensure_annotations
    def insert_record(self, record: Any, collection_name: str) -> None:
        collection = self.create_collection(collection_name)

        if isinstance(record, list):
            if not all(isinstance(data, dict) for data in record):
                raise TypeError("Each record in the list must be a dict.")
            collection.insert_many(record)
        elif isinstance(record, dict):
            collection.insert_one(record)
        else:
            raise TypeError("Record must be a dict or list of dicts.")

    def bulk_insert(self, datafile: str, collection_name: str = None):
        if datafile.endswith('.csv'):
            dataframe = pd.read_csv(datafile, encoding='utf-8')
        elif datafile.endswith(".xlsx"):
            dataframe = pd.read_excel(datafile)
        else:
            raise ValueError("Unsupported file format. Use CSV or XLSX.")

        datajson = json.loads(dataframe.to_json(orient='records'))
        collection = self.create_collection(collection_name)
        collection.insert_many(datajson)
        return f"{len(datajson)} records inserted successfully into '{collection.name}'"
