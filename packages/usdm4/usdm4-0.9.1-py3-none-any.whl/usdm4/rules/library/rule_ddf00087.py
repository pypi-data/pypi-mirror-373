from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00087(RuleTemplate):
    """
    DDF00087: Encounter ordering using previous and next attributes is expected to be consistent with the order of corresponding scheduled activity instances according to their specified default conditions.

    Applies to: Encounter
    Attributes: previous, next
    """

    def __init__(self):
        super().__init__(
            "DDF00087",
            RuleTemplate.ERROR,
            "Encounter ordering using previous and next attributes is expected to be consistent with the order of corresponding scheduled activity instances according to their specified default conditions.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
