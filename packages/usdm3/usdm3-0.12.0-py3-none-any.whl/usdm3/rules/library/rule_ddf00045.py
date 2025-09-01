from .rule_template import RuleTemplate


class RuleDDF00045(RuleTemplate):
    def __init__(self):
        super().__init__(
            "DDF00045",
            RuleTemplate.WARNING,
            "At least one attribute must be specified for an address.",
        )

    def validate(self, config: dict):
        data = config["data"]
        addresses = data.instances_by_klass("Address")
        for address in addresses:
            address_valid = False
            for attribute in [
                "text",
                "line",
                "city",
                "district",
                "state",
                "postalCode",
                "country",
            ]:
                if attribute in address and address[attribute]:
                    address_valid = True
            if not address_valid:
                self._add_failure(
                    "No attributes specified for address",
                    "Address",
                    "",
                    data.path_by_id(address["id"]),
                )
        return self._result()
