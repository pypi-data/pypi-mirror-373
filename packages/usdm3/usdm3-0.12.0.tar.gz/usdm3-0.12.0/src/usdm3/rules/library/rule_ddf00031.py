from .rule_template import RuleTemplate


class RuleDDF00031(RuleTemplate):
    """
    DDF00031: If timing type is not \"Fixed Reference\" then it must point to two scheduled instances (e.g. the relativeFromScheduledInstance and relativeToScheduledInstance attributes must not be missing and must not be equal to each other).

    Applies to: Timing
    Attributes: relativeToScheduledInstance
    """

    def __init__(self):
        super().__init__(
            "DDF00031",
            RuleTemplate.ERROR,
            'If timing type is not "Fixed Reference" then it must point to two scheduled instances (e.g. the relativeFromScheduledInstance and relativeToScheduledInstance attributes must not be missing and must not be equal to each other).',
        )

    def validate(self, config: dict) -> bool:
        data = config["data"]
        items = data.instances_by_klass("Timing")
        for item in items:
            check = True
            if item["type"]["decode"] != "Fixed Reference":
                if "relativeToScheduledInstanceId" not in item:
                    self._add_failure(
                        "Missing relativeToScheduledInstanceId",
                        "Timing",
                        "relativeToScheduledInstanceId",
                        data.path_by_id(item["id"]),
                    )
                    check = False
                if "relativeFromScheduledInstanceId" not in item:
                    self._add_failure(
                        "Missing relativeFromScheduledInstanceId",
                        "Timing",
                        "relativeFromScheduledInstanceId",
                        data.path_by_id(item["id"]),
                    )
                    check = False
                if (
                    check
                    and item["relativeToScheduledInstanceId"]
                    == item["relativeFromScheduledInstanceId"]
                ):
                    self._add_failure(
                        "relativeToScheduledInstanceId and relativeFromScheduledInstanceId are equal",
                        "Timing",
                        "relativeToScheduledInstanceId and relativeFromScheduledInstanceId",
                        data.path_by_id(item["id"]),
                    )
        return self._result()
