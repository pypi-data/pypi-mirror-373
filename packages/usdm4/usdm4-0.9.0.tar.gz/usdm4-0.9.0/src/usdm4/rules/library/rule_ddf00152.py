from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00152(RuleTemplate):
    """
    DDF00152: An activity must only reference timelines that are specified within the same study design.

    Applies to: Activity
    Attributes: timeline
    """

    def __init__(self):
        super().__init__(
            "DDF00152",
            RuleTemplate.ERROR,
            "An activity must only reference timelines that are specified within the same study design.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
