from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00004(RuleTemplate):
    """
    DDF00004: If duration will vary (attribute durationWillVary is True) then a reason (attribute reasonDurationWillVary) must be given and vice versa.

    Applies to: AdministrationDuration
    Attributes: durationWillVary, reasonDurationWillVary
    """

    def __init__(self):
        super().__init__(
            "DDF00004",
            RuleTemplate.ERROR,
            "If duration will vary (attribute durationWillVary is True) then a reason (attribute reasonDurationWillVary) must be given and vice versa.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
