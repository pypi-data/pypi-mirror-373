from typing import List, Literal, Union
from .api_base_model import ApiBaseModelName


class NarrativeContent(ApiBaseModelName):
    sectionNumber: str
    sectionTitle: str
    text: Union[str, None] = None
    childIds: List[str] = []
    previousId: Union[str, None] = None
    nextId: Union[str, None] = None
    instanceType: Literal["NarrativeContent"]
