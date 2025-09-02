from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0182(RuleTemplate):
    """
    CHK0182: Narrative content is expected to point to a child and/or to a content item text.

    Applies to: NarrativeContent
    Attributes: children, contentItem
    """

    def __init__(self):
        super().__init__(
            "CHK0182",
            RuleTemplate.ERROR,
            "Narrative content is expected to point to a child and/or to a content item text.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
