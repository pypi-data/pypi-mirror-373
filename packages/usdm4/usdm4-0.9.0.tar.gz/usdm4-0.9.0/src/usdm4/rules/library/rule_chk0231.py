from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0231(RuleTemplate):
    """
    CHK0231: Narrative content item text is expected to be HTML formatted.

    Applies to: NarrativeContentItem
    Attributes: text
    """

    def __init__(self):
        super().__init__(
            "CHK0231",
            RuleTemplate.ERROR,
            "Narrative content item text is expected to be HTML formatted.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
