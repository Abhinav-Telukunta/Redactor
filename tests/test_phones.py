import pytest

from redactor import redact_phone_numbers

def test_redact_phones():
    type_map = {}

    sample_text = "Contact us at 123-456-7890 or at +1 352-740-1212 for more information."
    
    # Run the redaction function
    redacted_text = redact_phone_numbers(sample_text, type_map)
    
    # Expected block replacements based on the sample text
    expected_text = "Contact us at " + "\u2588" * 12 + " or at " + "\u2588" * 15 + " for more information."
    
    # Assertions
    assert redacted_text == expected_text  