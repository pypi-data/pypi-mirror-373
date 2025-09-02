from motor.motor_asyncio import AsyncIOMotorDatabase
from ..schema import AddColumnField, FieldTypeEnum, CreateCollectionSchema
from typing import Optional, Any, List, Dict, TypeVar, Generic
from datetime import datetime, UTC
from uuid import uuid4
from pymongo.errors import PyMongoError, DuplicateKeyError, OperationFailure
from abs_exception_core.exceptions import GenericHttpError, BadRequestError, DuplicatedError,PermissionDeniedError
from pymongo import ASCENDING

T = TypeVar('T')

class BaseCollectionRepository(Generic[T]):
    """
    Base repository class for MongoDB collections with common CRUD operations.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize the repository with a MongoDB database connection.
        
        Args:
            db (AsyncIOMotorDatabase): MongoDB database instance
        """
        self.db = db
        self._validate_connection()

    def _validate_connection(self) -> None:
        """Validate the database connection."""
        try:
            # Try to get server info to validate connection
            self.db.client.server_info()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")

    def get_base_document_fields(self) -> Dict[str, Any]:
        """
        Get the base document fields that should be present in all documents.
        These fields match the BaseDocument class fields.
        
        Returns:
            Dict[str, Any]: Dictionary containing base document fields
        """
        return {
            "uuid": str(uuid4()),  # Unique identifier
            "created_at": datetime.now(UTC),  # Creation timestamp
            "updated_at": datetime.now(UTC)  # Last update timestamp
        }

    async def _handle_mongo_error(self, operation: str, error: Exception) -> None:
        """
        Handle MongoDB errors consistently with appropriate error types.
        
        Args:
            operation (str): Name of the operation that failed
            error (Exception): The error that occurred
            
        Raises:
            GenericHttpError: For general MongoDB errors
            BadRequestError: For invalid operations
            NotFoundError: For missing resources
        """
        
        if isinstance(error, DuplicateKeyError):
            raise BadRequestError(
                detail=f"Failed to {operation}: Duplicate key found"
            )
        elif isinstance(error, OperationFailure):
            raise BadRequestError(
                detail=f"Failed to {operation}: {str(error)}"
            )
        elif isinstance(error, PyMongoError):
            raise GenericHttpError(
                status_code=500,
                detail=str(error),
                error_type="PyMongoError",
                message=f"Failed to {operation}"
            )
        raise BadRequestError(detail=str(error))

    async def add_field(self, column: AddColumnField, collection_name: Optional[str] = None) -> bool:
        """
        Add a new field to all documents in the collection.
        
        Args:
            column (AddColumnField): Column configuration
            collection_name (Optional[str]): Name of the collection
            
        Returns:
            bool: True if operation was successful
            
        Raises:
            BadRequestError: If collection name is invalid or operation fails
        """
        if not collection_name:
            raise BadRequestError(detail="Collection name is required")
        
        try:
            collection = self.db[collection_name]
            result = await collection.update_many(
                {column.column_field: {"$exists": False}},
                {"$set": {column.column_field: column.column_default or self.get_default_for_type(column.column_type)}}
            )
            if column.column_index:
                await collection.create_index(column.column_field)
            return True
                    
        except Exception as e:
            await self._handle_mongo_error("add field", e)

    async def delete_field(self, column_name: str, collection_name: Optional[str] ,protected_fields:Optional[List[str]]=None) -> bool:
        """
        Delete a field from all documents in the collection.
        
        Args:
            column_name (str): Name of the field to delete
            collection_name (Optional[str]): Name of the collection
            protected_fields (List[str]): List of protected fields
            
        Returns:
            bool: True if operation was successful
            
        Raises:
            BadRequestError: If collection name is invalid
        """
        if not collection_name:
            raise BadRequestError(detail="Collection name is required")
        if protected_fields is None:
            protected_fields = ["_id","uuid","created_at","updated_at","name"]
        else:
            protected_fields = protected_fields+["_id","uuid","created_at","updated_at","name"]

        if protected_fields and column_name in protected_fields:
            raise PermissionDeniedError("Requested field cannot be deleted.")
            
        try:
            collection = self.db[collection_name]
            result = await collection.update_many(
                {},
                {"$unset": {column_name: ""}}
            )
            
            return True
                    
        except Exception as e:
            await self._handle_mongo_error("delete field", e)

    async def rename_field(self, old_name: str, new_name: str, collection_name: Optional[str] = None) -> bool:
        """
        Rename a field in all documents in the collection.
        
        Args:
            old_name (str): Current name of the field
            new_name (str): New name of the field
            collection_name (Optional[str]): Name of the collection
            
        Returns:
            bool: True if operation was successful
            
        Raises:
            BadRequestError: If collection name is invalid or target field already exists
        """
        if not collection_name:
            raise BadRequestError(detail="Collection name is required")
        
        try:
            collection = self.db[collection_name]
            
            # Check if target field exists in any records
            existing_docs = await collection.find({new_name: {"$exists": True}}).to_list(length=1)
            if existing_docs:
                raise DuplicatedError(
                    detail=f"Cannot rename field to '{new_name}' as it already exists in some records"
                )
            
            result = await collection.update_many(
                {},
                {"$rename": {old_name: new_name}}
            )
            
            return True
                    
        except Exception as e:
            await self._handle_mongo_error("rename field", e)
            
    

    async def create_collection(self, collection_data: CreateCollectionSchema) -> bool:
        """
        Create a new collection with default values.
        
        Args:
            collection_data (CreateCollectionSchema): Collection configuration
            
        Returns:
            bool: True if operation was successful
            
        Raises:
            BadRequestError: If collection name is invalid or operation fails
        """
        
        try:
            collection = self.db[collection_data.collection_name]
            default_fields = collection_data.default_values or {}
            base_fields = self.get_base_document_fields()
            full_doc = {**base_fields, **default_fields}

            collection.create_index([("_id", ASCENDING)])
            collection.create_index([("uuid", ASCENDING)])

            
            await collection.insert_one(full_doc)
            return True
                    
        except Exception as e:
            await self._handle_mongo_error("create collection", e)

    async def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection.
        
        Args:
            collection_name (str): Name of the collection to delete
            
        Returns:
            bool: True if operation was successful
        """
        
        try:
            await self.db.drop_collection(collection_name)
            return True
            
        except Exception as e:
            await self._handle_mongo_error("delete collection", e)

    async def rename_collection(self, old_name: str, new_name: str) -> bool:
        """
        Rename a collection in MongoDB.
        
        Args:
            old_name (str): Current collection name
            new_name (str): New collection name
            
        Returns:
            bool: True if operation was successful
            
        Raises:
            BadRequestError: If collection names are invalid
        """
        
        try:
            full_old = f"{self.db.name}.{old_name}"
            full_new = f"{self.db.name}.{new_name}"

            admin_db = self.db.client.admin

            await admin_db.command({
                "renameCollection": full_old,
                "to": full_new,
                "dropTarget": False 
            })

            return True
            
        except Exception as e:
            await self._handle_mongo_error("rename collection", e)

    async def get_collection_names(self) -> List[str]:
        """
        Get all collection names in the database.
        
        Returns:
            List[str]: List of collection names
        """
        try:
            return await self.db.list_collection_names()
        except Exception as e:
            await self._handle_mongo_error("get collection names", e)

    @staticmethod
    def get_default_for_type(field_type: FieldTypeEnum) -> Any:
        """
        Get default value for a field type.
        
        Args:
            field_type (FieldTypeEnum): Type of the field
            
        Returns:
            Any: Default value for the field type
        """
        default_values = {
            FieldTypeEnum.STR: "",
            FieldTypeEnum.INT: 0,
            FieldTypeEnum.BOOL: False,
            FieldTypeEnum.FLOAT: 0.0,
            FieldTypeEnum.LIST: [],
            FieldTypeEnum.DICT: {},
            FieldTypeEnum.DATETIME: None,
            FieldTypeEnum.DATE : None
        }
        return default_values.get(field_type) or ""
