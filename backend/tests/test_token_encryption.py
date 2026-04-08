# pyright: reportMissingImports=false, reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
from app.services.token_encryption import TokenEncryption

def test_aes_encryption_decryption_round_trip() -> None:
    user_id = "user123"
    original_token = "ey.secret.broker.token.12345"
    
    encrypted = TokenEncryption.encrypt_token(original_token, user_id)
    assert encrypted is not None
    assert encrypted != original_token
    
    decrypted = TokenEncryption.decrypt_token(encrypted, user_id)
    assert decrypted == original_token

def test_encryption_returns_none_for_empty_token() -> None:
    assert TokenEncryption.encrypt_token("", "user123") is None

def test_decryption_fails_with_different_user() -> None:
    original_token = "secret123"
    encrypted = TokenEncryption.encrypt_token(original_token, "userA")
    assert encrypted is not None
    
    decrypted_wrong_user = TokenEncryption.decrypt_token(encrypted, "userB")
    assert decrypted_wrong_user is None
