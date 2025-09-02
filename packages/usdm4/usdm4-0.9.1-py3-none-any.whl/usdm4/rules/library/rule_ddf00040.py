from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00040(RuleTemplate):
    """
    DDF00040: Each study element must be referenced by at least one study cell.

    Applies to: StudyCell
    Attributes: elements
    """

    def __init__(self):
        super().__init__(
            "DDF00040",
            RuleTemplate.ERROR,
            "Each study element must be referenced by at least one study cell.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
