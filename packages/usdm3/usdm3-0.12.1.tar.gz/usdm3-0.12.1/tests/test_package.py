import json
from src.usdm3 import USDM3
from tests.rules.helpers import clear_rules_library
from usdm3.__info__ import __package_version__


def test_validate(tmp_path):
    # Create temporary test file
    clear_rules_library()
    test_file = tmp_path / "validate.json"
    with open(test_file, "w") as f:
        json.dump(_expected(), f)
    result = USDM3().validate(test_file)
    assert result.passed_or_not_implemented()


def test_validate_error(tmp_path):
    # Create temporary test file
    clear_rules_library()
    test_file = tmp_path / "validate.json"
    with open(test_file, "w") as f:
        json.dump(_bad(), f)
    result = USDM3().validate(test_file)
    # print(f"RESULT: {result._items['DDF00082']}")
    assert not result.passed_or_not_implemented()


def test_minimum():
    result = USDM3().minimum("Name", "ACME", "1")
    result.study.id = "FAKE-UUID"
    assert result.model_dump() == _expected()


def _bad():
    data = _expected()
    data["study"]["documentedBy"]["id"] = None
    return data


def _expected():
    return {
        "id": "Wrapper_1",
        "study": {
            "description": "",
            "documentedBy": {
                "description": "The study protocol document",
                "id": "StudyProtocolDocument_1",
                "instanceType": "StudyProtocolDocument",
                "label": "Study Protocol",
                "name": "PROTOCOL",
                "versions": [
                    {
                        "childIds": [],
                        "contents": [],
                        "dateValues": [],
                        "id": "StudyProtocolDocumentVersion_1",
                        "instanceType": "StudyProtocolDocumentVersion",
                        "protocolStatus": {
                            "code": "C25425",
                            "codeSystem": "cdisc.org",
                            "codeSystemVersion": "2024-09-27",
                            "decode": "Approved",
                            "id": "Code_3",
                            "instanceType": "Code",
                        },
                        "protocolVersion": "1",
                    },
                ],
            },
            "id": "FAKE-UUID",
            "instanceType": "Study",
            "label": "",
            "name": "Study",
            "versions": [
                {
                    "amendments": [],
                    "businessTherapeuticAreas": [],
                    "dateValues": [],
                    "documentVersionId": "StudyProtocolDocumentVersion_1",
                    "id": "StudyVersion_1",
                    "instanceType": "StudyVersion",
                    "rationale": "To be provided",
                    "studyDesigns": [],
                    "studyIdentifiers": [
                        {
                            "id": "StudyIdentifier_1",
                            "instanceType": "StudyIdentifier",
                            "studyIdentifier": "ACME",
                            "studyIdentifierScope": {
                                "id": "Organization_1",
                                "identifier": "To be provided",
                                "identifierScheme": "To be provided",
                                "instanceType": "Organization",
                                "label": None,
                                "legalAddress": None,
                                "name": "Sponsor",
                                "organizationType": {
                                    "code": "C70793",
                                    "codeSystem": "cdisc.org",
                                    "codeSystemVersion": "2024-09-27",
                                    "decode": "Clinical Study Sponsor",
                                    "id": "Code_2",
                                    "instanceType": "Code",
                                },
                            },
                        },
                    ],
                    "studyPhase": None,
                    "studyType": None,
                    "titles": [
                        {
                            "id": "StudyTitle_1",
                            "instanceType": "StudyTitle",
                            "text": "Name",
                            "type": {
                                "code": "C207616",
                                "codeSystem": "cdisc.org",
                                "codeSystemVersion": "2024-09-27",
                                "decode": "Official Study Title",
                                "id": "Code_1",
                                "instanceType": "Code",
                            },
                        },
                    ],
                    "versionIdentifier": "1",
                },
            ],
        },
        "systemName": "Python USDM3 Package",
        "systemVersion": __package_version__,
        "usdmVersion": "3.0.0",
    }
