from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00091(RuleTemplate):
    """
    DDF00091: When a condition applies to a procedure, activity, biomedical concept, biomedical concept category, or biomedical concept surrogate then an instance must be available in the corresponding class with the specified id.

    Applies to: Condition
    Attributes: appliesTo
    """

    def __init__(self):
        super().__init__(
            "DDF00091",
            RuleTemplate.ERROR,
            "When a condition applies to a procedure, activity, biomedical concept, biomedical concept category, or biomedical concept surrogate then an instance must be available in the corresponding class with the specified id.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
