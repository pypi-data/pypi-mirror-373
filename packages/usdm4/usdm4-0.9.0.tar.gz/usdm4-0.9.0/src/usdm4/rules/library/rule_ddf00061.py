from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00061(RuleTemplate):
    """
    DDF00061: When specified, the lower limit of a timing window must be a non-negative duration in ISO 8601 format.

    Applies to: Timing
    Attributes: windowLower
    """

    def __init__(self):
        super().__init__(
            "DDF00061",
            RuleTemplate.ERROR,
            "When specified, the lower limit of a timing window must be a non-negative duration in ISO 8601 format.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
