from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00044(RuleTemplate):
    """
    DDF00044: The target for a condition must not be equal to its parent.

    Applies to: ConditionAssignment
    Attributes: conditionTarget
    """

    def __init__(self):
        super().__init__(
            "DDF00044",
            RuleTemplate.ERROR,
            "The target for a condition must not be equal to its parent.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
