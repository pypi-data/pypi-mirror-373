from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00062(RuleTemplate):
    """
    DDF00062: When specified, the upper limit of a timing window must be a non-negative duration in ISO 8601 format.

    Applies to: Timing
    Attributes: windowUpper
    """

    def __init__(self):
        super().__init__(
            "DDF00062",
            RuleTemplate.ERROR,
            "When specified, the upper limit of a timing window must be a non-negative duration in ISO 8601 format.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
