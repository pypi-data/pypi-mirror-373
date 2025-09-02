from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0183(RuleTemplate):
    """
    CHK0183: If a section number is to be displayed then a number must be specified and vice versa.

    Applies to: NarrativeContent
    Attributes: sectionNumber, displaySectionNumber
    """

    def __init__(self):
        super().__init__(
            "CHK0183",
            RuleTemplate.ERROR,
            "If a section number is to be displayed then a number must be specified and vice versa.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
