from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0050(RuleTemplate):
    """
    CHK0050: When included in text, references to items stored elsewhere in the data model must be specified in the correct format. They must start with '<usdm:ref', end with either '/>' or '></usdm:ref>', and must contain 'klass=\"klassName\"',  'id=\"idValue\"', and 'attribute=\"attributeName\"/>' in any order (where \"klassName\" and \"attributeName\" contain only letters in upper or lower case).

    Applies to: NarrativeContent
    Attributes: text
    """

    def __init__(self):
        super().__init__(
            "CHK0050",
            RuleTemplate.ERROR,
            "When included in text, references to items stored elsewhere in the data model must be specified in the correct format. They must start with '<usdm:ref', end with either '/>' or '></usdm:ref>', and must contain 'klass=\"klassName\"',  'id=\"idValue\"', and 'attribute=\"attributeName\"/>' in any order (where \"klassName\" and \"attributeName\" contain only letters in upper or lower case).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
