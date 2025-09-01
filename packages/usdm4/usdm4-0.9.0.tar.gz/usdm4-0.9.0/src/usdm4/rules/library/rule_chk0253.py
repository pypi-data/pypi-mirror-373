from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0253(RuleTemplate):
    """
    CHK0253: A medical device sourcing must be specified using the sourcing (Cxxx) DDF codelist.

    Applies to: MedicalDevice
    Attributes: sourcing
    """

    def __init__(self):
        super().__init__(
            "CHK0253",
            RuleTemplate.ERROR,
            "A medical device sourcing must be specified using the sourcing (Cxxx) DDF codelist.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
