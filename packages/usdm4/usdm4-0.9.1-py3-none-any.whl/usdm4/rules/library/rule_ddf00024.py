from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00024(RuleTemplate):
    """
    DDF00024: An epoch must only reference epochs that are specified within the same study design.

    Applies to: StudyEpoch
    Attributes: previous, next
    """

    def __init__(self):
        super().__init__(
            "DDF00024",
            RuleTemplate.ERROR,
            "An epoch must only reference epochs that are specified within the same study design.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
