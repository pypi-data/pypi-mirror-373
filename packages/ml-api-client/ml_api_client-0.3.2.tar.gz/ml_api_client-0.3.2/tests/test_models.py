import pytest


@pytest.mark.asyncio
async def test_list_models(api_client, env_variables):
    response = await api_client.models.list_models()
    assert "data" in response
