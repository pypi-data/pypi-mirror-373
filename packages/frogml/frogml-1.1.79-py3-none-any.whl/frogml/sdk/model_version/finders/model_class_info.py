from typing import Optional

from pydantic import BaseModel


class ModelClassInfo(BaseModel):
    file_path: str
    class_name: str
    model_field_name: Optional[str]
