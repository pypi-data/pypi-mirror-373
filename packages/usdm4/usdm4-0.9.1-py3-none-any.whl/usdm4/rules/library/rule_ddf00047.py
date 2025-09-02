from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00047(RuleTemplate):
    """
    DDF00047: A study cell must only reference elements that are defined within the same study design as the study cell.

    Applies to: StudyCell
    Attributes: elements
    """

    def __init__(self):
        super().__init__(
            "DDF00047",
            RuleTemplate.ERROR,
            "A study cell must only reference elements that are defined within the same study design as the study cell.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
