from pydantic import Field, BaseModel, field_validator
from typing import Optional, List, Literal, Tuple
from ara_cli.artefact_models.artefact_model import Artefact, ArtefactType
import re


class ActionItem(BaseModel):
    model_config = {
        "validate_assignment": True
    }

    status: Literal["to-do", "in-progress", "done"] = Field(
        default="to-do",
        description="work status of the action item. Can be 'to-do', 'in-progress' or 'done'"
    )
    text: str = Field(
        ...,
        description="action item text describing the action required"
    )

    @field_validator('status', mode='before')
    def validate_status(cls, v):
        if not v:
            raise ValueError("status must be set in ActionItem. May be one of 'to-do', 'in-progress' or 'done'")
        if v not in ["to-do", "in-progress", "done"]:
            raise ValueError(f"invalid status '{v}'. Allowed values are 'to-do', 'in-progress', 'done'")
        return v

    @field_validator('text', mode='before')
    def validate_text(cls, v):
        if not v:
            raise ValueError("text must be set in ActionItem. Should describe what action is required for the task to be accomplished")
        return v

    @classmethod
    def deserialize(cls, text: str) -> Optional['ActionItem']:
        if not text:
            return None
        
        lines = text.strip().split('\n')
        first_line = lines[0]
        
        match = re.match(r'\[@(.*?)\]\s+(.*)', first_line)
        if not match:
            return None

        status, first_line_text = match.groups()
        
        # Validate the status before creating the ActionItem
        if status not in ["to-do", "in-progress", "done"]:
            raise ValueError(f"invalid status '{status}' in action item. Allowed values are 'to-do', 'in-progress', 'done'")

        # If there are multiple lines, join them
        if len(lines) > 1:
            all_text = '\n'.join([first_line_text] + lines[1:])
        else:
            all_text = first_line_text

        return cls(status=status, text=all_text)

    def serialize(self) -> str:
        lines = self.text.split('\n')
        # First line includes the status marker
        first_line = f"[@{self.status}] {lines[0]}"
        if len(lines) == 1:
            return first_line
        
        # Additional lines follow without status marker
        result_lines = [first_line] + lines[1:]
        return '\n'.join(result_lines)


class TaskArtefact(Artefact):
    artefact_type: ArtefactType = ArtefactType.task
    action_items: List[ActionItem] = Field(default_factory=list)

    @classmethod
    def _is_action_item_start(cls, line: str) -> bool:
        return line.startswith('[@')

    @classmethod
    def _is_section_start(cls, line: str, description_marker: str, contribution_marker: str) -> bool:
        return (
            line.startswith(description_marker) or
            line.startswith(contribution_marker)
        )

    @classmethod
    def _collect_action_item_lines(cls, lines, start_idx, description_marker, contribution_marker):
        action_item_lines = [lines[start_idx]]
        j = start_idx + 1
        while j < len(lines):
            next_line = lines[j]
            if (
                cls._is_action_item_start(next_line) or 
                cls._is_section_start(next_line, description_marker, contribution_marker)
            ):
                break
            action_item_lines.append(next_line)
            j += 1
        return action_item_lines, j

    @classmethod
    def _deserialize_action_items(cls, text) -> Tuple[List[ActionItem], List[str]]:
        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
        action_items = []
        remaining_lines = []
        i = 0
        contribution_marker = cls._contribution_starts_with()
        description_marker = cls._description_starts_with()

        while i < len(lines):
            line = lines[i]
            if cls._is_action_item_start(line):
                action_item_lines, next_idx = cls._collect_action_item_lines(
                    lines, i, description_marker, contribution_marker
                )
                action_item_text = '\n'.join(action_item_lines)
                try:
                    action_item = ActionItem.deserialize(action_item_text)
                    if action_item:
                        action_items.append(action_item)
                except ValueError as e:
                    raise ValueError(f"Error parsing action item: {e}")
                i = next_idx
            else:
                remaining_lines.append(line)
                i += 1

        return action_items, remaining_lines

    @classmethod
    def deserialize(cls, text: str) -> 'TaskArtefact':
        fields = super()._parse_common_fields(text)

        action_items, lines = cls._deserialize_action_items(text)

        fields['action_items'] = action_items

        return cls(**fields)

    @classmethod
    def _title_prefix(cls) -> str:
        return "Task:"

    @classmethod
    def _artefact_type(cls) -> ArtefactType:
        return ArtefactType.task

    def _serialize_action_items(self) -> str:
        action_item_lines = []
        for action_item in self.action_items:
            action_item_lines.append(action_item.serialize())
        return "\n".join(action_item_lines)

    def serialize(self) -> str:
        tags = self._serialize_tags()
        title = self._serialize_title()
        contribution = self._serialize_contribution()
        description = self._serialize_description()
        action_items = self._serialize_action_items()

        lines = []
        if tags:
            lines.append(tags)
        lines.append(title)
        lines.append("")
        if contribution:
            lines.append(contribution)
            lines.append("")
        if action_items:
            lines.append(action_items)
            lines.append("")
        lines.append(description)
        lines.append("")

        return "\n".join(lines)