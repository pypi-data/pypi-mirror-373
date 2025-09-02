from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00051(RuleTemplate):
    """
    DDF00051: A timing's type must be specified using the Timing Type Value Set Terminology (C201264) DDF codelist.

    Applies to: Timing
    Attributes: type
    """

    def __init__(self):
        super().__init__(
            "DDF00051",
            RuleTemplate.ERROR,
            "A timing's type must be specified using the Timing Type Value Set Terminology (C201264) DDF codelist.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
