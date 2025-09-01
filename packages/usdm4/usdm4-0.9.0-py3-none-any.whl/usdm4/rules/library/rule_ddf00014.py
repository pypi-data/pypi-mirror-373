from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00014(RuleTemplate):
    """
    DDF00014: A biomedical concept category is expected to have at least a member or a child.

    Applies to: BiomedicalConceptCategory
    Attributes: members, children
    """

    def __init__(self):
        super().__init__(
            "DDF00014",
            RuleTemplate.ERROR,
            "A biomedical concept category is expected to have at least a member or a child.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
