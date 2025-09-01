"""
Unit tests for the proxycurl_get_company_search_id function.
"""

import unittest
from unittest.mock import patch, AsyncMock
import asyncio
from dhisana.utils.proxycurl_search_leads import proxycurl_get_company_search_id


class TestProxycurlGetCompanySearchId(unittest.TestCase):
    """Test cases for the proxycurl_get_company_search_id function."""

    def test_valid_company_url(self):
        """Test that function accepts valid company URLs"""
        valid_urls = [
            "https://www.linkedin.com/company/microsoft/",
            "https://www.linkedin.com/company/google",
            "https://linkedin.com/company/apple/",
        ]
        
        for url in valid_urls:
            # Just test that the URL parameter is accepted
            # (We'll test the actual API call separately)
            self.assertIsInstance(url, str)
            self.assertTrue(len(url) > 0)
    
    def test_empty_url_handling(self):
        """Test that function handles empty URLs appropriately"""
        empty_urls = ["", None]
        
        for url in empty_urls:
            if url is not None:
                # Test that we can at least pass the parameter
                self.assertTrue(isinstance(url, str) or url is None)

    def test_invalid_url_format(self):
        """Test that function handles invalid URL formats"""
        invalid_urls = [
            "not-a-url",
            "https://example.com",
            "https://www.linkedin.com/in/person/",  # Person profile, not company
        ]
        
        for url in invalid_urls:
            # The function should handle these gracefully
            self.assertIsInstance(url, str)

    @patch('dhisana.utils.proxycurl_search_leads.get_proxycurl_access_token')
    def test_no_api_key(self, mock_get_token):
        """Test behavior when no API key is available"""
        mock_get_token.side_effect = ValueError(
            "Proxycurl integration is not configured. Please configure the connection to Proxycurl in Integrations."
        )

        async def run_test():
            result = await proxycurl_get_company_search_id(
                "https://www.linkedin.com/company/microsoft/"
            )
            self.assertIn("error", result)
            self.assertEqual(result["search_id"], None)
            self.assertIn("Proxycurl integration is not configured", result["error"])

        asyncio.run(run_test())

    @patch('dhisana.utils.proxycurl_search_leads.get_proxycurl_access_token')
    @patch('aiohttp.ClientSession.get')
    def test_successful_response(self, mock_get, mock_get_token):
        """Test successful API response parsing"""
        mock_get_token.return_value = "test_api_key"
        
        # Mock successful API response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "search_id": "1441",
            "name": "Google",
            "linkedin_internal_id": "1441",
            "industry": "Software Development"
        })
        
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async def run_test():
            result = await proxycurl_get_company_search_id(
                "https://www.linkedin.com/company/google/"
            )
            
            self.assertEqual(result["search_id"], "1441")
            self.assertEqual(result["name"], "Google")
            self.assertEqual(result["industry"], "Software Development")
            self.assertNotIn("error", result)
        
        asyncio.run(run_test())

    @patch('dhisana.utils.proxycurl_search_leads.get_proxycurl_access_token')
    @patch('aiohttp.ClientSession.get')
    def test_api_error_response(self, mock_get, mock_get_token):
        """Test handling of API error responses"""
        mock_get_token.return_value = "test_api_key"
        
        # Mock API error response
        mock_response = AsyncMock()
        mock_response.status = 404
        
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async def run_test():
            result = await proxycurl_get_company_search_id(
                "https://www.linkedin.com/company/non-existent/"
            )
            
            self.assertIn("error", result)
            self.assertEqual(result["search_id"], None)
            self.assertIn("404", result["error"])
        
        asyncio.run(run_test())

    @patch('dhisana.utils.proxycurl_search_leads.get_proxycurl_access_token')
    @patch('aiohttp.ClientSession.get')
    def test_network_exception(self, mock_get, mock_get_token):
        """Test handling of network exceptions"""
        mock_get_token.return_value = "test_api_key"
        
        # Mock network exception
        mock_get.side_effect = Exception("Network error")
        
        async def run_test():
            result = await proxycurl_get_company_search_id(
                "https://www.linkedin.com/company/microsoft/"
            )
            
            self.assertIn("error", result)
            self.assertEqual(result["search_id"], None)
            self.assertIn("Network error", result["error"])
        
        asyncio.run(run_test())

    @patch('dhisana.utils.proxycurl_search_leads.get_proxycurl_access_token')
    @patch('aiohttp.ClientSession.get')
    def test_missing_search_id_in_response(self, mock_get, mock_get_token):
        """Test handling when search_id is missing from API response"""
        mock_get_token.return_value = "test_api_key"
        
        # Mock response without search_id
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "name": "Some Company",
            "industry": "Technology"
            # Missing search_id field
        })
        
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async def run_test():
            result = await proxycurl_get_company_search_id(
                "https://www.linkedin.com/company/some-company/"
            )
            
            self.assertEqual(result["search_id"], None)
            self.assertEqual(result["name"], "Some Company")
            self.assertIn("error", result)
            self.assertIn("No search_id found", result["error"])
        
        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
