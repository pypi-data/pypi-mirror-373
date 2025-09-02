from ..repository import BaseRepository
from ..schema import ListFilter,FindUniqueByFieldInput,FilterSchema,EmbeddingSchema, AuditLogSchema
from typing import Any, Dict, Optional,List

class BaseService:
    def __init__(self, repository: BaseRepository):
        self.repository = repository

    async def create(
            self, 
            data: dict, 
            collection_name: str = None, 
            embedding_config: EmbeddingSchema = None,
            audit_log: Optional[AuditLogSchema] = None) -> any:
        return await self.repository.create(data, collection_name, embedding_config, audit_log)
    
    async def bulk_create(
            self, data: list[any], 
            collection_name: str = None, 
            embedding_config: EmbeddingSchema = None,
            audit_log: Optional[AuditLogSchema] = None) -> list[any]:
        return await self.repository.bulk_create(data, collection_name, embedding_config, audit_log)
    
    async def get_by_attr(self, attr: str, value: any, collection_name: str = None) -> any:
        return await self.repository.get_by_attr(attr, value, collection_name)

    async def update(
            self, _id: str, 
            data: dict, 
            collection_name: str = None, 
            embedding_config: EmbeddingSchema = None,
            audit_log: Optional[AuditLogSchema] = None) -> any:
        return await self.repository.update(_id, data, collection_name, embedding_config, audit_log)
    
    async def delete(
            self, _id: str, 
            collection_name: str = None, 
            embedding_config: EmbeddingSchema = None,
            audit_log: Optional[AuditLogSchema] = None) -> any:
        return await self.repository.delete(_id, collection_name, embedding_config, audit_log)

    async def get_unique_values(self, schema: FindUniqueByFieldInput, collection_name: str = None) -> list[any]:
        return await self.repository.get_unique_values(schema, collection_name)
    
    async def get_all(self,find:ListFilter=dict,collection_name:str=None)->list[any]:
        return await self.repository.get_all(find,collection_name)
    
    async def bulk_update(
            self, 
            conditions: FilterSchema, 
            update_data: Dict[str, Any], 
            collection_name: Optional[str] = None, 
            embedding_config: EmbeddingSchema = None,
            audit_log: Optional[AuditLogSchema] = None) -> int:
        return await self.repository.bulk_update(conditions, update_data, collection_name, embedding_config, audit_log)
    
    async def bulk_delete(
            self, 
            conditions: FilterSchema, 
            collection_name: Optional[str] = None, 
            embedding_config: EmbeddingSchema = None,
            audit_log : Optional[AuditLogSchema] = None) -> int:
        return await self.repository.bulk_delete(conditions, collection_name, embedding_config, audit_log)
    
    async def bulk_write(self, data: List[any], collection_name: Optional[str] = None):
        return await self.repository.bulk_write(data, collection_name)