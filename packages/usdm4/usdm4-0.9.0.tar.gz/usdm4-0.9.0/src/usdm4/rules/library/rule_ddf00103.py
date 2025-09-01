from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00103(RuleTemplate):
    """
    DDF00103: Within a document version, the specified section numbers for narrative content must be unique.

    Applies to: NarrativeContent
    Attributes: sectionNumber
    """

    def __init__(self):
        super().__init__(
            "DDF00103",
            RuleTemplate.ERROR,
            "Within a document version, the specified section numbers for narrative content must be unique.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
