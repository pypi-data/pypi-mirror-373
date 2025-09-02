from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00090(RuleTemplate):
    """
    DDF00090: The same Biomedical Concept Category must not be referenced more than once from the same activity.

    Applies to: Activity
    Attributes: bcCategories
    """

    def __init__(self):
        super().__init__(
            "DDF00090",
            RuleTemplate.ERROR,
            "The same Biomedical Concept Category must not be referenced more than once from the same activity.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
