import pytest

from .modifier import ModifierBuilder


@pytest.mark.parametrize(
    ["text", "input_name", "input_number"],
    [("text", "name", 1), (None, None, 1), (None, "name", None)],
)
def test_invalid_arguments(text, input_name, input_number):
    with pytest.raises(ValueError):
        ModifierBuilder(text=text, input_name=input_name, input_number=input_number)


def test_build_with_text():
    builder = ModifierBuilder(text="Hello, World!")
    modifier = builder.build()

    assert modifier({}) == {"content": "Hello, World!"}


def test_with_input():
    builder = ModifierBuilder(input_name="hashtags", input_number=1)
    modifier = builder.build()

    assert modifier({}) == {
        "content": "text",
        "tag": {"name": "nohash", "type": "Hashtag"},
    }


def test_with_input_zero_value():
    builder = ModifierBuilder(input_name="hashtags", input_number=0)
    modifier = builder.build()

    assert modifier({}) == {
        "content": "text",
        "tag": {"name": "#test", "type": "Hashtag"},
    }
