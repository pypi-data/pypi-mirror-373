from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00026(RuleTemplate):
    """
    DDF00026: A scheduled activity instance must not point (via the \"timeline\" relationship) to the timeline in which it is specified.

    Applies to: ScheduledActivityInstance
    Attributes: timeline
    """

    def __init__(self):
        super().__init__(
            "DDF00026",
            RuleTemplate.ERROR,
            'A scheduled activity instance must not point (via the "timeline" relationship) to the timeline in which it is specified.',
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
