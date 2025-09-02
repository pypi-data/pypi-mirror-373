from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0184(RuleTemplate):
    """
    CHK0184: If a section title is to be displayed then a title must be specified and vice versa.

    Applies to: NarrativeContent
    Attributes: sectionTitle, displaySectionTitle
    """

    def __init__(self):
        super().__init__(
            "CHK0184",
            RuleTemplate.ERROR,
            "If a section title is to be displayed then a title must be specified and vice versa.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
