from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0167(RuleTemplate):
    """
    CHK0167: A scheduled decision instance must refer to a default condition.

    Applies to: ScheduledDecisionInstance
    Attributes: defaultCondition
    """

    def __init__(self):
        super().__init__(
            "CHK0167",
            RuleTemplate.ERROR,
            "A scheduled decision instance must refer to a default condition.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
