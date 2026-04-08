from app.core.logging_setup import mask_sensitive_data, sentry_before_send

def test_mask_pan_number() -> None:
    text = "User PAN is ABCDE1234F."
    masked = mask_sensitive_data(text)
    assert "ABCDE1234F" not in masked
    assert "[REDACTED_PAN]" in masked

def test_mask_bearer_token() -> None:
    text = "Authorization: Bearer my-secret-token"
    masked = mask_sensitive_data(text)
    assert "my-secret-token" not in masked
    assert "[REDACTED_TOKEN]" in masked

def test_mask_password() -> None:
    text = "password=my_password123; user=john"
    masked = mask_sensitive_data(text)
    assert "my_password123" not in masked
    assert "password=[REDACTED_TOKEN]; user=john" in masked

def test_sentry_before_send_headers() -> None:
    event = {
        "request": {
            "headers": {
                "authorization": "Bearer secretly",
                "x-api-key": "mykey",
                "content-type": "application/json"
            }
        }
    }
    scrubbed = sentry_before_send(event, {})
    assert scrubbed is not None
    assert scrubbed["request"]["headers"]["authorization"] == "[REDACTED]"
    assert scrubbed["request"]["headers"]["x-api-key"] == "[REDACTED]"
    assert scrubbed["request"]["headers"]["content-type"] == "application/json"

def test_sentry_before_send_data() -> None:
    event = {
        "request": {
            "data": {
                "password": "mypassword",
                "safe_field": "value"
            }
        }
    }
    scrubbed = sentry_before_send(event, {})
    assert scrubbed is not None
    assert scrubbed["request"]["data"]["password"] == "[REDACTED]"
    assert scrubbed["request"]["data"]["safe_field"] == "value"
