from ara_cli.artefact_models.artefact_model import Artefact, ArtefactType
from pydantic import field_validator, Field
from typing import Optional


class IssueArtefact(Artefact):
    artefact_type: ArtefactType = ArtefactType.issue
    additional_description: Optional[str] = Field(
        default=None,
        description="Optional block of text before description. Usually describes the issue in gherkin style. To use gherkin style, use separate lines that start with 'Given', 'When', 'Then' to describe the issue."
    )

    @field_validator('artefact_type')
    def validate_artefact_type(cls, v):
        if v != ArtefactType.issue:
            raise ValueError(f"ExampleArtefact must have artefact_type of '{ArtefactType.issue}', not '{v}'")
        return v

    @classmethod
    def _title_prefix(cls) -> str:
        return "Issue:"

    @classmethod
    def _artefact_type(cls) -> ArtefactType:
        return ArtefactType.issue

    @classmethod
    def deserialize(cls, text) -> 'IssueArtefact':
        fields = super()._parse_common_fields(text)

        lines = [line for line in text.strip().splitlines()]

        extract = False
        extracted_text = []

        contribution_beginning = cls._contribution_starts_with()
        description_beginning = cls._description_starts_with()

        for line in lines:
            if line.startswith(contribution_beginning):
                extract = True
                continue
            if line.startswith(description_beginning):
                extract = False
                break
            if extract:
                extracted_text.append(line)

        additional_description = "\n".join(extracted_text).strip()

        fields['additional_description'] = additional_description

        return cls(**fields)

    def _serialize_additional_description(self):
        return self.additional_description

    def serialize(self):
        tags = self._serialize_tags()
        title = self._serialize_title()
        contribution = self._serialize_contribution()
        additional_description = self._serialize_additional_description()
        description = self._serialize_description()

        lines = []
        if tags:
            lines.append(tags)
        lines.append(title)
        lines.append("")
        lines.append(contribution)
        lines.append("")
        if additional_description:
            lines.append(additional_description)
            lines.append("")
        lines.append(description)
        lines.append("")

        return "\n".join(lines)
