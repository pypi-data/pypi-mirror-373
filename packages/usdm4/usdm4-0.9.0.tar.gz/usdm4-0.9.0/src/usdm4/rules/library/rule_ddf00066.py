from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00066(RuleTemplate):
    """
    DDF00066: A scheduled decision instance is expected to refer to a default condition.

    Applies to: ScheduledDecisionInstance
    Attributes: defaultCondition
    """

    def __init__(self):
        super().__init__(
            "DDF00066",
            RuleTemplate.ERROR,
            "A scheduled decision instance is expected to refer to a default condition.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
