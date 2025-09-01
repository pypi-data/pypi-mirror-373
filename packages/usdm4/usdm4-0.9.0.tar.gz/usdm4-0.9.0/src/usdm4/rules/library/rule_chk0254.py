from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0254(RuleTemplate):
    """
    CHK0254: An administrable product's product designation must be specified using the product designation (C207418) DDF codelist.

    Applies to: StudyIntervention
    Attributes: productDesignation
    """

    def __init__(self):
        super().__init__(
            "CHK0254",
            RuleTemplate.ERROR,
            "An administrable product's product designation must be specified using the product designation (C207418) DDF codelist.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
