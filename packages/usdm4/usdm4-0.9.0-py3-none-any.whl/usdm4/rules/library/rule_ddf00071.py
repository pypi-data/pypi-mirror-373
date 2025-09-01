from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00071(RuleTemplate):
    """
    DDF00071: A study cell must only reference an arm that is defined within the same study design as the study cell.

    Applies to: StudyCell
    Attributes: arm
    """

    def __init__(self):
        super().__init__(
            "DDF00071",
            RuleTemplate.ERROR,
            "A study cell must only reference an arm that is defined within the same study design as the study cell.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
