from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00065(RuleTemplate):
    """
    DDF00065: A scheduled decision instance is not expected to have a sub-timeline.

    Applies to: ScheduledDecisionInstance
    Attributes: timeline
    """

    def __init__(self):
        super().__init__(
            "DDF00065",
            RuleTemplate.ERROR,
            "A scheduled decision instance is not expected to have a sub-timeline.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
