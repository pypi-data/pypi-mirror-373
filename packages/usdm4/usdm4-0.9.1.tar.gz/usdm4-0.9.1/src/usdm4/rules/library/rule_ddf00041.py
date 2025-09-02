from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00041(RuleTemplate):
    """
    DDF00041: Within a study design, there must be at least one endpoint with level primary.

    Applies to: Endpoint
    Attributes: level
    """

    def __init__(self):
        super().__init__(
            "DDF00041",
            RuleTemplate.ERROR,
            "Within a study design, there must be at least one endpoint with level primary.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
