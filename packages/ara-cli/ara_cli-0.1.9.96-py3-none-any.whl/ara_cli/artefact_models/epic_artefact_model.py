from ara_cli.artefact_models.artefact_model import Artefact, ArtefactType, Intent
from pydantic import Field, field_validator
from typing import List, Tuple, Optional


class EpicIntent(Intent):
    in_order_to: str = Field(
        description="Motivation or benefit the user aims to achieve. This should specify the ultimate goal or the key benefit the user is seeking, like improving efficiency, saving time, or enhancing productivity."
    )
    as_a: str = Field(
        description="User role or persona description. Specify the type of user or persona that interacts with the product, such as a developer, administrator, or end-user."
    )
    i_want: str = Field(
        description="Desired product feature or behavior. Detail the specific action or functionality the user wishes the product to perform, addressing their need or problem directly."
    )

    @field_validator('in_order_to')
    def validate_in_order_to(cls, v):
        if not v:
            # TODO: what is in_order_to?
            raise ValueError("in_order_to must be set for EpicIntent")
        return v

    @field_validator('as_a')
    def validate_as_a(cls, v):
        if not v:
            raise ValueError("as_a must be set for EpicIntent")
        return v

    @field_validator('i_want')
    def validate_i_want(cls, v):
        if not v:
            raise ValueError("i_want must be set for EpicIntent")
        return v

    def serialize(self):
        from ara_cli.artefact_models.serialize_helper import as_a_serializer

        lines = []

        as_a_line = as_a_serializer(self.as_a)

        lines.append(f"In order to {self.in_order_to}")
        lines.append(as_a_line)
        lines.append(f"I want {self.i_want}")

        return "\n".join(lines)

    @classmethod
    def deserialize_from_lines(cls, lines: List[str], start_index: int = 0) -> 'EpicIntent':
        prefixes = [
            ("In order to ", "in_order_to"),
            ("As a ", "as_a"),
            ("As an ", "as_a"),
            ("I want ", "i_want"),
        ]

        found = {"in_order_to": None, "as_a": None, "i_want": None}

        def match_and_store(line):
            for prefix, field in prefixes:
                if line.startswith(prefix) and found[field] is None:
                    found[field] = line[len(prefix):].strip()
                    return True
            return False

        index = start_index
        while index < len(lines) and any(v is None for v in found.values()):
            match_and_store(lines[index])
            index += 1

        if not found["in_order_to"]:
            raise ValueError("Could not find 'In order to' line")
        if not found["as_a"]:
            raise ValueError("Could not find 'As a' line")
        if not found["i_want"]:
            raise ValueError("Could not find 'I want' line")

        return cls(
            in_order_to=found["in_order_to"],
            as_a=found["as_a"],
            i_want=found["i_want"]
        )


class EpicArtefact(Artefact):
    artefact_type: ArtefactType = ArtefactType.epic
    intent: EpicIntent
    rules: Optional[List[str]] = Field(
        default=None,
        description="Rules the epic defines. It is recommended to create rules to clarify the desired outcome"
    )

    @field_validator('artefact_type')
    def validate_artefact_type(cls, v):
        if v != ArtefactType.epic:
            raise ValueError(
                f"EpicArtefact must have artefact_type of '{ArtefactType.epic}', not '{v}'")
        return v

    @field_validator('rules')
    def allow_empty_rules(cls, v):  # pragma: no cover
        return v

    @classmethod
    def _title_prefix(cls) -> str:
        return "Epic:"

    @classmethod
    def _artefact_type(cls) -> ArtefactType:
        return ArtefactType.epic

    @classmethod
    def _deserialize_rules(cls, lines) -> Tuple[List[str], List[str]]:
        rules = []
        remaining_lines = []
        rule_line_start = "Rule: "
        for line in lines:
            if line.startswith(rule_line_start):
                rules.append(line[len(rule_line_start):])
                continue
            remaining_lines.append(line)
        return rules, remaining_lines

    @classmethod
    def deserialize(cls, text: str) -> 'EpicArtefact':
        fields = super()._parse_common_fields(text)

        intent = EpicIntent.deserialize(text)

        lines = [line.strip()
                 for line in text.strip().splitlines() if line.strip()]
        rules, lines = cls._deserialize_rules(lines)

        # Add the intent to the fields dictionary
        fields['intent'] = intent
        fields['rules'] = rules

        # Create and return the BusinessgoalArtefact instance
        return cls(**fields)

    def _serialize_rules(self) -> str:
        if not self.rules:
            return None
        rules = [f"Rule: {rule}" for rule in self.rules]
        return '\n'.join(rules)

    def serialize(self) -> str:
        tags = self._serialize_tags()
        title = self._serialize_title()
        contribution = self._serialize_contribution()
        description = self._serialize_description()
        rules = self._serialize_rules()
        intent = self.intent.serialize()
        lines = []
        if tags:
            lines.append(tags)
        lines.append(title)
        lines.append("")
        lines.append(contribution)
        lines.append("")
        lines.append(intent)
        lines.append("")
        if rules:
            lines.append(rules)
            lines.append("")
        lines.append(description)
        lines.append("")
        return "\n".join(lines)
