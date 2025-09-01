from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00049(RuleTemplate):
    """
    DDF00049: A study arm must only reference populations that are defined within the same study design as the study arm.

    Applies to: StudyArm
    Attributes: populations
    """

    def __init__(self):
        super().__init__(
            "DDF00049",
            RuleTemplate.ERROR,
            "A study arm must only reference populations that are defined within the same study design as the study arm.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
