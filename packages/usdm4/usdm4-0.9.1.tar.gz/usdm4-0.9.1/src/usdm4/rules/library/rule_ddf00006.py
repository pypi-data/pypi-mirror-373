from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00006(RuleTemplate):
    """
    DDF00006: Timing windows must be fully defined, if one of the window attributes (i.e., window label, window lower, and window upper) is defined then all must be specified.

    Applies to: Timing
    Attributes: windowLabel, windowLower, windowUpper
    """

    def __init__(self):
        super().__init__(
            "DDF00006",
            RuleTemplate.ERROR,
            "Timing windows must be fully defined, if one of the window attributes (i.e., window label, window lower, and window upper) is defined then all must be specified.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
