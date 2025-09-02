from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00022(RuleTemplate):
    """
    DDF00022: An instance of a class must not refer to itself as its next instance.

    Applies to: StudyEpoch, Encounter, Activity, NarrativeContent, EligibilityCriterion
    Attributes: next
    """

    def __init__(self):
        super().__init__(
            "DDF00022",
            RuleTemplate.ERROR,
            "An instance of a class must not refer to itself as its next instance.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
