from operator import index
from typing import Type, TypeVar, List, Dict, Any, Union, Optional
from abs_exception_core.exceptions import (
    BadRequestError,
    NotFoundError,
    GenericHttpError,
    ValidationError,
)
from pydantic import BaseModel
from pymongo import ASCENDING, DESCENDING
from beanie.operators import Set
from pymongo.errors import PyMongoError
from datetime import datetime, UTC
from motor.motor_asyncio import AsyncIOMotorDatabase
from beanie import Document
from bson import ObjectId, Decimal128
from decimal import Decimal
from uuid import uuid4
import re
from abs_utils.azure_service_bus.azure_service_bus import AzureServiceBus
from abs_utils.socket_io.server import SocketIOService
from abs_utils.constants.event_constants import (
    ON_RECORD_CREATION,
    ON_RECORD_UPDATION,
    ON_RECORD_DELETION,
)
from ..schema import (
    ListFilter,
    SortDirection,
    Operator,
    FindUniqueByFieldInput,
    FieldRule,
    Aggregations,
    AggregationType,
    FilterSchema,
    SortSchema,
    AggregationStage,
    EmbeddingSchema,
    AuditLogSchema,
    AuditActionType,
    AuditSourceSchema
)
from ..util import coerce_value, apply_condition, logical_operator_map, convert_to_text
from abs_utils.logger import setup_logger


logger = setup_logger(__name__)
T = TypeVar("T", bound=BaseModel)
DocumentType = TypeVar("DocumentType", bound=Document)


class BaseRepository:
    """
    Base repository class for doing all the database operations using Beanie for NoSQL database.
    """

    def __init__(
        self,
        document: Type[DocumentType] = None,
        db: AsyncIOMotorDatabase = None,
        sio_service: SocketIOService = None,
        azure_service_bus: AzureServiceBus = None,
    ):
        if document is None and db is None:
            raise ValidationError(detail="Either document or db must be provided")
        self.document = document
        self.db = db
        self.sio_service = sio_service
        self.azure_service_bus = azure_service_bus

    def _convert_to_json_serializable(self, data: Any) -> Any:
        """
        Converts MongoDB documents to JSON-serializable format.
        """
        if data is None:
            return None

        # Fast path for common types
        if isinstance(data, (str, int, float, bool)):
            return data

        # Handle MongoDB specific types
        if isinstance(data, (ObjectId, Decimal128)):
            return str(data)

        if isinstance(data, datetime):
            return data.isoformat()

        if isinstance(data, Decimal):
            return float(data)

        # Handle collections
        if isinstance(data, dict):
            return {
                str(k): self._convert_to_json_serializable(v) for k, v in data.items()
            }

        if isinstance(data, (list, tuple, set)):
            return [self._convert_to_json_serializable(item) for item in data]

        # Handle Pydantic and Beanie models
        if isinstance(data, (BaseModel, Document)):
            return self._convert_to_json_serializable(data.model_dump())

        # Handle objects with __dict__
        if hasattr(data, "__dict__"):
            return self._convert_to_json_serializable(vars(data))

        # If we can't convert it, return string representation
        return str(data)

    def get_collection(self, collection_name: Optional[str] = None) -> Any:
        """Get the collection from the database"""
        return (
            self.db.get_collection(collection_name)
            if collection_name
            else self.document.get_motor_collection()
        )

    def get_base_document_fields(self) -> Dict[str, Any]:
        """Get the base document fields"""
        return {
            "uuid": str(uuid4()),
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }

    async def _handle_mongo_error(self, operation: str, error: Exception) -> None:
        """Handle MongoDB errors consistently."""
        if isinstance(error, PyMongoError):
            raise GenericHttpError(
                status_code=500,
                detail=str(error),
                error_type="PyMongoError",
                message=f"Failed to {operation}",
            )
        raise error

    def _coerce_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coerce all values in a document to their appropriate types.
        This is used before saving to the database to ensure proper type conversion.
        """
        return coerce_value(data)
    

    async def _send_audit_log(
                self,
                audit_log: AuditLogSchema,
                action_type: AuditActionType,
                collection_name: Optional[str] = None
        ):
        try:
            audit_log.collection_name = collection_name if collection_name else self.document.get_collection_name()
            audit_log.target_type = self.target_type if hasattr(self, "target_type") else None
            audit_log.action_type = action_type
            
            payload = audit_log.model_dump()
            payload["event_id"] = str(uuid4())
            payload["event_key"] = "audit_logs"

            if self.azure_service_bus:
                await self.azure_service_bus.send(self._convert_to_json_serializable(payload))

        except Exception as e:
            logger.error(f"Error sending audit log: {e}")

        return True


    async def create(
        self, obj: T, 
        collection_name: Optional[str] = None, 
        embedding_config: Optional[EmbeddingSchema] = None,
        audit_log: Optional[AuditLogSchema] = None
    ) -> Dict[str, Any]:
        """Create a new document in the collection"""
        try:
            # Convert to dict and coerce values
            obj_dict = obj.model_dump() if hasattr(obj, "model_dump") else dict(obj)
            obj_dict = self._coerce_document(obj_dict)

            if collection_name:
                collection = self.get_collection(collection_name)
                result = await collection.insert_one(
                    {**self.get_base_document_fields(), **obj_dict}
                )
                created_doc = await self.get_by_attr(
                    "_id", result.inserted_id, collection_name
                )
                entity_id = collection_name.split("_")[1]
                if audit_log: audit_log.target_id = created_doc["_id"]
                try:
                    if embedding_config and self.azure_service_bus:
                        payload = {
                            "event_id": str(uuid4()),
                            "event_key":"embedding",
                            "action":"creation",
                            "container_name": embedding_config.container_name,
                            "payload": [
                                {
                                    "id": str(result.inserted_id),
                                    "text": convert_to_text(created_doc),
                                    "metadata": {
                                        "entity_id": entity_id,
                                        "content":{
                                            "id":str(created_doc["_id"]),
                                            "created_at":created_doc["created_at"],
                                            "updated_at":created_doc["updated_at"],
                                            "uuid":created_doc["uuid"],
                                            "data":obj_dict
                                        }
                                    }
                                }
                            ]
                        }

                        await self.azure_service_bus.send(self._convert_to_json_serializable(payload))
                except Exception as e:
                    logger.error(f"Error sending embedding payload: {e}")
                    
                if self.sio_service or self.azure_service_bus:
                    payload = {
                        "event_id": str(uuid4()),
                        "event_key": ON_RECORD_CREATION,
                        "result": created_doc,
                        "payload": obj_dict,
                        "record_id": str(result.inserted_id),
                        "collection_name": collection_name,
                    }
                    if self.sio_service:
                        await self.sio_service.emit_to_room(
                            ON_RECORD_CREATION,f"entity:{entity_id}" ,payload
                        )
                    if self.azure_service_bus:
                        await self.azure_service_bus.send(self._convert_to_json_serializable(payload))
                        
            else :
                model_instance = self.document(**obj_dict)
                model = await model_instance.insert()
                created_doc = await self.get_by_attr("id", model.id)
                if audit_log: audit_log.target_id = created_doc["id"]


            if self.azure_service_bus and audit_log:
                audit_log.data = created_doc
                await self._send_audit_log(audit_log,AuditActionType.CREATION,collection_name)

            return created_doc
        except Exception as e:
            await self._handle_mongo_error("create document", e)

    async def bulk_create(
        self, data: List[T], 
        collection_name: Optional[str] = None, 
        embedding_config: Optional[EmbeddingSchema] = None,
        audit_log: Optional[AuditLogSchema] = None
    ) -> List[Dict[str, Any]]:
        """Create multiple documents in the collection"""
        try:

            # Convert to dicts and coerce values
            get_obj = lambda obj: (
                obj.model_dump() if hasattr(obj, "model_dump") else dict(obj)
            )
            coerced_data = [self._coerce_document(get_obj(item)) for item in data]

            if collection_name:
                collection = self.get_collection(collection_name)
                documents = [
                    {**self.get_base_document_fields(), **item} for item in coerced_data
                ]
                result = await collection.insert_many(documents)
                result_docs = []
                for doc in documents:
                    doc["_id"] = str(doc.get("_id", ""))
                    result_docs.append(self._convert_to_json_serializable(doc))

                created_docs = []
                entity_id = collection_name.split("_")[1]
                try:
                    if embedding_config and self.azure_service_bus:
                        for doc in result_docs:
                            doc_data = {}
                            doc_data["id"] = str(doc.get("_id", ""))
                            doc_data["text"] = convert_to_text(doc)
                            doc_data["metadata"] = {
                                "entity_id": entity_id,
                                "content":{
                                    "id":str(doc.get("_id", "")),
                                    "created_at":doc.get("created_at", ""),
                                    "updated_at":doc.get("updated_at", ""),
                                    "uuid":doc.get("uuid", ""),
                                    "data":doc
                                }
                            }
                            created_docs.append(doc_data)

                        payload = {
                            "event_id": str(uuid4()),
                            "event_key": "embedding",
                            "action": "creation",
                            "container_name": embedding_config.container_name,
                            "payload": created_docs
                        }

                        await self.azure_service_bus.send(self._convert_to_json_serializable(payload))
                except Exception as e:
                    logger.error(f"Error sending embedding payload: {e}")
                    
                # TODO: Add event handling for bulk create
                # payload = {
                #     "event_id": str(uuid4()),
                #     "event_key": "records_created",
                #     "payload": created_docs,
                #     "request_body": coerced_data,
                #     "collection_name": collection_name,
                # }
                # if self.sio_service:
                #     await self.sio_service.emit_broadcast(
                #         "records_created", payload
                #     )
                # if self.azure_service_bus:
                #     await self.azure_service_bus.send(payload)
            
            else :
                model_instances = [self.document(**item) for item in coerced_data]
                result = await self.document.insert_many(model_instances)
                
                result_docs = [
                    self._convert_to_json_serializable(doc.model_dump())
                    for doc in model_instances
                ]

            if self.azure_service_bus and audit_log:
                audit_log.data = result_docs
                await self._send_audit_log(audit_log,AuditActionType.BULK_CREATION,collection_name)

            return result_docs

        except Exception as e:
            await self._handle_mongo_error("bulk create documents", e)

    async def bulk_write(self, data: List[T], collection_name: Optional[str] = None):
        """Bulk write documents to the collection"""
        try:  
            collection = self.get_collection(collection_name)
            result = await collection.bulk_write(data,ordered=False)
            return result.upserted_count
        except Exception as e:
            await self._handle_mongo_error("bulk write documents", e)

    async def update(
        self, id: Union[str, ObjectId], obj: T, 
        collection_name: Optional[str] = None, 
        embedding_config: Optional[EmbeddingSchema] = None,
        audit_log: Optional[AuditLogSchema] = None
    ) -> Dict[str, Any]:
        """Update a document by id"""
        try:
            # remove none values from the object
            if hasattr(obj, "model_dump"):
                obj_dict = obj.model_dump(exclude_unset=True)
            else:
                obj_dict = obj

            # Convert to dict and coerce values
            obj_dict = self._coerce_document(obj_dict)
            object_id = ObjectId(id) if isinstance(id, str) else id
            if audit_log: audit_log.target_id = str(id)

            if collection_name:
                collection = self.get_collection(collection_name)
                previous_record = await self.get_by_attr("_id", object_id, collection_name)
                result = await collection.find_one_and_update(
                    {"_id": object_id},
                    {"$set": obj_dict, "$currentDate": {"updated_at": True}},
                    return_document=True
                )

                if result:
                    updated_doc = self._convert_to_json_serializable(result)
                else:
                    raise NotFoundError(detail=f"Document with id {id} not found")

                entity_id = collection_name.split("_")[1]
                try:
                    if embedding_config and self.azure_service_bus:
                        payload = {
                            "event_id": str(uuid4()),
                            "event_key": "embedding",
                            "action": "updation",
                            "container_name": embedding_config.container_name,
                            "payload": [
                                {
                                    "id": str(object_id),
                                    "text": convert_to_text(updated_doc),
                                    "metadata": {
                                        "entity_id": entity_id,
                                        "content":{
                                            "id":str(updated_doc.get("_id", "")),
                                            "created_at":updated_doc.get("created_at", ""),
                                            "updated_at":updated_doc.get("updated_at", ""),
                                            "uuid":updated_doc.get("uuid", ""),
                                            "data":updated_doc
                                        }
                                    }
                                }
                            ]
                        }

                        await self.azure_service_bus.send(self._convert_to_json_serializable(payload))
                except Exception as e:
                    logger.error(f"Error sending embedding payload: {e}")

                if self.sio_service or self.azure_service_bus:
                    payload = {
                        "event_id": str(uuid4()),
                        "event_key": ON_RECORD_UPDATION,
                        "previous_record": previous_record,
                        "result": updated_doc,
                        "payload": obj_dict,
                        "record_id": str(object_id),
                        "collection_name": collection_name,
                    }
                    if self.sio_service:
                        await self.sio_service.emit_to_room(
                            ON_RECORD_UPDATION,f"entity:{entity_id}" ,payload
                        )
                    if self.azure_service_bus:
                        await self.azure_service_bus.send(self._convert_to_json_serializable(payload))

            else :
                obj_dict["updated_at"] = datetime.now(UTC)
                result = await self.document.get(object_id)
                if not result:
                    raise NotFoundError(detail=f"Document with id {id} not found")

                await result.update(Set(obj_dict))
                updated_doc = await self.get_by_attr("id", object_id)


            if self.azure_service_bus and audit_log:
                audit_log.data = updated_doc
                await self._send_audit_log(audit_log,AuditActionType.UPDATION,collection_name)

            return updated_doc

        except Exception as e:
            await self._handle_mongo_error("update document", e)

    async def get_by_attr(
        self,
        attr: Union[str, Dict[str, Any]],
        value: Any = None,
        collection_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        try:
            # Handle multiple attributes
            if isinstance(attr, dict):
                query = {}
                for field, field_value in attr.items():
                    if field == "id":
                        field = "_id"
                        field_value = ObjectId(field_value)
                    query[field] = field_value
            else:
                if attr == "id":
                    attr = "_id"
                    value = ObjectId(value)
                query = {attr: value}

            if collection_name:
                collection = self.get_collection(collection_name)
                result = await collection.find_one(query)
                if not result:
                    raise NotFoundError(
                        detail=f"Document with {attr}={value} not found"
                    )
                return self._convert_to_json_serializable(result)

            if not self.document:
                raise ValueError("Document class is not provided.")

            result = await self.document.find_one(query)
            if not result:
                raise NotFoundError(detail=f"Document with {attr}={value} not found")
            return self._convert_to_json_serializable(result)

        except Exception as e:
            await self._handle_mongo_error("get document", e)

    async def get_many_by_attr(
        self,
        attr: Union[str, Dict[str, Any]],
        value: Any = None,
        collection_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get multiple documents by attribute"""
        try:
            if isinstance(attr, dict):
                query = {}
                for field, field_value in attr.items():
                    if field == "id":
                        field = "_id"
                        field_value = ObjectId(field_value)
                    query[field] = field_value
            else:
                if attr == "id":
                    attr = "_id"
                    value = ObjectId(value)
                query = {attr: value}

            if collection_name:
                collection = self.get_collection(collection_name)
                result = await collection.find(query).to_list(length=None)
                return [self._convert_to_json_serializable(doc) for doc in result]

            if not self.document:
                raise ValueError("Document class is not provided.")

            result = await self.document.find(query).to_list(length=None)
            return [self._convert_to_json_serializable(doc) for doc in result]
        except Exception as e:
            await self._handle_mongo_error("get many documents", e)
    

    def _build_search_conditions(
        self, search_term: str, searchable_fields: List[str]
    ) -> List[Dict[str, Any]]:
        """Build case-insensitive search conditions for fields"""
        try :         
            if not searchable_fields:
                return None
            
            if search_term.strip() == "":
                return [{field: ""} for field in searchable_fields]
     
            escaped_term = re.escape(search_term.strip())
            regex = {"$regex": f".*{escaped_term}.*", "$options": "i"}
            return [{field: regex} for field in searchable_fields]

        except Exception as e:
            return None
    

    def _build_query_filter(
        self, find: ListFilter, collection_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Build MongoDB filter from ListFilter"""
        if find.filters:
            if hasattr(find.filters, "model_dump"):
                filter = find.filters.model_dump(exclude_none=True)
            else:
                filter = {k: v for k, v in find.filters.items() if v is not None}
        else:
            filter = {}

        base_filter = (
            self._build_filter_condition(filter, collection_name, is_expr=False)
            if find.filters
            else None
        )
        
        if find.search and find.searchable_fields:
            search_conditions = self._build_search_conditions(find.search, find.searchable_fields)
            if search_conditions:
                search_filter = {
                    "$or": search_conditions
                }
                return (
                {"$and": [base_filter, search_filter]} if base_filter else search_filter
                )

        return base_filter


    def _build_filter_condition(
        self,
        filter_dict: Dict[str, Any],
        collection_name: Optional[str] = None,
        is_expr: bool = False,
    ) -> Dict[str, Any]:
        """Recursively build MongoDB filter"""
        if not isinstance(filter_dict, dict):
            return {}

        if "operator" in filter_dict and "conditions" in filter_dict:
            conditions = [
                self._build_filter_condition(cond, collection_name, is_expr)
                for cond in filter_dict["conditions"]
            ]
            return {logical_operator_map[filter_dict["operator"]]: conditions}

        if all(k in filter_dict for k in ["field", "operator", "value"]):
            try:
                model = self.document or self.db[collection_name]
                op = Operator(filter_dict["operator"].lower())
                if filter_dict["field"] == "id" or filter_dict["field"] == "_id":
                    if isinstance(filter_dict["value"], list):
                        value = [ObjectId(v) for v in filter_dict["value"]]
                    else:
                        value = ObjectId(filter_dict["value"])
                else:
                    value = coerce_value(filter_dict["value"])
                return apply_condition(model, op, filter_dict["field"], value, is_expr)
            except ValueError:
                raise BadRequestError(
                    f"Invalid comparison operator: {filter_dict['operator']}"
                )

        return {}

    def _get_sort_order(self, sort_order: List[SortSchema], for_aggregation: bool = False) -> Union[List[tuple], Dict[str, int]]:
        """Generate sort for MongoDB queries or aggregation pipelines"""
        if not sort_order:
            return [("created_at", DESCENDING)] if not for_aggregation else {"created_at": -1}
        
        if for_aggregation:
            return {
                s.field: (1 if s.direction == SortDirection.ASC else -1)
                for s in sort_order
            }
        else:
            return [
                (s.field, ASCENDING if s.direction == SortDirection.ASC else DESCENDING)
                for s in sort_order
            ]
    

    async def get_all(
        self, find: ListFilter, collection_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve documents with filtering, sorting, and pagination"""
        try :
            page = find.page or 1
            page_size = find.page_size or 20
            skip = (page - 1) * page_size
            pipeline = []

            if find.pre_filters:
                if hasattr(find.pre_filters, "model_dump"):
                    pre_filters = find.pre_filters.model_dump(exclude_none=True)
                else:
                    pre_filters = {
                        k: v for k, v in find.pre_filters.items() if v is not None
                    }
                pipeline.append(
                    {
                        "$match": self._build_filter_condition(
                            pre_filters, collection_name, is_expr=False
                        )
                    }
                )

            if find.reference_fields:
                pipeline = self._build_reference_stage(pipeline, find.reference_fields)

            query_filter = self._build_query_filter(find, collection_name)
            if query_filter:
                pipeline.append({"$match": query_filter})

            if find.field_rules:
                pipeline = self._get_field_rule(find.field_rules, pipeline, collection_name)
            if find.sort_order and not find.aggregations:
                pipeline.append({"$sort": self._get_sort_order(find.sort_order, for_aggregation=True)})


            if find.field_filter and not find.aggregations:
                field_filters = self._build_field_filters(find.field_filter)
                if field_filters:
                    pipeline.append({"$project": field_filters})

            model = self.document or self.db[collection_name]

            count_pipeline = pipeline + [{"$count": "total"}]
            count_result = await model.aggregate(count_pipeline).to_list(length=1)
            total_count = count_result[0]["total"] if count_result else 0

            if find.aggregations:

                projection = self._build_aggregation_projection(find) if find.aggregations.group_by else None
                if projection:
                    pipeline.append({"$project": projection})


                group_stage = self._build_group_stage(find.aggregations)
                if "$group" in group_stage and "count" not in group_stage["$group"]:
                    group_stage["$group"]["count"] = {"$sum": 1}

                pipeline.append(group_stage)

                
                pipeline += self._build_group_filter_stage(find.aggregations)
                
                if find.aggregations.group_options and getattr(find.aggregations.group_options, 'sort_by', None):
                    sort_by = self._get_sort_order(find.aggregations.group_options.sort_by, for_aggregation=True)
                elif find.sort_order and len(find.sort_order) > 0:
                    sort_by = self._get_sort_order(find.sort_order, for_aggregation=True)
                else:
                    sort_by = {"_id": -1}


                if sort_by:
                    pipeline.append({
                        "$set": {
                            "data": {
                                "$sortArray": {
                                    "input": "$data",
                                    "sortBy": sort_by
                                }
                            }
                        }
                    })


                pipeline.append(self._build_data_pagination_stage(find.aggregations))


                data = await model.aggregate(pipeline).to_list(length=None)

                count_pipeline = self._build_count_pipeline(pipeline)
                count_result = await model.aggregate(count_pipeline).to_list(length=1)
                total_groups = count_result[0]["total"] if count_result else len(data)
                group_options = getattr(find.aggregations, 'group_options', None)
                group_page = getattr(group_options, 'page', 1) if group_options else 1
                group_page_size = getattr(group_options, 'page_size', 10) if group_options else 10
                total_group_pages = (total_groups + group_page_size - 1) // group_page_size

                data, data_page, data_page_size = self._process_group_data(data, find)

                result = {
                    "founds": self._convert_to_json_serializable(data),
                    "total_groups": total_groups,
                    "search_options": {
                        "total_pages": None,
                        "total_count": total_count,
                        "page": None,
                        "page_size": None,
                        "search": find.search,
                        "sort_order": find.sort_order,
                    },
                }
                return result
            else:
                pipeline += [{"$skip": skip}, {"$limit": page_size}]
                data = await model.aggregate(pipeline).to_list(length=None)
                total_pages = (total_count + page_size - 1) // page_size

                return {
                    "founds": self._convert_to_json_serializable(data),
                    "search_options": {
                        "total_pages": total_pages,
                        "total_count": total_count,
                        "page": page,
                        "page_size": page_size,
                        "search": find.search,
                        "sort_order": find.sort_order,
                    },
                }
        except Exception as e:
            await self._handle_mongo_error("get_all", e)

    def _build_field_rules_stage(
        self, field_rules: List[FieldRule], collection_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Build $addFields stages for dynamic array inclusion/exclusion logic"""
        stages = []

        for rule in field_rules:
            action = rule.action.lower()
            field_path = rule.field
            conditions = rule.conditions

            if action not in ("include", "exclude"):
                raise ValueError(f"Unsupported filter action: {action}")
            
            if not conditions or not conditions.conditions:
                continue

            condition_expr = self._build_filter_condition(
                filter_dict=conditions.model_dump(),
                collection_name=collection_name,
                is_expr=True,
            )

            filter_condition = ( {"$not": [condition_expr]} if action == "exclude" else condition_expr)

            stages.append(
                {
                    "$addFields": {
                        field_path: {
                            "$filter": {
                                "input": f"${field_path}",
                                "as": "item",
                                "cond": filter_condition,
                            }
                        }
                    }
                }
            )

        return stages
    
    def _get_field_rule(
        self,
        field_rules: List[FieldRule],
        pipeline: List[Dict[str, Any]],
        collection_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Append field modifier stages to the aggregation pipeline."""
        if not field_rules:
            return pipeline

        field_rule_stages = self._build_field_rules_stage(field_rules, collection_name)
        pipeline.extend(field_rule_stages)
        return pipeline

    

    def _build_reference_stage(
        self, pipeline: List[Dict[str, Any]], references: AggregationStage
    ) -> List[Dict[str, Any]]:
        """Build reference stages supporting both flat and deeply nested alias paths."""
        if references and references.pipeline:
            return pipeline+references.pipeline
        else:
            return pipeline

    def _build_group_stage(self, group_agg: Aggregations) -> Dict[str, Any]:
        _id = (
            {field: f"${field}" for field in group_agg.group_by}
            if group_agg.group_by
            else None
        )
        group_stage = {"_id": _id}

 
        group_stage["data"] = {"$push": "$$ROOT"}


        if group_agg.aggregation_fields:
            for agg in group_agg.aggregation_fields:
                agg_type = agg.type.lower()
                field = agg.field
                alias = agg.alias

                if agg_type == "count":
                    group_stage[alias] = {"$sum": 1}
                elif agg_type in AggregationType:
                    group_stage[alias] = {f"${agg_type}": f"${field}"}
                else:
                    raise ValueError(f"Unsupported aggregation type: {agg_type}")
        return {"$group": group_stage}
    
    def _build_aggregation_projection(self, find: ListFilter) -> Dict[str, Any]:
        # Handle field projection before group stage for include type
        if find.field_filter and find.field_filter.fields and find.field_filter.type == "include":
            projection = self._build_field_filters(find.field_filter)
            # Ensure group_by fields are always included
            for field in find.aggregations.group_by:
                projection[field] = 1
            
        elif find.field_filter and find.field_filter.fields and find.field_filter.type == "exclude":
            # Remove group_by fields from exclusion
            for field in find.aggregations.group_by or []:
                if field in find.field_filter.fields:
                    find.field_filter.fields.remove(field)
            projection = self._build_field_filters(find.field_filter)
            
        elif (find.aggregations.document_inclusion_mode == "partial" and 
            find.aggregations.included_fields):
            # Create a temporary field_filter for partial mode
            temp_field_filter = type('obj', (object,), {
                'type': 'include',
                'fields': find.aggregations.included_fields
            })
            projection = self._build_field_filters(temp_field_filter)
            # Ensure group_by fields are always included
            for field in find.aggregations.group_by:
                projection[field] = 1
        else:
            return None
        
        return projection
    


    def _build_group_filter_stage(self, group_agg: Aggregations) -> list:
        try:
            group_options = getattr(group_agg, 'group_options', None)
            if group_options and getattr(group_options, 'group_id', None):
                # Convert values that look like ObjectId to proper ObjectId objects
                match_conditions = {}
                for k, v in group_options.group_id.items():
                    try:
                        if isinstance(v, list):
                            # Handle list of values
                            converted_values = []
                            for item in v:
                                if isinstance(item, str) and ObjectId.is_valid(item):
                                    converted_values.append(ObjectId(item))
                                else:
                                    converted_values.append(item)
                            match_conditions[f"_id.{k}"] = converted_values
                        else:
                            # Handle single value
                            if isinstance(v, str) and ObjectId.is_valid(v):
                                match_conditions[f"_id.{k}"] = ObjectId(v)
                            else:
                                match_conditions[f"_id.{k}"] = v
                    except (TypeError, ValueError):
                        # If conversion fails, use the original value
                        match_conditions[f"_id.{k}"] = v
                
                stage = [{"$match": match_conditions}]
                return stage
            return []
        except Exception as e:
            return []


    def _build_data_pagination_stage(self, group_agg: Aggregations) -> dict:
        try:
            group_options = getattr(group_agg, 'group_options', None)
            data_page = getattr(group_options, 'page', 1) if group_options else 1
            data_page_size = getattr(group_options, 'page_size', 10) if group_options else 10
            data_skip = (data_page - 1) * data_page_size

            stage = {
                "$set": {
                    "data": {
                        "$slice": [
                            "$data",  # Data is already sorted by the previous stage
                            data_skip,
                            data_page_size
                        ]
                    }
                }
            }
            return stage
        except Exception as e:
            # Fallback to default pagination without sorting
            return {
                "$set": {
                    "data": {
                        "$slice": [
                            "$data",
                            0,
                            data_page_size
                        ]
                    }
                }
            }

    def _build_count_pipeline(self, pipeline: list) -> list:
        """Build count pipeline for total groups calculation (matches old logic)"""
        count_pipeline = pipeline[:]
        # Remove $set stage for count
        if count_pipeline and "$set" in count_pipeline[-1]:
            count_pipeline = count_pipeline[:-1]
        count_pipeline.append({"$count": "total"})
        return count_pipeline

    def _process_group_data(self, data: list, find: ListFilter) -> tuple:
        try:
            group_options = getattr(find.aggregations, 'group_options', None)
            data_page = getattr(group_options, 'page', 1) if group_options else 1
            data_page_size = getattr(group_options, 'page_size', 10) if group_options else 10
            for group in data:
                try:
                    group['data'] = self._convert_to_json_serializable(group.get("data", []))
                    total_records_in_group = group.get("count", len(group.get("data", [])))
                    total_data_pages = (total_records_in_group + data_page_size - 1) // data_page_size
                    group["data_pagination"] = {
                        "page": data_page,
                        "page_size": data_page_size,
                        "total_pages": total_data_pages,
                        "total_counts": total_records_in_group
                    }
                except Exception as e:
                    group["data_pagination"] = {
                        "page": data_page,
                        "page_size": data_page_size,
                        "total_pages": 0,
                        "total_counts": 0
                    }
            return data, data_page, data_page_size
        except Exception as e:
            return [], 1, 10

    async def delete(
        self, id: Union[str, ObjectId], 
        collection_name: Optional[str] = None, 
        embedding_config: Optional[EmbeddingSchema] = None,
        audit_log: Optional[AuditLogSchema] = None
    ) -> bool:
        """Delete a document by id"""
        try:
            object_id = ObjectId(id) if isinstance(id, str) else id

            if collection_name:
                collection = self.get_collection(collection_name)
                result = await collection.delete_one({"_id": object_id})
                if result.deleted_count == 0:
                    raise NotFoundError(detail="Document not found")
                if embedding_config and self.azure_service_bus:
                    try:
                        payload = {
                            "event_id": str(uuid4()),
                            "event_key": "embedding",
                            "action": "deletion",
                            "container_name": embedding_config.container_name,
                            "payload": [
                                {
                                    "id": str(object_id),
                                    "text": "",
                                    "metadata": None
                                }
                            ]
                        }
                        await self.azure_service_bus.send(self._convert_to_json_serializable(payload))
                    except Exception as e:
                        logger.error(f"Error sending embedding payload: {e}")
                    
                if self.sio_service or self.azure_service_bus:
                    payload = {
                        "event_id": str(uuid4()),
                        "event_key": ON_RECORD_DELETION,
                        "result": result.deleted_count,
                        "payload": None,
                        "record_id": str(id),
                        "collection_name": collection_name,
                    }
                    entity_id = collection_name.split("_")[1]
                    if self.sio_service:
                        await self.sio_service.emit_to_room(
                            ON_RECORD_DELETION,f"entity:{entity_id}" ,payload
                        )
                    if self.azure_service_bus:
                        await self.azure_service_bus.send(payload)

            else:
                result = await self.document.get(object_id)
                if not result:
                    raise NotFoundError(detail="Document not found")
                
                await result.delete()

            if self.azure_service_bus and audit_log:
                audit_log.target_id = str(id)
                await self._send_audit_log(audit_log,AuditActionType.DELETION,collection_name)

            return True

        except Exception as e:
            await self._handle_mongo_error("delete document", e)

    async def get_unique_values(
        self, schema: FindUniqueByFieldInput, collection_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get unique values for a field with pagination and search"""
        try:
            if not schema.field_name:
                raise BadRequestError(detail="Field name is required")

            collection = (
                self.get_collection(collection_name)
                if collection_name
                else self.document.get_motor_collection()
            )

            pipeline = []

            if schema.search:
                pipeline.append(
                    {
                        "$match": {
                            schema.field_name: {
                                "$regex": f".*{schema.search}.*",
                                "$options": "i",
                            }
                        }
                    }
                )

            pipeline.append({"$group": {"_id": f"${schema.field_name}"}})

            if schema.ordering:
                pipeline.append(
                    {
                        "$sort": {
                            "_id": ASCENDING if schema.ordering == "asc" else DESCENDING
                        }
                    }
                )

            count_pipeline = pipeline + [{"$count": "total"}]
            count_result = await collection.aggregate(count_pipeline).to_list(length=1)
            total_count = count_result[0]["total"] if count_result else 0

            skip = ((schema.page or 1) - 1) * (schema.page_size or 10)
            pipeline.extend([{"$skip": skip}, {"$limit": schema.page_size or 10}])

            results = await collection.aggregate(pipeline).to_list(length=None)
            values = [r["_id"] for r in results]

            return {
                "founds": values,
                "search_options": {
                    "page": schema.page or 1,
                    "page_size": schema.page_size or 10,
                    "ordering": schema.ordering or "asc",
                    "total_count": total_count,
                },
            }

        except Exception as e:
            await self._handle_mongo_error("get unique values", e)

    async def bulk_update(
        self,
        conditions: FilterSchema,
        update_data: Dict[str, Any],
        collection_name: Optional[str] = None,
        embedding_config: Optional[EmbeddingSchema] = None,
        audit_log: Optional[AuditLogSchema] = None
    ) -> int:
        """
        Update multiple documents based on ListFilter conditions

        Args:
            conditions: FilterSchema object containing filter conditions
            update_data: Dictionary of fields to update
            collection_name: Optional collection name
            embedding_config: Optional embedding config

        Returns:
            Dictionary containing update results
        """
        try:
            # Build the MongoDB filter from ListFilter
            if hasattr(conditions, "model_dump"):
                conditions = conditions.model_dump(exclude_none=True)
            else:
                conditions = {k: v for k, v in conditions.items() if v is not None}
            # Build the MongoDB filter from ListFilter
            mongo_filter = self._build_filter_condition(conditions, collection_name)

            # Coerce the update data to ensure proper type conversion
            update_data = self._coerce_document(update_data)
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.now(UTC)

            if mongo_filter:
                if collection_name:
                    entity_id = collection_name.split("_")[1]
                    collection = self.get_collection(collection_name)
                    data = await collection.find(mongo_filter).to_list(length=None)
                    ids = [item.get("_id", "") for item in data]
                    result = await collection.update_many(
                        mongo_filter, {"$set": update_data}
                    )
                    
                    try:
                        updated_docs = await collection.find({"_id": {"$in": ids}}).to_list(length=None)
                        if embedding_config and self.azure_service_bus:
                            payloads = []
                            for doc in updated_docs:
                                doc_data = {}
                                doc_data["id"] = str(doc.get("_id", ""))
                                doc_data["text"] = convert_to_text(doc)
                                doc_data["metadata"] = {
                                    "entity_id": entity_id,
                                    "content":{
                                        "id":str(doc.get("_id", "")),
                                        "created_at":doc.get("created_at", ""),
                                        "updated_at":doc.get("updated_at", ""),
                                        "uuid":doc.get("uuid", ""),
                                        "data":doc
                                    }
                                }
                                payloads.append(self._convert_to_json_serializable(doc_data))
                            payload = {
                                "event_id": str(uuid4()),
                                "event_key": "embedding",
                                "action": "updation",
                                "container_name": embedding_config.container_name,
                                "payload": payloads
                            }
                            await self.azure_service_bus.send(self._convert_to_json_serializable(payload))

                    except Exception as e:
                        logger.error(f"Error sending embedding payload: {e}")
                        
                    # TODO: Add event handling for bulk update
                    # payload = {
                    #     "event_id": str(uuid4()),
                    #     "event_key": "records_updated",
                    #     "payload": result,
                    #     "request_body": {
                    #         "conditions": conditions,
                    #         "update_data": update_data,
                    #     },
                    #     "collection_name": collection_name,
                    # }
                    # if self.sio_service:
                    #     await self.sio_service.emit_broadcast(
                    #         "records_updated", payload
                    #     )
                    # if self.azure_service_bus:
                    #     await self.azure_service_bus.send(payload)
                else:
                    result = await self.document.find(mongo_filter).update_many(
                        Set(update_data)
                    )
                    updated_docs = await self.document.find(mongo_filter).to_list(length=None)


                if self.azure_service_bus and audit_log:
                    audit_log.data = updated_docs
                    await self._send_audit_log(audit_log,AuditActionType.BULK_UPDATION,collection_name)

                return {
                    "modified_count": result.modified_count,
                    "matched_count": result.matched_count,
                    "upserted_id": result.upserted_id
                }
            else:
                raise BadRequestError(detail="No filter conditions provided")

        except Exception as e:
            await self._handle_mongo_error("bulk update documents", e)

    async def bulk_delete(
        self, conditions: FilterSchema, 
        collection_name: Optional[str] = None, 
        embedding_config: Optional[EmbeddingSchema] = None,
        audit_log: Optional[AuditLogSchema] = None
    ) -> int:
        """
        Delete multiple documents based on ListFilter conditions

        Args:
            conditions: FilterSchema object containing filter conditions
            collection_name: Optional collection name

        Returns:
            Dictionary containing deletion results
        """
        try:
            # Build the MongoDB filter from ListFilter
            if hasattr(conditions, "model_dump"):
                conditions = conditions.model_dump(exclude_none=True)
            else:
                conditions = {k: v for k, v in conditions.items() if v is not None}

            mongo_filter = self._build_filter_condition(conditions, collection_name)
            if mongo_filter:
                if collection_name:
                    collection = self.get_collection(collection_name)
                    data = await collection.find(mongo_filter).to_list(length=None)
                    ids = [str(item.get("_id", "")) for item in data]
                    result = await collection.delete_many(mongo_filter)
                    try:
                        if embedding_config and self.azure_service_bus and ids:
                            payloads = []
                            for id in ids:
                                doc_data = {}
                                doc_data["id"] = str(id)
                                payloads.append(self._convert_to_json_serializable(doc_data))
                            payload = {
                                "event_id": str(uuid4()),
                                "event_key": "embedding",
                                "action": "deletion",
                                "container_name": embedding_config.container_name,
                                "payload": payloads
                            }
                            await self.azure_service_bus.send(self._convert_to_json_serializable(payload))
                    except Exception as e:
                        logger.error(f"Error sending embedding payload: {e}")

                    # result = await collection.delete_many(mongo_filter)
                    # TODO: Add event handling for bulk delete
                    # payload = {
                    #     "event_id": str(uuid4()),
                    #     "event_key": "records_deleted",
                    #     "payload": result.deleted_count or None,
                    #     "request_body": conditions or None,
                    #     "collection_name": collection_name,
                    # }
                    # if self.sio_service:
                    #     await self.sio_service.emit_broadcast(
                    #         "records_deleted", payload
                    #     )
                    # if self.azure_service_bus:
                    #     await self.azure_service_bus.send(payload)
                else:
                    documents_to_delete = await self.document.find(mongo_filter).to_list(length=None)
                    ids = [str(doc.id) for doc in documents_to_delete]
                    result = await self.document.find(mongo_filter).delete_many()

                
                if self.azure_service_bus and audit_log:
                    audit_log.data = ids
                    await self._send_audit_log(audit_log,AuditActionType.BULK_DELETION,collection_name)
                    
                return { "deleted_count": result.deleted_count }
            
            else:
                raise BadRequestError(detail="No filter conditions provided")

        except Exception as e:
            await self._handle_mongo_error("bulk delete documents", e)


    def _build_field_filters(self, field_filter) -> Dict[str, Any]:
        if not field_filter or not field_filter.fields:
            return {}
        if len(field_filter.fields) == 0:
            return {}

        # Always include _id and rank at the root (or exclude if user wants)
        projection = {"_id": 1, "rank": 1} if field_filter.type == "include" else {}
        for field in field_filter.fields:
            if isinstance(field, str) and field not in ["_id", "rank"]:
                projection[field] = 1 if field_filter.type == "include" else 0
            elif isinstance(field, dict):
                for parent_field, nested_fields in field.items():
                    if isinstance(nested_fields, list):
                        nested_projection = self._build_nested_field_projection(
                            nested_fields, field_filter.type
                        )
                        if nested_projection:
                            projection[parent_field] = nested_projection
        return projection

    def _build_nested_field_projection(self, fields: List[Any], filter_type: str) -> Dict[str, Any]:
        projection = {}
        if filter_type == "include":
            projection["_id"] = 1
            projection["rank"] = 1
        for field in fields:
            if isinstance(field, str) and field not in ["_id", "rank"]:
                projection[field] = 1 if filter_type == "include" else 0
            elif isinstance(field, dict):
                for parent_field, nested_fields in field.items():
                    if isinstance(nested_fields, list):
                        nested_projection = self._build_nested_field_projection(
                            nested_fields, filter_type
                        )
                        if nested_projection:
                            projection[parent_field] = nested_projection
        return projection
