from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0240(RuleTemplate):
    """
    CHK0240: There must be a one-to-one relationship between referenced section number and title within a study amendment.

    Applies to: DocumentContentReference
    Attributes: sectionNumber, sectionTitle
    """

    def __init__(self):
        super().__init__(
            "CHK0240",
            RuleTemplate.ERROR,
            "There must be a one-to-one relationship between referenced section number and title within a study amendment.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
