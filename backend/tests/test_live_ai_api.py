# pyright: reportMissingImports=false, reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import pytest
import os
from openai import AsyncOpenAI

pytestmark = pytest.mark.asyncio

@pytest.mark.skipif(not os.getenv("NVIDIA_API_KEY"), reason="NVIDIA_API_KEY not set")
async def test_live_nvidia_nim_api_connection() -> None:
    """
    This is an integration test that fires a real request to NVIDIA NIM API.
    It proves our API key works and the mistral model is reachable.
    """
    nim_client = AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=os.environ.get("NVIDIA_API_KEY"),
    )
    
    response = await nim_client.chat.completions.create(
        model="mistralai/mistral-7b-instruct-v0.3",
        messages=[{"role": "user", "content": "Say 'hello world' literally."}],
        temperature=0.1,
        max_tokens=10,
    )
    
    assert response.choices[0].message.content is not None
    assert len(response.choices[0].message.content) > 0 # Should capture "hello world"
