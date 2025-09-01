import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from src.dhisana.utils.test_connect import test_connectivity

class TestMCPConnectivity(unittest.TestCase):
    def test_mcp_server_connectivity_dispatch(self):
        async def runner():
            with patch('src.dhisana.utils.test_connect.test_mcp_server', new=AsyncMock(return_value={'success': True, 'status_code': 200, 'error_message': None})):
                tool_config = [
                    {
                        'name': 'mcpServer',
                        'configuration': [
                            {'name': 'serverLabel', 'value': 'stripe'},
                            {'name': 'serverUrl', 'value': 'https://mcp.stripe.com'},
                            {'name': 'apiKeyHeaderName', 'value': 'Authorization'},
                            {'name': 'apiKeyHeaderValue', 'value': 'Bearer key'},
                        ]
                    }
                ]
                result = await test_connectivity(tool_config)
                assert 'mcpServer' in result
                assert result['mcpServer']['success']
        asyncio.run(runner())

if __name__ == '__main__':
    unittest.main()
