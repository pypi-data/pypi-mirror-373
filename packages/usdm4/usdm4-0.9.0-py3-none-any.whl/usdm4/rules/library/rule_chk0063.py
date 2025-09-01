from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0063(RuleTemplate):
    """
    CHK0063: Each specified procedure is expected to be referenced by an activity.

    Applies to: Activity
    Attributes: definedProcedures
    """

    def __init__(self):
        super().__init__(
            "CHK0063",
            RuleTemplate.ERROR,
            "Each specified procedure is expected to be referenced by an activity.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
