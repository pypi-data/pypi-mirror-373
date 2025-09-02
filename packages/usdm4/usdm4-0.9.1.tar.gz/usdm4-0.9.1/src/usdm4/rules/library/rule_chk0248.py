from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0248(RuleTemplate):
    """
    CHK0248: Narrative content must only reference narrative content that is specified within the same study definition document version.

    Applies to: NarrativeContent
    Attributes: next, previous, children
    """

    def __init__(self):
        super().__init__(
            "CHK0248",
            RuleTemplate.ERROR,
            "Narrative content must only reference narrative content that is specified within the same study definition document version.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
