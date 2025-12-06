"""
Database Utilities
Provides helper functions for database operations during testing
"""

from pymongo import MongoClient
from typing import List, Dict, Optional
from test_config import config
import time


class DatabaseHelper:
    """Helper class for database operations"""

    def __init__(self, connection_string: str = None, db_name: str = None):
        """
        Initialize database helper

        Args:
            connection_string: MongoDB connection string
            db_name: Database name
        """
        self.connection_string = connection_string or config.DB_CONNECTION_STRING
        self.db_name = db_name or config.DB_NAME
        self.client = None
        self.db = None

    def connect(self):
        """Connect to the database"""
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.db_name]
            # Test connection
            self.client.server_info()
            return True
        except Exception as e:
            print(f"Failed to connect to database: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from the database"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None

    def clear_all_collections(self):
        """Drop all collections in the database"""
        if not self.db:
            self.connect()

        collections = self.db.list_collection_names()
        for collection_name in collections:
            self.db[collection_name].delete_many({})

        print(f"Cleared {len(collections)} collections")

    def clear_collection(self, collection_name: str):
        """
        Clear a specific collection

        Args:
            collection_name: Name of the collection to clear
        """
        if not self.db:
            self.connect()

        result = self.db[collection_name].delete_many({})
        print(f"Deleted {result.deleted_count} documents from {collection_name}")
        return result.deleted_count

    def get_collection_count(self, collection_name: str) -> int:
        """
        Get document count in a collection

        Args:
            collection_name: Name of the collection

        Returns:
            Number of documents
        """
        if not self.db:
            self.connect()

        return self.db[collection_name].count_documents({})

    def insert_document(self, collection_name: str, document: Dict) -> str:
        """
        Insert a document into a collection

        Args:
            collection_name: Name of the collection
            document: Document to insert

        Returns:
            Inserted document ID
        """
        if not self.db:
            self.connect()

        result = self.db[collection_name].insert_one(document)
        return str(result.inserted_id)

    def insert_many(self, collection_name: str, documents: List[Dict]) -> List[str]:
        """
        Insert multiple documents

        Args:
            collection_name: Name of the collection
            documents: List of documents to insert

        Returns:
            List of inserted document IDs
        """
        if not self.db:
            self.connect()

        result = self.db[collection_name].insert_many(documents)
        return [str(id) for id in result.inserted_ids]

    def find_one(self, collection_name: str, query: Dict) -> Optional[Dict]:
        """
        Find a single document

        Args:
            collection_name: Name of the collection
            query: Query filter

        Returns:
            Document or None
        """
        if not self.db:
            self.connect()

        return self.db[collection_name].find_one(query)

    def find_all(self, collection_name: str, query: Dict = None) -> List[Dict]:
        """
        Find all documents matching query

        Args:
            collection_name: Name of the collection
            query: Query filter (empty dict for all documents)

        Returns:
            List of documents
        """
        if not self.db:
            self.connect()

        query = query or {}
        return list(self.db[collection_name].find(query))

    def update_document(self, collection_name: str, query: Dict, update: Dict) -> int:
        """
        Update a document

        Args:
            collection_name: Name of the collection
            query: Query filter
            update: Update operations

        Returns:
            Number of documents modified
        """
        if not self.db:
            self.connect()

        result = self.db[collection_name].update_one(query, update)
        return result.modified_count

    def delete_document(self, collection_name: str, query: Dict) -> int:
        """
        Delete documents

        Args:
            collection_name: Name of the collection
            query: Query filter

        Returns:
            Number of documents deleted
        """
        if not self.db:
            self.connect()

        result = self.db[collection_name].delete_many(query)
        return result.deleted_count

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        return self.find_one("users", {"username": username})

    def get_course_by_id(self, course_id: str) -> Optional[Dict]:
        """Get course by ID"""
        return self.find_one("courses", {"_id": course_id})

    def get_enrollments_by_user(self, user_id: str) -> List[Dict]:
        """Get enrollments for a user"""
        return self.find_all("enrollments", {"user": user_id})

    def get_enrollments_by_course(self, course_id: str) -> List[Dict]:
        """Get enrollments for a course"""
        return self.find_all("enrollments", {"course": course_id})

    def wait_for_collection_count(self, collection_name: str, expected_count: int, timeout: int = 10) -> bool:
        """
        Wait for collection to reach expected count

        Args:
            collection_name: Name of the collection
            expected_count: Expected document count
            timeout: Timeout in seconds

        Returns:
            True if count reached, False if timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            count = self.get_collection_count(collection_name)
            if count == expected_count:
                return True
            time.sleep(0.5)
        return False

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Create global instance
db_helper = DatabaseHelper()
