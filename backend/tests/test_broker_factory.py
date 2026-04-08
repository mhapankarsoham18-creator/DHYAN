from app.services.broker.broker_factory import create_broker_client

def test_create_paper_client() -> None:
    client = create_broker_client("paper")
    assert client is not None
    assert type(client).__name__ == "PaperTradingClient"

def test_create_angelone_client_with_tokens() -> None:
    client = create_broker_client("angelone", access_token="tok", refresh_token="ref")
    # For unsupported brokers or those acting as stubs, it still returns the class instance
    assert client is not None
    assert type(client).__name__ == "AngelOneClient"

def test_create_unknown_client() -> None:
    client = create_broker_client("invalid_broker")
    assert client is None
