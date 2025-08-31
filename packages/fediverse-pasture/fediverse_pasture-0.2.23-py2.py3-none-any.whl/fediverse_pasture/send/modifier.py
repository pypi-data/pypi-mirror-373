from dataclasses import dataclass

from fediverse_pasture.types import MessageModifier


def get_inputs_value(input_name: str, input_number: int) -> dict:
    try:
        import fediverse_pasture_inputs
    except ImportError:
        raise ImportError(
            "The 'fediverse_pasture_inputs' package is required to use input modifiers."
        )
    inputs = fediverse_pasture_inputs.available[input_name]

    return inputs.examples[input_number]


@dataclass
class ModifierBuilder:
    text: str | None = None
    input_name: str | None = None
    input_number: int | None = None

    def __post_init__(self):
        if (self.input_name and self.input_number is None) or (
            not self.input_name and self.input_number
        ):
            raise ValueError(
                "Both input_name and input_number must be specified together."
            )

        if self.text and self.input_name and self.input_number:
            raise ValueError(
                "Cannot specify text, input_name, and input_number at the same time."
            )

    def build(self) -> MessageModifier:
        if self.text:
            return lambda x: {**x, "content": self.text}

        if self.input_name and self.input_number is not None:
            info = get_inputs_value(self.input_name, self.input_number)

            return lambda x: {**x, "content": "text", **info}

        return lambda x: {
            **x,
            "content": "text",
        }
