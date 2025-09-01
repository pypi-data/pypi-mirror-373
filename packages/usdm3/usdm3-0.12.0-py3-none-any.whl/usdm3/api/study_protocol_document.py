from typing import List, Literal
from .api_base_model import ApiBaseModelNameLabelDesc
from .study_protocol_document_version import StudyProtocolDocumentVersion


class StudyProtocolDocument(ApiBaseModelNameLabelDesc):
    versions: List[StudyProtocolDocumentVersion] = []
    instanceType: Literal["StudyProtocolDocument"]
