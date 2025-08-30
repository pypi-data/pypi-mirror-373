from pymongo import MongoClient
import os
from typing import Literal

class MongoManager:
    def __init__(self, mongo_uri=None):
        """
        mongo_uri: MongoDB connection string (optional). 
        If not provided, MongoDB saving will be disabled.
        """
        self.mongo_uri = mongo_uri or os.getenv("MONGO_URI")
        if self.mongo_uri:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client["sherlock-meta"]         # Fixed database name
            self.collection_error_insights = self.db["error-insights"]    # Fixed collection name
            self.collection_performance_insights = self.db["performance-insights"]
            self.enabled = True
            # print("✅ MongoDB backend enabled (DB: sherlock-meta, Collection: error-insights, performance-insights).")
        else:
            self.client = None
            self.enabled = False
            # print("ℹ️ MongoDB backend not configured.")

        self.collection_map = {
            "error-insights": self.collection_error_insights,
            "performance-insights": self.collection_performance_insights
        }

    def save(self, data, collection_name: Literal["error-insights", "performance-insights"]):
        """
        Saves data (Python dict) to MongoDB if backend is enabled.
        """
        if self.enabled:
            self.collection_map[collection_name].insert_one(data)
            # print(f"✅ Saved data to MongoDB (sherlock-meta.{collection_name}).")
        else:
            # print("ℹ️ Skipping MongoDB save (backend disabled).")
            pass
