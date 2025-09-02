from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00079(RuleTemplate):
    """
    DDF00079: If a synonym is specified then it is not expected to be equal to the name of the biomedical concept (case insensitive).

    Applies to: BiomedicalConcept
    Attributes: synonyms
    """

    def __init__(self):
        super().__init__(
            "DDF00079",
            RuleTemplate.ERROR,
            "If a synonym is specified then it is not expected to be equal to the name of the biomedical concept (case insensitive).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
