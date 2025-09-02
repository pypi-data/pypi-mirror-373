from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00037(RuleTemplate):
    """
    DDF00037: At least one scheduled activity instance within a timeline must point to a timeline exit.

    Applies to: ScheduledActivityInstance
    Attributes: timelineExit
    """

    def __init__(self):
        super().__init__(
            "DDF00037",
            RuleTemplate.ERROR,
            "At least one scheduled activity instance within a timeline must point to a timeline exit.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
