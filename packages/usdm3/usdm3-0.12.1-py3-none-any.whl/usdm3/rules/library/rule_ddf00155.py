from .rule_template import RuleTemplate


class RuleDDF00155(RuleTemplate):
    """
    DDF00155: For CDISC codelist references (where the code system is 'http://www.cdisc.org'), the code system version must be a valid CDISC terminology release date in ISO 8601 date format.

    Applies to: Code
    Attributes: codeSystemVersion
    """

    VERSION_LIST = [
        "2020-03-27",
        "2020-05-08",
        "2020-06-26",
        "2020-09-25",
        "2020-11-06",
        "2020-12-18",
        "2021-03-26",
        "2021-06-25",
        "2021-09-24",
        "2021-12-17",
        "2022-03-25",
        "2022-06-24",
        "2022-09-30",
        "2022-12-16",
        "2023-03-31",
        "2023-06-30",
        "2023-09-29",
        "2023-12-15",
        "2024-03-29",
        "2024-09-27",
        "2025-03-28",
    ]

    def __init__(self):
        super().__init__(
            "DDF00155",
            RuleTemplate.ERROR,
            "For CDISC codelist references (where the code system is 'http://www.cdisc.org'), the code system version must be a valid CDISC terminology release date in ISO 8601 date format.",
        )

    def validate(self, config: dict) -> bool:
        data = config["data"]
        items = data.instances_by_klass("Code")
        for item in items:
            if "codeSystem" in item and item["codeSystem"] == "http://www.cdisc.org":
                if "codeSystemVersion" not in item:
                    self._add_failure(
                        "Missing codeSystemVersion",
                        "Code",
                        "codeSystemVersion",
                        data.path_by_id(item["id"]),
                    )
                else:
                    if item["codeSystemVersion"] not in self.VERSION_LIST:
                        self._add_failure(
                            "Invalid codeSystemVersion",
                            "Code",
                            "codeSystemVersion",
                            data.path_by_id(item["id"]),
                        )
        return self._result()
