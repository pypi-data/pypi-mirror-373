import asyncio
import json
import unittest
from unittest.mock import AsyncMock, patch

from src.dhisana.utils.serpapi_search_tools import (
    find_user_linkedin_url_with_serper,
    LeadSearchResult,
)


class TestFindUserLinkedInUrlWithSerper(unittest.TestCase):
    def test_match_and_parse(self):
        async def runner():
            fake_results = [json.dumps({
                "title": "Foo Bar - CEO",
                "link": "https://www.linkedin.com/in/foo-bar",
                "snippet": "Foo Bar is CEO at Example"
            })]

            fake_lead = LeadSearchResult(full_name="Foo Bar", job_title="CEO")
            with patch(
                "src.dhisana.utils.serpapi_search_tools.search_google_serper",
                new=AsyncMock(return_value=fake_results),
            ), patch(
                "src.dhisana.utils.serpapi_search_tools.get_structured_output_internal",
                new=AsyncMock(return_value=(fake_lead, "SUCCESS")),
            ):
                result = await find_user_linkedin_url_with_serper(
                    "https://www.linkedin.com/in/foo-bar"
                )
                self.assertIsInstance(result, dict)
                self.assertEqual(result["user_linkedin_url"], "https://www.linkedin.com/in/foo-bar")
        asyncio.run(runner())

    def test_no_match_returns_none(self):
        async def runner():
            fake_results = [json.dumps({
                "title": "Other Person",
                "link": "https://www.linkedin.com/in/other",
                "snippet": "Other"
            })]
            with patch(
                "src.dhisana.utils.serpapi_search_tools.search_google_serper",
                new=AsyncMock(return_value=fake_results),
            ):
                result = await find_user_linkedin_url_with_serper(
                    "https://www.linkedin.com/in/foo-bar"
                )
                self.assertIsNone(result)
        asyncio.run(runner())


if __name__ == "__main__":
    unittest.main()
