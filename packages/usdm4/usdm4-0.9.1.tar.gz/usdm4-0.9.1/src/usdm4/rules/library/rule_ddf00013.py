from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00013(RuleTemplate):
    """
    DDF00013: If a biomedical concept property is required then it must also be enabled, while if it is not enabled then it must not be required.

    Applies to: BiomedicalConceptProperty
    Attributes: isRequired, isEnabled
    """

    def __init__(self):
        super().__init__(
            "DDF00013",
            RuleTemplate.ERROR,
            "If a biomedical concept property is required then it must also be enabled, while if it is not enabled then it must not be required.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
