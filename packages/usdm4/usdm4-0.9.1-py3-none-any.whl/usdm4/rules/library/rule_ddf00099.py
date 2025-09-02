from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00099(RuleTemplate):
    """
    DDF00099: All epochs are expected to be referred to from a scheduled Activity Instance.

    Applies to: ScheduledActivityInstance
    Attributes: epoch
    """

    def __init__(self):
        super().__init__(
            "DDF00099",
            RuleTemplate.ERROR,
            "All epochs are expected to be referred to from a scheduled Activity Instance.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
