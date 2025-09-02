from ara_cli.artefact_models.artefact_model import Artefact, ArtefactType, Intent
from pydantic import field_validator, Field
from typing import List


class KeyfeatureIntent(Intent):
    in_order_to: str = Field(
        description="Motivation or business objective that this product feature supports. Define the specific goal or outcome you aim to achieve with this feature."
    )
    as_a: str = Field(
        description="Main stakeholder or persona who will benefit from this feature. Identify who this feature is primarily designed for, such as an end user, customer, or a business role."
    )
    i_want: str = Field(
        description="Specific functionality or capability desired. Describe what the user or stakeholder wants the product feature to do, including how it helps achieve their goal."
    )

    @field_validator('in_order_to', mode='before')
    def validate_in_order_to(cls, v):
        if not v:
            raise ValueError("in_order_to must be set for KeyfeatureIntent")
        return v

    @field_validator('as_a', mode='before')
    def validate_as_a(cls, v):
        if not v:
            raise ValueError("as_a must be set for KeyfeatureIntent")
        return v

    @field_validator('i_want', mode='before')
    def validate_i_want(cls, v):
        if not v:
            raise ValueError("i_want must be set for KeyfeatureIntent")
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
    def deserialize_from_lines(cls, lines: List[str], start_index: int = 0) -> 'KeyfeatureIntent':
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
                    return

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


class KeyfeatureArtefact(Artefact):
    artefact_type: ArtefactType = ArtefactType.keyfeature
    intent: KeyfeatureIntent

    @classmethod
    def _title_prefix(cls) -> str:
        return "Keyfeature:"

    @classmethod
    def _artefact_type(cls) -> ArtefactType:
        return ArtefactType.keyfeature

    @classmethod
    def deserialize(cls, text: str) -> 'KeyfeatureArtefact':
        fields = super()._parse_common_fields(text)

        intent = KeyfeatureIntent.deserialize(text)

        fields['intent'] = intent

        return cls(**fields)

    def serialize(self) -> str:
        tags = self._serialize_tags()
        title = self._serialize_title()
        contribution = self._serialize_contribution()
        description = self._serialize_description()
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
        lines.append(description)
        lines.append("")

        return "\n".join(lines)
