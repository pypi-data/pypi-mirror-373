from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00107(RuleTemplate):
    """
    DDF00107: A scheduled activity instance must only have a sub-timeline that is defined within the same study design as the scheduled activity instance.

    Applies to: ScheduledActivityInstance
    Attributes: timeline
    """

    def __init__(self):
        super().__init__(
            "DDF00107",
            RuleTemplate.ERROR,
            "A scheduled activity instance must only have a sub-timeline that is defined within the same study design as the scheduled activity instance.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
