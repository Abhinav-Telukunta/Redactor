import pytest

from redactor import redact_dates

def test_redact_dates():
    # Sample input text
    text = "The event is scheduled for December 9, and a follow-up on March 18."
    type_map = {}
    
    # Mocking sorted_ents similar to spaCy entities for testing
    class MockEntity:
        def __init__(self, text, label_):
            self.text = text
            self.label_ = label_

    sorted_ents = [MockEntity("December 9", "DATE"),MockEntity("March 18","DATE")]

    # Expected redacted output
    expected_text = "The event is scheduled for \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588, and a follow-up on \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588."

    # Run the function
    result_text = redact_dates(text, type_map, sorted_ents)

    # Assertions
    assert result_text == expected_text, "Redacted text does not match expected output."