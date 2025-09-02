from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00019(RuleTemplate):
    """
    DDF00019: A scheduled activity/decision instance must not refer to itself as its default condition.

    Applies to: ScheduledActivityInstance, ScheduledDecisionInstance
    Attributes: defaultCondition
    """

    def __init__(self):
        super().__init__(
            "DDF00019",
            RuleTemplate.ERROR,
            "A scheduled activity/decision instance must not refer to itself as its default condition.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
