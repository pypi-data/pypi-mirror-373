from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00059(RuleTemplate):
    """
    DDF00059: Within a study intervention, if more intervention codes are defined, they must be distinct.

    Applies to: StudyIntervention
    Attributes: codes
    """

    def __init__(self):
        super().__init__(
            "DDF00059",
            RuleTemplate.ERROR,
            "Within a study intervention, if more intervention codes are defined, they must be distinct.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
