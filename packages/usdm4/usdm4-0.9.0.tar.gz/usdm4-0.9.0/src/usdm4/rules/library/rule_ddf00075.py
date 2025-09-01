from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00075(RuleTemplate):
    """
    DDF00075: An activity is expected to refer to at least one procedure, biomedical concept, biomedical concept category or biomedical concept surrogate.

    Applies to: Activity
    Attributes: definedProcedures, biomedicalConcepts, bcCategories, bcSurrogates
    """

    def __init__(self):
        super().__init__(
            "DDF00075",
            RuleTemplate.ERROR,
            "An activity is expected to refer to at least one procedure, biomedical concept, biomedical concept category or biomedical concept surrogate.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
