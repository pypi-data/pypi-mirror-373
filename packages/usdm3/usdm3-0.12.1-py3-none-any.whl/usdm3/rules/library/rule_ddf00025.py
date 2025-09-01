from .rule_template import RuleTemplate


class RuleDDF00025(RuleTemplate):
    """
    DDF00025: A window must not be defined for an anchor timing (i.e., type is \"Fixed Reference\").

    Applies to: Timing
    Attributes: windowLabel, windowLower, windowUpper
    """

    def __init__(self):
        super().__init__(
            "DDF00025",
            RuleTemplate.ERROR,
            'A window must not be defined for an anchor timing (i.e., type is "Fixed Reference").',
        )

    def validate(self, config: dict) -> bool:
        data = config["data"]
        items = data.instances_by_klass("Timing")
        for item in items:
            if item["type"]["decode"] == "Fixed Reference":
                if "windowLower" in item:
                    if item["windowLower"] is not None:
                        self._add_failure(
                            "Window lower defined for anchor timing",
                            "Timing",
                            "windowLower",
                            data.path_by_id(item["id"]),
                        )
                if "windowUpper" in item:
                    if item["windowUpper"] is not None:
                        self._add_failure(
                            "Window upper defined for anchor timing",
                            "Timing",
                            "windowUpper",
                            data.path_by_id(item["id"]),
                        )
        return self._result()
