from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0257(RuleTemplate):
    """
    CHK0257: If the intervention model indicates a single group design then only one intervention is expected. In all other cases more interventions are expected.

    Applies to: InterventionalStudyDesign
    Attributes: model
    """

    def __init__(self):
        super().__init__(
            "CHK0257",
            RuleTemplate.ERROR,
            "If the intervention model indicates a single group design then only one intervention is expected. In all other cases more interventions are expected.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
