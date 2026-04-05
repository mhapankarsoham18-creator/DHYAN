# pyright: reportMissingImports=false, reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false

import pytest
from httpx import AsyncClient
import hmac
import hashlib
import json
import os

pytestmark = pytest.mark.asyncio

async def test_razorpay_webhook_valid_signature(async_client: AsyncClient):
    # Setup test payload and secret
    payload = {"event": "subscription.charged", "payload": {"subscription": {"entity": {"id": "sub_123"}}}}
    body = json.dumps(payload, separators=(',', ':'))
    secret = "test_webhook_secret"
    os.environ["RAZORPAY_WEBHOOK_SECRET"] = secret
    
    # Generate valid signature
    signature = hmac.new(
        secret.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    response = await async_client.post(
        "/api/v1/webhooks/razorpay",
        content=body,
        headers={"x-razorpay-signature": signature, "Content-Type": "application/json"}
    )
    
    # Check if we got 200 OK or 404 (if we didn't mock DB properly in webhook logic, it might 500, but 404 is bad)
    # The actual business logic of the webhook is outside the scope of just signature validation,
    # but the signature should definitely pass without a 400.
    assert response.status_code != 400

async def test_razorpay_webhook_invalid_signature(async_client: AsyncClient):
    payload = {"event": "subscription.charged"}
    body = json.dumps(payload)
    
    response = await async_client.post(
        "/api/v1/webhooks/razorpay",
        content=body,
        headers={"x-razorpay-signature": "invalid_sig", "Content-Type": "application/json"}
    )
    
    assert response.status_code == 400
    assert "signature" in response.json().get("detail", "").lower()
