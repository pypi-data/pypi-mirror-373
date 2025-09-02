from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00076(RuleTemplate):
    """
    DDF00076: If a biomedical concept is referenced from an activity then it is not expected to be referenced as well by a biomedical concept category that is referenced from the same activity.

    Applies to: Activity, BiomedicalConceptCategory
    Attributes: biomedicalConcepts, members
    """

    def __init__(self):
        super().__init__(
            "DDF00076",
            RuleTemplate.ERROR,
            "If a biomedical concept is referenced from an activity then it is not expected to be referenced as well by a biomedical concept category that is referenced from the same activity.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
