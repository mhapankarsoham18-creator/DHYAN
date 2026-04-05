# pyright: reportMissingImports=false, reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnusedParameter=false, reportMissingParameterType=false, reportUnknownParameterType=false, reportReturnType=false

import pytest
from collections.abc import AsyncGenerator
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import get_db
from app.services.auth_service import get_current_user
from app.models import User
import uuid
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def mock_user() -> User:
    user = User()
    user.id = uuid.uuid4()
    user.firebase_uid = "test-uid-123"
    user.phone_number = "+1234567890"
    user.virtual_balance = 100000.0
    return user

@pytest.fixture
async def mock_db_session():
    # Provide an isolated mock for the DB
    session = MagicMock()
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_result.scalars.return_value.all.return_value = []
    
    session.execute = AsyncMock(return_value=mock_result)
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    yield session

@pytest.fixture
def override_dependencies(mock_user: User, mock_db_session: MagicMock):  # type: ignore[no-untyped-def]
    def _override_get_current_user() -> User:
        return mock_user
        
    def _override_get_db():  # type: ignore[no-untyped-def]
        yield mock_db_session
        
    app.dependency_overrides[get_current_user] = _override_get_current_user
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
async def async_client(override_dependencies: None) -> AsyncGenerator[AsyncClient, None]:  # noqa: ARG001
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
