"""PII: phone, SSN, card numbers, and emails must be caught and redacted.

All PII strings below are synthetic test fixtures (555 numbers, a test
card number, example.com addresses), never real personal data.
"""

from finance_data_validation import pii

PHONE = "555-010-1234"
SSN = "123-45-6789"
CARD = "4111 1111 1111 1111"
EMAIL = "analyst@example.com"


def test_detect_phone():
    assert pii.detect(f"call {PHONE} today") == {"phone": 1}


def test_detect_ssn():
    assert pii.detect(f"ssn {SSN} on file") == {"ssn": 1}


def test_detect_card_number():
    assert pii.detect(f"card {CARD} charged") == {"card": 1}


def test_detect_email():
    assert pii.detect(f"write to {EMAIL} please") == {"email": 1}


def test_detect_all_four_categories_together():
    text = f"{PHONE} {SSN} {CARD} {EMAIL}"
    assert pii.detect(text) == {"phone": 1, "ssn": 1, "card": 1, "email": 1}


def test_redact_phone():
    result = pii.redact(f"call {PHONE}")
    assert PHONE not in result.text
    assert "[REDACTED:PHONE]" in result.text
    assert result.hits["phone"] == 1


def test_redact_ssn():
    result = pii.redact(f"ssn {SSN}")
    assert SSN not in result.text and "[REDACTED:SSN]" in result.text


def test_redact_card_number():
    result = pii.redact(f"card {CARD} charged")
    assert CARD not in result.text and "4111" not in result.text
    assert "[REDACTED:CARD]" in result.text


def test_redact_email():
    result = pii.redact(f"write to {EMAIL}")
    assert EMAIL not in result.text and "[REDACTED:EMAIL]" in result.text


def test_redact_all_four_leaves_no_raw_value():
    text = f"Contact {PHONE}, ssn {SSN}, card {CARD}, mail {EMAIL}."
    result = pii.redact(text)
    for raw in (PHONE, SSN, CARD, EMAIL):
        assert raw not in result.text
    assert result.total_hits == 4


def test_ordinary_amount_is_not_a_card():
    # $500,000 and long reference numbers must not be swept up as cards.
    assert pii.detect("Revenue was $500,000, ref 20260715.") == {}


def test_non_luhn_digit_run_is_not_a_card():
    assert pii.detect("code 1234 5678 9012 3456 on file") == {}


def test_safe_log_redacts_before_logging():
    logged = pii.safe_log(f"failed for {EMAIL} and {CARD}")
    assert EMAIL not in logged and "4111" not in logged
    assert "[REDACTED:EMAIL]" in logged and "[REDACTED:CARD]" in logged


def test_safe_error_never_echoes_raw_pii():
    message = pii.safe_error("validation failed", f"bad row for {SSN}")
    assert SSN not in message and "[REDACTED:SSN]" in message


def test_clean_text_unchanged():
    result = pii.redact("Revenue was $500,000 in Q3.")
    assert result.text == "Revenue was $500,000 in Q3."
    assert result.total_hits == 0
