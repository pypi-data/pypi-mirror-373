from .rule_template import RuleTemplate
from usdm3.data_store.data_store import DataStore


class RuleDDF00011(RuleTemplate):
    def __init__(self):
        super().__init__(
            "DDF00011",
            RuleTemplate.ERROR,
            'Anchor timings (e.g. type is "Fixed Reference") must be related to a scheduled activity instance via a relativeFromScheduledInstance relationship.',
        )

    def validate(self, config: dict) -> bool:
        data: DataStore = config["data"]
        items = data.instances_by_klass("Timing")
        for item in items:
            if item["type"]["decode"] == "Fixed Reference":
                if "relativeFromScheduledInstanceId" not in item:
                    self._add_failure(
                        "Missing relativeFromScheduledInstance",
                        "Timing",
                        "relativeFromScheduledInstanceId",
                        data.path_by_id(item["id"]),
                    )
        return self._result()
