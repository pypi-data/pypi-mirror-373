from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00018(RuleTemplate):
    """
    DDF00018: An instance of a class must not reference itself as one of its own children.

    Applies to: BiomedicalConceptCategory, StudyProtocolDocumentVersion, StudyDefinitionDocumentVersion, NarrativeContent, Activity
    Attributes: children
    """

    def __init__(self):
        super().__init__(
            "DDF00018",
            RuleTemplate.ERROR,
            "An instance of a class must not reference itself as one of its own children.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
