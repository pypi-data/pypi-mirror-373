from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0178(RuleTemplate):
    """
    CHK0178: An activity with children must not refer to a timeline, procedure, biomedical concept, biomedical concept category or biomedical concept surrogate.

    Applies to: Activity
    Attributes: children
    """

    def __init__(self):
        super().__init__(
            "CHK0178",
            RuleTemplate.ERROR,
            "An activity with children must not refer to a timeline, procedure, biomedical concept, biomedical concept category or biomedical concept surrogate.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
