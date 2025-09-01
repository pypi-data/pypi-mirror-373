from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0197(RuleTemplate):
    """
    CHK0197: An identified organization is not expected to have more than 1 identifier for the study.

    Applies to: StudyIdentifier
    Attributes: scope
    """

    def __init__(self):
        super().__init__(
            "CHK0197",
            RuleTemplate.ERROR,
            "An identified organization is not expected to have more than 1 identifier for the study.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
