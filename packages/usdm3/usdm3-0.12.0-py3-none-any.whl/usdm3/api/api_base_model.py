import json
import enum
import datetime
from typing import Union
from pydantic import BaseModel, Field
from uuid import UUID


def _serialize_as_json(obj):
    if isinstance(obj, enum.Enum):
        return obj.value
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, UUID):
        return str(obj)
    else:
        return obj.__dict__


class ApiBaseModel(BaseModel):
    id: str = Field(min_length=1)

    def to_json(self):
        return json.dumps(self, default=_serialize_as_json)


class ApiBaseModelAndDesc(ApiBaseModel):
    description: Union[str, None] = None


class ApiBaseModelName(ApiBaseModel):
    name: str = Field(min_length=1)


class ApiBaseModelNameLabelDesc(ApiBaseModelName):
    label: Union[str, None] = None
    description: Union[str, None] = None


class ApiBaseModelNameLabel(ApiBaseModelName):
    label: Union[str, None] = None


class ApiBaseModelNameDesc(ApiBaseModelName):
    description: Union[str, None] = None
