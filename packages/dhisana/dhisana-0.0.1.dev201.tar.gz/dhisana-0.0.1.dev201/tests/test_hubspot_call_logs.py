import asyncio
import unittest
import sys
import types
from unittest.mock import patch, AsyncMock, MagicMock

# Provide minimal stub modules so hubspot_crm_tools can be imported without
# installing heavy dependencies.
sys.modules.setdefault("aiohttp", MagicMock())
sys.modules.setdefault("bs4", types.SimpleNamespace(BeautifulSoup=MagicMock()))
sys.modules.setdefault("fastapi", types.SimpleNamespace(Query=MagicMock()))
sys.modules.setdefault("markdown", types.SimpleNamespace(markdown=MagicMock()))
sys.modules.setdefault("pydantic", types.SimpleNamespace(BaseModel=object))

# Stub out dhisana.schemas.sales to avoid requiring pydantic
sales_stub = types.ModuleType("dhsana.schemas.sales")

class HubSpotLeadInformation:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

sales_stub.HubSpotLeadInformation = HubSpotLeadInformation
sales_stub.HUBSPOT_TO_LEAD_MAPPING = {}
sys.modules.setdefault("dhisana.schemas", types.ModuleType("dhsana.schemas"))
sys.modules["dhisana.schemas.sales"] = sales_stub

from dhisana.utils.hubspot_crm_tools import get_last_n_calls_for_lead
from dhisana.schemas.sales import HubSpotLeadInformation


class TestGetLastNCallLogs(unittest.TestCase):
    """Tests for retrieving call logs using lead information."""

    @patch('dhisana.utils.hubspot_crm_tools.get_hubspot_access_token')
    @patch('aiohttp.ClientSession.get')
    @patch('aiohttp.ClientSession.post')
    def test_get_last_n_calls_by_email(self, mock_post, mock_get, mock_token):
        mock_token.return_value = 'test_token'

        # Mock search response (contact lookup)
        search_resp = AsyncMock()
        search_resp.status = 200
        search_resp.json = AsyncMock(return_value={"results": [{"id": "123"}]})

        # Mock associations response (calls ids)
        assoc_resp = AsyncMock()
        assoc_resp.status = 200
        assoc_resp.json = AsyncMock(return_value={"results": [{"id": "1"}, {"id": "2"}]})

        # Mock batch read response for calls
        batch_resp = AsyncMock()
        batch_resp.status = 200
        batch_resp.json = AsyncMock(return_value={
            "results": [
                {"id": "1", "properties": {"hs_createdate": "2023-01-01", "hs_call_title": "first"}},
                {"id": "2", "properties": {"hs_createdate": "2023-01-02", "hs_call_title": "second"}},
            ]
        })

        def async_cm(result):
            cm = AsyncMock()
            cm.__aenter__.return_value = result
            return cm

        mock_post.side_effect = [async_cm(search_resp), async_cm(batch_resp)]
        mock_get.return_value.__aenter__.return_value = assoc_resp

        lead = HubSpotLeadInformation(email="test@example.com")

        async def run_test():
            return await get_last_n_calls_for_lead(lead, n=2)

        result = asyncio.run(run_test())
        self.assertEqual([c["id"] for c in result], ["2", "1"])
        self.assertEqual(result[0]["properties"]["hs_call_title"], "second")


if __name__ == '__main__':
    unittest.main()
