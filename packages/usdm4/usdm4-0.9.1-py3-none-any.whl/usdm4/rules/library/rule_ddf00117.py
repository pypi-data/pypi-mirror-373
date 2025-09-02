from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00117(RuleTemplate):
    """
    DDF00117: A study protocol document version's protocol status must be specified using the Protocol Status Value Set Terminology (C188723) DDF codelist.

    Applies to: StudyProtocolDocumentVersion
    Attributes: protocolStatus
    """

    def __init__(self):
        super().__init__(
            "DDF00117",
            RuleTemplate.ERROR,
            "A study protocol document version's protocol status must be specified using the Protocol Status Value Set Terminology (C188723) DDF codelist.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
