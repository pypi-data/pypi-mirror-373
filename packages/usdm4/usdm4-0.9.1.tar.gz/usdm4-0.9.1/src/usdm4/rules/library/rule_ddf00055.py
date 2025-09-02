from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00055(RuleTemplate):
    """
    DDF00055: Within a study design, if more trial types are defined, they must be distinct.

    Applies to: StudyDesign
    Attributes: trialTypes
    """

    def __init__(self):
        super().__init__(
            "DDF00055",
            RuleTemplate.ERROR,
            "Within a study design, if more trial types are defined, they must be distinct.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
