from typing import List, Literal, Union
from .api_base_model import ApiBaseModel
from .study_identifier import StudyIdentifier
from .alias_code import AliasCode
from .code import Code
from .study_design import StudyDesign
from .governance_date import GovernanceDate
from .study_amendment import StudyAmendment
from .study_title import StudyTitle


class StudyVersion(ApiBaseModel):
    versionIdentifier: str
    rationale: str
    studyType: Union[Code, None] = None
    studyPhase: Union[AliasCode, None] = None
    documentVersionId: Union[str, None] = None
    dateValues: List[GovernanceDate] = []
    amendments: List[StudyAmendment] = []
    businessTherapeuticAreas: List[Code] = []
    studyIdentifiers: List[StudyIdentifier] = []
    studyDesigns: List[StudyDesign] = []
    titles: List[StudyTitle]
    instanceType: Literal["StudyVersion"]
