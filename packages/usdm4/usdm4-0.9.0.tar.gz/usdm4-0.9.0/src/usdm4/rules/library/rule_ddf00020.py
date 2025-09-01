from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00020(RuleTemplate):
    """
    DDF00020: If the reason for a study amendment is 'Other' then this must be specified (attribute reasonOther must be completed)

    Applies to: StudyAmendmentReason
    Attributes: code, otherReason
    """

    def __init__(self):
        super().__init__(
            "DDF00020",
            RuleTemplate.ERROR,
            "If the reason for a study amendment is 'Other' then this must be specified (attribute reasonOther must be completed)",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
