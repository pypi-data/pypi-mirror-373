from typing import List

from ..repository.base_collection_repository import BaseCollectionRepository
from ..schema import CreateCollectionSchema,AddColumnField

class BaseCollectionService:
    def __init__(self, repository: BaseCollectionRepository):
        self.repository = repository

    async def create_collection(self, collection: CreateCollectionSchema):
        return await self.repository.create_collection(collection)
    
    async def delete_collection(self, collection_name: str):
        return await self.repository.delete_collection(collection_name)
    
    async def get_collection_names(self):
        return await self.repository.get_collection_names()
    
    async def rename_collection(self, old_name: str, new_name: str):
        return await self.repository.rename_collection(old_name, new_name)
    
    async def add_field(self, field: AddColumnField, collection_name: str):
        return await self.repository.add_field( field,collection_name)
    
    async def delete_field(self, field: str, collection_name: str,protected_fields:List[str]):
        return await self.repository.delete_field(field,collection_name,protected_fields)
    
    async def rename_field(self, old_name: str, new_name: str, collection_name: str):
        return await self.repository.rename_field(old_name, new_name, collection_name)
    