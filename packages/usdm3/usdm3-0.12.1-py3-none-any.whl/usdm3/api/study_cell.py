from typing import List, Literal
from .api_base_model import ApiBaseModel


class StudyCell(ApiBaseModel):
    armId: str
    epochId: str
    elementIds: List[str] = []
    instanceType: Literal["StudyCell"]
