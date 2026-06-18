from pydantic import BaseModel
from typing import Dict, List, Any

class ColumnSchema(BaseModel):
    name: str
    data_type: str

class DatasetSchema(BaseModel):
    table_name: str
    columns: List[ColumnSchema]
    sample_data: List[Dict[str, Any]]

class UploadResponse(BaseModel):
    message: str
    table_name: str
    schema_info: DatasetSchema
