import pytest

from redactor import redact_names

def test_redact_names():
    # Sample input text
    text = "Chris works at Facebook. Sarah works at Google."
    type_map = {}
    
    # Mocking sorted_ents similar to spaCy entities for testing
    class MockEntity:
        def __init__(self, text, label_):
            self.text = text
            self.label_ = label_

    sorted_ents = [MockEntity("Chris", "PERSON"),MockEntity("Sarah","PERSON")]

    # Expected redacted output
    expected_text = "\u2588\u2588\u2588\u2588\u2588 works at Facebook. \u2588\u2588\u2588\u2588\u2588 works at Google."

    # Run the function
    result_text = redact_names(text, type_map, sorted_ents)

    # Assertions
    assert result_text == expected_text, "Redacted text does not match expected output."