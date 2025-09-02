from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00093(RuleTemplate):
    """
    DDF00093: Date values associated to a study version must be unique regarding the combination of type and geographic scopes of the date.

    Applies to: StudyVersion
    Attributes: dateValues
    """

    def __init__(self):
        super().__init__(
            "DDF00093",
            RuleTemplate.ERROR,
            "Date values associated to a study version must be unique regarding the combination of type and geographic scopes of the date.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
