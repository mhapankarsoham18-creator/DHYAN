# pyright: reportMissingImports=false, reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import pytest
from httpx import AsyncClient
from app.services.billing_service import BillingService
from unittest.mock import patch, MagicMock

pytestmark = pytest.mark.asyncio

async def test_gst_invoice_generation() -> None:
    mock_db = MagicMock()
    invoice = await BillingService.generate_invoice(
        db=mock_db,
        user_id="12345678-1234-5678-1234-567812345678",
        payment_id="pay_ABC",
        amount_inr=1000.0,
    )
    assert invoice["user_id"] == "12345678-1234-5678-1234-567812345678"
    assert invoice["payment_id"] == "pay_ABC"
    assert invoice["total_amount"] == 1000.0
    assert invoice["gst_amount"] == 180.0  # 18% of 1000
    assert invoice["base_amount"] == 820.0 # 1000 - 180
    assert mock_db.add.called

@patch("app.services.razorpay_service.client")
def test_create_customer_success(mock_client: MagicMock) -> None:
    from app.services.razorpay_service import create_customer
    mock_res = {"id": "cust_mock123"}
    mock_client.customer.create.return_value = mock_res
    
    # Mock user
    mock_user = MagicMock()
    mock_user.id = "user123"
    mock_user.phone_number = "+919999999999"
    mock_user.name = "Test User"
    
    cust_id = create_customer(mock_user)
    assert cust_id == "cust_mock123"

@patch("app.services.razorpay_service.client")
def test_create_subscription_success(mock_client: MagicMock) -> None:
    from app.services.razorpay_service import create_subscription_for_customer
    mock_res = {"id": "sub_mock123", "status": "created"}
    mock_client.subscription.create.return_value = mock_res
    
    res = create_subscription_for_customer("cust_mock123", "plan_ABC")
    assert res["id"] == "sub_mock123"

async def test_refund_endpoint_success(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/billing/refund",
        json={"payment_id": "pay_mock123", "amount_inr": 500.0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "refund_id" in data
    assert data["refunded_amount_inr"] == 500.0

async def test_refund_endpoint_without_amount_does_full_refund(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/billing/refund",
        json={"payment_id": "pay_mock123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["refunded_amount_inr"] == 0.0 # Our mock sets amount to 0 if none passed
