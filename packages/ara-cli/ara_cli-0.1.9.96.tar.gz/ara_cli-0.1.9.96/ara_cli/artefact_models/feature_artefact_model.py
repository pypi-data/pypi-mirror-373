from pydantic import BaseModel, field_validator, model_validator, Field
from typing import List, Dict, Tuple, Union, Optional
from ara_cli.artefact_models.artefact_model import Artefact, ArtefactType, Intent
import re


class FeatureIntent(Intent):
    as_a: str = Field(
        description="Role or identity of the user. Specify who is interacting with the product or feature—for example, a project manager, or a student."
    )
    i_want_to: str = Field(
        description="Specific action or need of the user. Outline what the user is looking to accomplish or the problem they are trying to solve. What task or goal motivates their interaction with the product?"
    )
    so_that: str = Field(
        description="The desired outcome or benefit the user wishes to attain. What is the ultimate result they are hoping to achieve by using the product or feature? This should highlight the end benefit or solution provided."
    )

    @field_validator('as_a')
    def validate_in_order_to(cls, v):
        if not v:
            raise ValueError("as_a must be set for FeatureIntent")
        return v

    @field_validator('i_want_to')
    def validate_as_a(cls, v):
        if not v:
            raise ValueError("i_want_to must be set for FeatureIntent")
        return v

    @field_validator('so_that')
    def validate_i_want(cls, v):
        if not v:
            raise ValueError("so_that must be set for FeatureIntent")
        return v

    def serialize(self):
        from ara_cli.artefact_models.serialize_helper import as_a_serializer

        lines = []

        as_a_line = as_a_serializer(self.as_a)

        lines.append(as_a_line)
        lines.append(f"I want to {self.i_want_to}")
        lines.append(f"So that {self.so_that}")

        return "\n".join(lines)

    @classmethod
    def deserialize_from_lines(cls, lines: List[str], start_index: int = 0) -> 'FeatureIntent':
        prefixes = [
            ("As a ", "as_a"),
            ("As an ", "as_a"),
            ("I want to ", "i_want_to"),
            ("So that ", "so_that"),
        ]
        found = {"as_a": None, "i_want_to": None, "so_that": None}

        def match_and_store(line):
            for prefix, field in prefixes:
                if line.startswith(prefix) and found[field] is None:
                    found[field] = line[len(prefix):].strip()
                    return

        index = start_index
        while index < len(lines) and any(v is None for v in found.values()):
            match_and_store(lines[index].strip())
            index += 1

        if not found["as_a"]:
            raise ValueError("Could not find 'As a' line")
        if not found["i_want_to"]:
            raise ValueError("Could not find 'I want to' line")
        if not found["so_that"]:
            raise ValueError("Could not find 'So that' line")

        return cls(
            as_a=found["as_a"],
            i_want_to=found["i_want_to"],
            so_that=found["so_that"]
        )


class Example(BaseModel):
    values: Dict[str, str] = Field(
        description="A set of placeholder names and their values from the example row, used to fill in the scenario outline’s steps."
    )

    @classmethod
    def from_row(cls, headers: List[str], row: List[str]) -> 'Example':
        if len(row) != len(headers):
            raise ValueError(
                f"Row has {len(row)} cells, but expected {len(headers)}.\nFound row: {row}")
        values = {header: value.strip() for header, value in zip(headers, row)}
        return cls(values=values)


class Background(BaseModel):
    steps: List[str] = Field(
        description="A list of Gherkin 'Given' type steps that describe what the background does."
    )

    @field_validator('steps', mode='before')
    def validate_steps(cls, v: List[str]) -> List[str]:
        """Ensure steps are non-empty and stripped."""
        steps = [step.strip() for step in v if step.strip()]
        if not steps:
            raise ValueError("steps list must not be empty")
        return steps

    @classmethod
    def from_lines(cls, lines: List[str], start_idx: int) -> Tuple['Background', int]:
        """Parse a Background from a list of lines starting at start_idx."""
        if not lines[start_idx].startswith('Background:'):
            raise ValueError("Expected 'Background:' at start index")

        steps = []
        idx = start_idx + 1
        while idx < len(lines) and not lines[idx].startswith('Background:'):
            step = lines[idx].strip()
            if step:
                steps.append(step)
            idx += 1
        return cls(steps=steps), idx


class Scenario(BaseModel):
    title: str = Field(
        description="The name of the scenario, giving a short summary of the test case. It comes from the 'Scenario:' line in the feature file."
    )
    steps: List[str] = Field(
        description="A list of Gherkin steps (like 'Given', 'When', 'Then') that describe what the scenario does."
    )

    @field_validator('title')
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        v = v.replace('_', ' ')
        if not v:
            raise ValueError("title must not be empty")
        return v

    @field_validator('steps', mode='before')
    def validate_steps(cls, v: List[str]) -> List[str]:
        """Ensure steps are non-empty and stripped."""
        steps = [step.strip() for step in v if step.strip()]
        if not steps:
            raise ValueError("steps list must not be empty")
        return steps

    @model_validator(mode='after')
    def check_no_placeholders(cls, values: 'Scenario') -> 'Scenario':
        """Ensure regular scenarios don't contain placeholders that should be in scenario outlines."""
        placeholders = set()
        for step in values.steps:
            # Skip validation if step contains docstring placeholders (during parsing)
            if '__DOCSTRING_PLACEHOLDER_' in step:
                continue
            
            # Skip validation if step contains docstring markers (after reinjection)
            if '"""' in step:
                continue
                
            found = re.findall(r'<([^>]+)>', step)
            placeholders.update(found)
        
        if placeholders:
            placeholder_list = ', '.join(f"<{p}>" for p in sorted(placeholders))
            raise ValueError(
                f"Scenario Contains Placeholders ({placeholder_list}) but is not a Scenario Outline. "
                f"Use 'Scenario Outline:' instead of 'Scenario:' and provide an Examples table."
            )
        return values

    @classmethod
    def from_lines(cls, lines: List[str], start_idx: int) -> Tuple['Scenario', int]:
        """Parse a Scenario from a list of lines starting at start_idx."""
        if not lines[start_idx].startswith('Scenario:'):
            raise ValueError("Expected 'Scenario:' at start index")
        title = lines[start_idx][len('Scenario:'):].strip()
        steps = []
        idx = start_idx + 1
        while idx < len(lines) and not (lines[idx].startswith('Scenario:') or lines[idx].startswith('Scenario Outline:')):
            step = lines[idx].strip()
            if step:
                steps.append(step)
            idx += 1
        return cls(title=title, steps=steps), idx


class ScenarioOutline(BaseModel):
    title: str = Field(
        description="The name of the scenario outline, summarizing the test case that uses placeholders. It comes from the 'Scenario Outline:' line in the feature file."
    )
    steps: List[str] = Field(
        description="A list of Gherkin steps with placeholders (like '<name>'), which get filled in by example values."
    )
    examples: List[Example] = Field(
        description="A list of examples that provide values for the placeholders in the steps, sometimes with an optional title for clarity."
    )

    @field_validator('title')
    def validate_title(cls, v: str) -> str:
        if not v:
            raise ValueError("title must not be empty in a ScenarioOutline")
        v = v.replace('_', ' ')
        return v

    @field_validator('steps', mode='before')
    def validate_steps(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("steps list must not be empty in a ScenarioOutline")
        return v

    @field_validator('examples')
    def validate_examples(cls, v: List[Example]) -> List[Example]:
        if not v:
            raise ValueError("examples must not be empty in a ScenarioOutline")
        return v

    @model_validator(mode='after')
    def check_placeholders(cls, values: 'ScenarioOutline') -> 'ScenarioOutline':
        """Ensure all placeholders in steps have corresponding values in examples."""
        placeholders = set()
        for step in values.steps:
            found = re.findall(r'<([^>]+)>', step)
            placeholders.update(found)
        for example in values.examples:
            missing = placeholders - set(example.values.keys())
            if missing:
                raise ValueError(
                    f"Example is missing values for placeholders: {missing}")
        return values

    @classmethod
    def from_lines(cls, lines: List[str], start_idx: int) -> Tuple['ScenarioOutline', int]:
        """Parse a ScenarioOutline from a list of lines starting at start_idx."""

        def extract_title(line: str) -> str:
            if not line.startswith('Scenario Outline:'):
                raise ValueError("Expected 'Scenario Outline:' at start index")
            return line[len('Scenario Outline:'):].strip()

        def extract_steps(lines: List[str], idx: int) -> Tuple[List[str], int]:
            steps = []
            while idx < len(lines) and not lines[idx].strip().startswith('Examples:'):
                if lines[idx].strip():
                    steps.append(lines[idx].strip())
                idx += 1
            return steps, idx

        def extract_headers(line: str) -> List[str]:
            return [h.strip() for h in line.split('|') if h.strip()]

        def extract_row(line: str) -> List[str]:
            return [cell.strip() for cell in line.split('|') if cell.strip()]

        def is_scenario_line(line: str) -> bool:
            return line.startswith("Scenario:") or line.startswith("Scenario Outline:")

        def extract_examples(lines: List[str], idx: int) -> Tuple[List['Example'], int]:
            examples = []

            if idx >= len(lines) or lines[idx].strip() != 'Examples:':
                return examples, idx

            idx += 1
            headers = extract_headers(lines[idx])
            idx += 1

            while idx < len(lines):
                current_line = lines[idx].strip()
                if not current_line or is_scenario_line(current_line):
                    break

                row = extract_row(lines[idx])
                example = Example.from_row(headers, row)
                examples.append(example)
                idx += 1

            return examples, idx

        title = extract_title(lines[start_idx])
        steps, idx = extract_steps(lines, start_idx + 1)
        examples, idx = extract_examples(lines, idx)

        return cls(title=title, steps=steps, examples=examples), idx


class FeatureArtefact(Artefact):
    artefact_type: ArtefactType = ArtefactType.feature
    intent: FeatureIntent
    scenarios: List[Union[Scenario, ScenarioOutline]] = Field(default=None)
    background: Optional[Background] = Field(
        default=None, description="Highly optional background Gherkin steps for Feature Artefacts. This steps apply for all scenarios and scenario outlines in this feature file.")

    @field_validator('artefact_type')
    def validate_artefact_type(cls, v):
        if v != ArtefactType.feature:
            raise ValueError(
                f"FeatureArtefact must have artefact_type of '{ArtefactType.feature}', not '{v}'")
        return v


    @classmethod
    def _title_prefix(cls) -> str:
        return "Feature:"

    @classmethod
    def _artefact_type(cls) -> ArtefactType:
        return ArtefactType.feature

    def _serialize_background(self) -> str:
        """Helper method to dispatch background serialization."""
        if not self.background:
            return ""
        lines = []
        lines.append("  Background:")
        for step in self.background.steps:
            lines.append(f"    {step}")
        return "\n".join(lines)

    def _serialize_scenario(self, scenario: Union[Scenario, ScenarioOutline]) -> str:
        """Helper method to dispatch scenario serialization."""
        if isinstance(scenario, Scenario):
            return self._serialize_regular_scenario(scenario)
        elif isinstance(scenario, ScenarioOutline):
            return self._serialize_scenario_outline(scenario)
        else:   # pragma: no cover
            raise ValueError("Unknown scenario type")

    def _serialize_regular_scenario(self, scenario: Scenario) -> str:
        """Serialize a regular Scenario."""
        lines = []
        lines.append(f"  Scenario: {scenario.title}")
        for step in scenario.steps:
            lines.append(f"    {step}")
        return "\n".join(lines)

    def _serialize_scenario_outline(self, scenario: ScenarioOutline) -> str:
        """Serialize a ScenarioOutline with aligned examples."""
        def serialize_scenario_examples():
            nonlocal lines, scenario
            if not scenario:
                return
            headers = self._extract_placeholders(scenario.steps)

            rows = [headers]

            # Build rows for each example
            for example in scenario.examples:
                row = [str(example.values.get(ph, "")) for ph in headers]
                rows.append(row)

            # Calculate column widths for alignment
            column_widths = [max(len(str(row[i])) for row in rows)
                             for i in range(len(headers))]

            # Format rows with padding
            formatted_rows = []
            for row in rows:
                padded = [str(cell).ljust(width)
                          for cell, width in zip(row, column_widths)]
                formatted_rows.append("| " + " | ".join(padded) + " |")

            lines.append("")
            lines.append("    Examples:")
            for formatted_row in formatted_rows:
                lines.append(f"      {formatted_row}")

        lines = []
        lines.append(f"  Scenario Outline: {scenario.title}")
        for step in scenario.steps:
            lines.append(f"    {step}")

        serialize_scenario_examples()

        return "\n".join(lines)

    def _extract_placeholders(self, steps):
        placeholders = []
        for step in steps:
            found = re.findall(r'<([^>]+)>', step)
            for ph in found:
                if ph not in placeholders:
                    placeholders.append(ph)
        return placeholders

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
        lines.append(intent)
        lines.append("")
        lines.append(contribution)
        lines.append("")
        lines.append(description)
        lines.append("")

        if self.background:
            lines.append(self._serialize_background())
            lines.append("")

        if self.scenarios:
            for scenario in self.scenarios:
                lines.append(self._serialize_scenario(scenario))
                lines.append("")

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, text: str) -> 'FeatureArtefact':
        """
        Deserializes the feature file using a robust extract-and-reinject strategy.
        1. Hides all docstrings by replacing them with placeholders.
        2. Parses the sanitized text using the original, simple parsing logic.
        3. Re-injects the original docstring content back into the parsed objects.
        This prevents the parser from ever being confused by content within docstrings.
        """
        # 1. Hide all docstrings from the entire file text first.
        sanitized_text, docstrings = cls._hide_docstrings(text)

        # 2. Perform the original parsing logic on the SANITIZED text.
        # This part of the code is now "safe" because it will never see a docstring.
        fields = super()._parse_common_fields(sanitized_text)
        intent = FeatureIntent.deserialize(sanitized_text)
        background = cls.deserialize_background(sanitized_text)
        scenarios = cls.deserialize_scenarios(sanitized_text)

        fields['intent'] = intent
        fields['background'] = background
        fields['scenarios'] = scenarios

        # 3. Re-inject the docstrings back into the parsed scenarios.
        if fields['scenarios'] and docstrings:
            for scenario in fields['scenarios']:
                if isinstance(scenario, (Scenario, ScenarioOutline)):
                    scenario.steps = cls._reinject_docstrings_into_steps(scenario.steps, docstrings)

        return cls(**fields)

    @classmethod
    def deserialize_scenarios(cls, text):
        if not text: return []
        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
        scenarios = []
        idx = 0
        while idx < len(lines):
            line = lines[idx]
            if line.startswith('Scenario:'):
                scenario, next_idx = Scenario.from_lines(lines, idx)
                scenarios.append(scenario)
                idx = next_idx
            elif line.startswith('Scenario Outline:'):
                scenario, next_idx = ScenarioOutline.from_lines(lines, idx)
                scenarios.append(scenario)
                idx = next_idx
            else:
                idx += 1
        return scenarios

    @classmethod
    def deserialize_background(cls, text):
        if not text: return None
        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
        background = None
        idx = 0
        while idx < len(lines):
            line = lines[idx]
            if line.startswith('Background:'):
                background, _ = Background.from_lines(lines, idx)
                break
            idx += 1
        return background


    @staticmethod
    def _hide_docstrings(text: str) -> Tuple[str, Dict[str, str]]:
        """
        Finds all docstring blocks ('''...''') in the text,
        replaces them with a unique placeholder, and returns the sanitized
        text and a dictionary mapping placeholders to the original docstrings.
        """
        docstrings = {}
        placeholder_template = "__DOCSTRING_PLACEHOLDER_{}__"

        def replacer(match):
            # This function is called for each found docstring.
            key = placeholder_template.format(len(docstrings))
            docstrings[key] = match.group(0)  # Store the full matched docstring
            return key

        # The regex finds ''' followed by any character (including newlines)
        # in a non-greedy way (.*?) until the next '''.
        sanitized_text = re.sub(r'"""[\s\S]*?"""', replacer, text)

        return sanitized_text, docstrings

    @staticmethod
    def _reinject_docstrings_into_steps(steps: List[str], docstrings: Dict[str, str]) -> List[str]:
        """
        Iterates through a list of steps, finds any placeholders,
        and replaces them with their original docstring content.
        """
        rehydrated_steps = []
        for step in steps:
            for key, value in docstrings.items():
                if key in step:
                    # Replace the placeholder with the original, full docstring block.
                    # This handles cases where the step is just the placeholder,
                    # or the placeholder is at the end of a line (e.g., "Then I see... __PLACEHOLDER__").
                    step = step.replace(key, value)
            rehydrated_steps.append(step)
        return rehydrated_steps
