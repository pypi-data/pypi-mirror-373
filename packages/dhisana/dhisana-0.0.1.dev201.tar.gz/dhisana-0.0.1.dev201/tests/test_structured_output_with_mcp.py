import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from pydantic import BaseModel

from src.dhisana.utils.generate_structured_output_internal import (
    get_structured_output_with_mcp,
)


class DummyModel(BaseModel):
    foo: str


class TestStructuredOutputWithMCP(unittest.TestCase):
    def test_mcp_tool_usage(self):
        fake_completion = MagicMock()
        fake_completion.output = [
            MagicMock(type="message", content=[MagicMock(text='{"foo": "bar"}')])
        ]
        mock_client = MagicMock()
        mock_client.responses.create = AsyncMock(return_value=fake_completion)

        async def runner():
            with patch(
                "src.dhisana.utils.generate_structured_output_internal.create_async_openai_client",
                return_value=mock_client,
            ):
                result, status = await get_structured_output_with_mcp(
                    "hello",
                    DummyModel,
                    server_label="stripe",
                    server_url="https://mcp.stripe.com",
                    api_key_header_name="Authorization",
                    api_key_header_value="Bearer key",
                )
                self.assertEqual(status, "SUCCESS")
                self.assertEqual(result.foo, "bar")
                mock_client.responses.create.assert_called()
                _, kwargs = mock_client.responses.create.call_args
                self.assertIn(
                    {
                        "type": "mcp",
                        "server_label": "stripe",
                        "server_url": "https://mcp.stripe.com",
                        "headers": {"Authorization": "Bearer key"},
                    },
                    kwargs.get("tools", []),
                )

        asyncio.run(runner())


if __name__ == "__main__":
    unittest.main()
