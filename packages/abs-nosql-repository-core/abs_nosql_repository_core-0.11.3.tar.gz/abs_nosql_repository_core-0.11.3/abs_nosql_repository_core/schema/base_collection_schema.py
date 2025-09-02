from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import UTC
from enum import Enum

class FieldTypeEnum(str, Enum):
    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    LIST = "list"
    DICT = "dict"
    DATETIME = "datetime"
    DATE = "date"

# Add column field schema
class AddColumnField(BaseModel):
    column_field:str
    column_type:FieldTypeEnum
    column_default:Optional[Any] = None
    column_index:Optional[bool] = False

class CreateCollectionSchema(BaseModel):
    collection_name:str
    default_values:Optional[Dict[str,Any]] = None