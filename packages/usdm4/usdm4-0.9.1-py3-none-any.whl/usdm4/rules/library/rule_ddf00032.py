from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00032(RuleTemplate):
    """
    DDF00032: Within a study version, if more than 1 business therapeutic area is defined then they must be distinct.

    Applies to: StudyVersion
    Attributes: businessTherapeuticAreas
    """

    def __init__(self):
        super().__init__(
            "DDF00032",
            RuleTemplate.ERROR,
            "Within a study version, if more than 1 business therapeutic area is defined then they must be distinct.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
