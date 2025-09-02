from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00023(RuleTemplate):
    """
    DDF00023: To ensure consistent ordering, when both previous and next attributes are available within an entity the previous id value must match the next id value of the referred instance.

    Applies to: Activity, EligibilityCriterion, Encounter, NarrativeContent, StudyEpoch
    Attributes: previous, next
    """

    def __init__(self):
        super().__init__(
            "DDF00023",
            RuleTemplate.ERROR,
            "To ensure consistent ordering, when both previous and next attributes are available within an entity the previous id value must match the next id value of the referred instance.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
