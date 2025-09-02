from ara_cli.artefact_models.artefact_model import Artefact, ArtefactType
from pydantic import field_validator


class ExampleArtefact(Artefact):
    artefact_type: ArtefactType = ArtefactType.example

    @field_validator('artefact_type')
    def validate_artefact_type(cls, v):
        if v != ArtefactType.example:
            raise ValueError(
                f"ExampleArtefact must have artefact_type of '{ArtefactType.example}', not '{v}'")
        return v

    @classmethod
    def _title_prefix(cls) -> str:
        return "Example:"

    @classmethod
    def _artefact_type(cls) -> ArtefactType:
        return ArtefactType.example

    @classmethod
    def _contribution_starts_with(cls) -> str:
        return "Illustrates"

    @classmethod
    def deserialize(cls, text: str) -> 'ExampleArtefact':
        fields = super()._parse_common_fields(text)

        return cls(**fields)

    def serialize(self) -> str:
        tags = self._serialize_tags()
        title = self._serialize_title()
        contribution = self._serialize_contribution()
        description = self._serialize_description()

        lines = []
        if tags:
            lines.append(tags)
        lines.append(title)
        lines.append("")
        lines.append(contribution)
        lines.append("")
        lines.append(description)
        lines.append("")

        return "\n".join(lines)
