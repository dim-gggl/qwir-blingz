"""Conversation scaffolding for the planet builder chatbot."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional


class InputType(str, Enum):
    CHOICE = "choice"
    MULTI_CHOICE = "multi_choice"
    FREE_TEXT = "free_text"
    COLOR = "color"
    NUMBER = "number"
    BOOLEAN = "boolean"


@dataclass(frozen=True)
class BuilderStep:
    """Metadata describing a conversation step."""

    id: str
    title: str
    prompt: str
    input_type: InputType
    field_mapping: Dict[str, str]
    optional: bool = False
    suggestions: List[str] = field(default_factory=list)
    dependencies: Dict[str, Any] = field(default_factory=dict)
    validation: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlanetBuilderState:
    """Mutable session state while guiding a member through the builder."""

    planet_id: int
    step_index: int = 0
    attributes: Dict[str, Any] = field(default_factory=dict)
    skipped_steps: List[str] = field(default_factory=list)
    confirmations: Dict[str, bool] = field(default_factory=dict)

    def current_step(self) -> BuilderStep:
        return PLANET_BUILDER_STEPS[self.step_index]

    def advance(self) -> None:
        if self.step_index < len(PLANET_BUILDER_STEPS) - 1:
            self.step_index += 1

    def retreat(self) -> None:
        if self.step_index > 0:
            self.step_index -= 1

    def goto(self, step_id: str) -> None:
        for idx, step in enumerate(PLANET_BUILDER_STEPS):
            if step.id == step_id:
                self.step_index = idx
                return
        raise ValueError(f"Unknown builder step: {step_id}")

    def set_values(self, **values: Any) -> None:
        self.attributes.update(values)

    def mark_skipped(self, step_id: Optional[str] = None) -> None:
        sid = step_id or self.current_step().id
        if sid not in self.skipped_steps:
            self.skipped_steps.append(sid)

    def mark_confirmed(self, step_id: Optional[str] = None) -> None:
        sid = step_id or self.current_step().id
        self.confirmations[sid] = True


PLANET_BUILDER_STEPS: List[BuilderStep] = [
    BuilderStep(
        id="intro",
        title="Planet identity",
        prompt="Hi luminous soul! Let's name your planet and set its greeting. What name, tagline, or motto feels right?",
        input_type=InputType.FREE_TEXT,
        field_mapping={
            "name": "name",
            "tagline": "tagline",
            "motto": "motto",
        },
    ),
    BuilderStep(
        id="tone",
        title="Tone & emotion",
        prompt="How should your planet feel to those who visit? Pick a tone or describe your own vibe.",
        input_type=InputType.CHOICE,
        suggestions=[
            "sanctuary",
            "rebellious",
            "jubilant",
            "reflective",
            "fiery",
            "tender",
            "enigmatic",
            "custom",
        ],
        field_mapping={
            "emotional_tone": "emotional_tone",
            "emotional_custom_label": "emotional_custom_label",
        },
    ),
    BuilderStep(
        id="palette",
        title="Color palette",
        prompt="Let's paint the planet. Share a primary color (HEX like #FF69B4) and any accents that belong in the orbit.",
        input_type=InputType.COLOR,
        field_mapping={
            "primary_color": "primary_color",
            "secondary_color": "secondary_color",
            "palette": "palette",
        },
        validation={"hex": True},
    ),
    BuilderStep(
        id="surface",
        title="Surface & textures",
        prompt="What is the surface like? Choose a base type and add descriptors (e.g., glossy, mossy, embroidered).",
        input_type=InputType.MULTI_CHOICE,
        suggestions=[
            "gas",
            "rocky",
            "oceanic",
            "metallic",
            "organic",
            "crystalline",
            "hybrid",
        ],
        field_mapping={
            "surface_type": "surface_type",
            "surface_descriptors": "surface_descriptors",
        },
    ),
    BuilderStep(
        id="rings",
        title="Rings & satellites",
        prompt="Does your planet flaunt rings or moons? Tell me about their shapes, colors, and numbers.",
        input_type=InputType.FREE_TEXT,
        field_mapping={
            "ring_style": "ring_style",
            "ring_descriptors": "ring_descriptors",
            "ring_color": "ring_color",
            "has_moons": "has_moons",
            "moon_count": "moon_count",
            "moon_descriptors": "moon_descriptors",
        },
    ),
    BuilderStep(
        id="atmosphere",
        title="Atmosphere",
        prompt="Look up! What's happening in the sky? Auroras, storms, vaporwave glows?",
        input_type=InputType.MULTI_CHOICE,
        suggestions=[
            "aurora",
            "nebula",
            "stormy",
            "calm",
            "glowing",
            "vaporwave",
            "none",
        ],
        field_mapping={
            "atmosphere_style": "atmosphere_style",
            "atmosphere_descriptors": "atmosphere_descriptors",
        },
    ),
    BuilderStep(
        id="origin",
        title="Origin & materials",
        prompt="What's the story of this planet's birth? Natural, hand-crafted, ritual forged? Any materials woven in?",
        input_type=InputType.FREE_TEXT,
        field_mapping={
            "origin_type": "origin_type",
            "materials": "materials",
        },
    ),
    BuilderStep(
        id="accessibility",
        title="Accessibility & sensory cues",
        prompt="Describe how to experience this planet. What should visitors know, hear, smell, or feel when they arrive?",
        input_type=InputType.FREE_TEXT,
        field_mapping={
            "accessibility_notes": "accessibility_notes",
        },
    ),
    BuilderStep(
        id="safety",
        title="Safety shields",
        prompt="Let’s set boundaries. Are there topics you’d like to flag or keep from resurfacing here?",
        input_type=InputType.MULTI_CHOICE,
        field_mapping={
            "trigger_avoidance_tags": "trigger_avoidance_tags",
            "custom_trigger_warnings": "custom_trigger_warnings",
        },
        optional=True,
    ),
    BuilderStep(
        id="summary",
        title="Review & launch",
        prompt="Ready to launch? I’ll recap everything. Say yes to send it to the art engines or tweak anything you like.",
        input_type=InputType.CHOICE,
        suggestions=["approve", "edit", "randomize", "restart"],
        field_mapping={},
    ),
]


def iter_builder_steps() -> Iterable[BuilderStep]:
    """Convenience iterator for external consumers."""

    return iter(PLANET_BUILDER_STEPS)
