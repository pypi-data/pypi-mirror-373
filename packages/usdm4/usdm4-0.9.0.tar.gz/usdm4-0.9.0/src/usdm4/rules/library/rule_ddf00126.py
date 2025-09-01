from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00126(RuleTemplate):
    """
    DDF00126: Cardinalities must be as defined in the USDM schema based on the API specification (i.e., required properties have at least one value and single-value properties are not lists).

    Applies to: All
    Attributes: All
    """

    def __init__(self):
        super().__init__(
            "DDF00126",
            RuleTemplate.ERROR,
            "Cardinalities must be as defined in the USDM schema based on the API specification (i.e., required properties have at least one value and single-value properties are not lists).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
