from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00060(RuleTemplate):
    """
    DDF00060: The value for each timing must be a non-negative duration specified in ISO 8601 format.

    Applies to: Timing
    Attributes: value
    """

    def __init__(self):
        super().__init__(
            "DDF00060",
            RuleTemplate.ERROR,
            "The value for each timing must be a non-negative duration specified in ISO 8601 format.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
