from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0187(RuleTemplate):
    """
    CHK0187: A study definition document version must not be referenced more than once by the same study version.

    Applies to: StudyVersion
    Attributes: documentVersions
    """

    def __init__(self):
        super().__init__(
            "CHK0187",
            RuleTemplate.ERROR,
            "A study definition document version must not be referenced more than once by the same study version.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
