from .rule_template import RuleTemplate


class RuleDDF00036(RuleTemplate):
    """
    DDF00036: If timing type is \"Fixed Reference\" then the corresponding attribute relativeToFrom must be filled with \"Start to Start\".

    Applies to: Timing
    Attributes: relativeToFrom
    """

    def __init__(self):
        super().__init__(
            "DDF00036",
            RuleTemplate.ERROR,
            'If timing type is "Fixed Reference" then the corresponding attribute relativeToFrom must be filled with "Start to Start".',
        )

    def validate(self, config: dict) -> bool:
        data = config["data"]
        items = data.instances_by_klass("Timing")
        for item in items:
            if item["type"]["decode"] == "Fixed Reference":
                if item["relativeToFrom"]["decode"] != "Start to Start":
                    self._add_failure(
                        "Invalid relativeToFrom",
                        "Timing",
                        "relativeToFrom",
                        data.path_by_id(item["id"]),
                    )
        return self._result()
