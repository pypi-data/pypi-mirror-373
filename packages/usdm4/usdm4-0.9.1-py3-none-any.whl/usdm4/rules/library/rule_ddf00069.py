from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00069(RuleTemplate):
    """
    DDF00069: Each combination of arm and epoch must occur no more than once within a study design.

    Applies to: StudyCell
    Attributes: arm, epoch
    """

    def __init__(self):
        super().__init__(
            "DDF00069",
            RuleTemplate.ERROR,
            "Each combination of arm and epoch must occur no more than once within a study design.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
