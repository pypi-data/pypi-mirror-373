from ara_cli.artefact_models.artefact_model import Artefact, ArtefactType, Intent
from pydantic import field_validator, Field
from typing import List


class CapabilityIntent(Intent):
    to_be_able_to: str = Field(
        ...,
        description="Expression of the desired capability or action that stakeholders, who are crucial for achieving the business goal, aim to possess or perform. Define what specific skill, access, or knowledge stakeholders need in order to effectively contribute to the success of the product or initiative."
    )

    @field_validator('to_be_able_to')
    def validate_in_order_to(cls, v):
        if not v:
            # TODO: what is to_be_able_to?
            raise ValueError("to_be_able_to must be set for CapabilityIntent")
        return v

    def serialize(self):
        lines = []
        lines.append(f"To be able to {self.to_be_able_to}")

        return "\n".join(lines)

    @classmethod
    def deserialize_from_lines(cls, lines: List[str], start_index: int = 0) -> 'CapabilityIntent':
        to_be_able_to = None

        to_be_able_to_prefix = "To be able to "

        index = start_index
        while index < len(lines) and (not to_be_able_to):
            line = lines[index]
            if line.startswith(to_be_able_to_prefix) and not to_be_able_to:
                to_be_able_to = line[len(to_be_able_to_prefix):].strip()
            index += 1

        if not to_be_able_to:
            raise ValueError("Could not find 'To be able to' line")

        return cls(to_be_able_to=to_be_able_to)


class CapabilityArtefact(Artefact):
    artefact_type: ArtefactType = ArtefactType.capability
    intent: CapabilityIntent

    @field_validator('artefact_type')
    def validate_artefact_type(cls, v):
        if v != ArtefactType.capability:
            raise ValueError(
                f"CapabilityArtefact must have artefact_type of '{ArtefactType.capability}', not '{v}'")
        return v

    @classmethod
    def _title_prefix(cls) -> str:
        return "Capability:"

    @classmethod
    def _artefact_type(cls) -> ArtefactType:
        return ArtefactType.capability

    @classmethod
    def deserialize(cls, text: str) -> 'CapabilityArtefact':
        fields = super()._parse_common_fields(text)

        intent = CapabilityIntent.deserialize(text)

        # Add the intent to the fields dictionary
        fields['intent'] = intent

        # Create and return the BusinessgoalArtefact instance
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
