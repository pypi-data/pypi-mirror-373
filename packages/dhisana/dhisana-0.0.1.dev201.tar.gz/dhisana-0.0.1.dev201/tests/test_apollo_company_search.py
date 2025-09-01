import asyncio
import json
import pytest
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from src.dhisana.schemas.sales import CompanyQueryFilters
from src.dhisana.utils.apollo_tools import (
    search_companies_with_apollo_page,
    search_companies_with_apollo,
    fill_in_company_properties
)


class TestApolloCompanySearch(unittest.TestCase):
    """Test cases for Apollo company search functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_apollo_response = {
            "pagination": {
                "page": 1,
                "per_page": 25,
                "total_entries": 100,
                "total_pages": 4
            },
            "organizations": [
                {
                    "id": "123456",
                    "name": "Example Corp",
                    "primary_domain": "example.com",
                    "website_url": "https://example.com",
                    "linkedin_url": "https://linkedin.com/company/example-corp",
                    "city": "San Francisco",
                    "state": "California",
                    "country": "United States",
                    "estimated_num_employees": 150,
                    "annual_revenue": 10000000,
                    "industry": "Technology",
                    "keywords": ["saas", "software"],
                    "description": "A technology company",
                    "founded_year": 2010,
                    "latest_funding_stage": "Series B",
                    "total_funding": 5000000,
                    "technology_names": ["React", "Python", "AWS"],
                    "phone": "+1-555-123-4567",
                    "facebook_url": "https://facebook.com/example-corp",
                    "twitter_url": "https://twitter.com/example_corp"
                },
                {
                    "id": "789012",
                    "name": "Test Inc",
                    "primary_domain": "test.com",
                    "website_url": "https://test.com",
                    "linkedin_url": "https://linkedin.com/company/test-inc",
                    "city": "New York",
                    "state": "New York",
                    "country": "United States",
                    "estimated_num_employees": 500,
                    "annual_revenue": 50000000,
                    "industry": "Finance",
                    "keywords": ["fintech", "banking"],
                    "description": "A financial services company",
                    "founded_year": 2005,
                    "latest_funding_stage": "Series C",
                    "total_funding": 25000000,
                    "technology_names": ["Java", "PostgreSQL", "Kubernetes"],
                    "phone": "+1-555-987-6543",
                    "facebook_url": "",
                    "twitter_url": ""
                }
            ],
            "accounts": []
        }
        
        self.tool_config = [
            {
                "name": "apollo",
                "configuration": [
                    {"name": "apiKey", "value": "test_api_key"}
                ]
            }
        ]

    def test_fill_in_company_properties(self):
        """Test the company properties mapping function."""
        company_data = self.mock_apollo_response["organizations"][0]
        result = fill_in_company_properties(company_data)
        
        self.assertEqual(result["organization_name"], "Example Corp")
        self.assertEqual(result["primary_domain"], "example.com")
        self.assertEqual(result["website_url"], "https://example.com")
        self.assertEqual(result["organization_linkedin_url"], "https://linkedin.com/company/example-corp")
        self.assertEqual(result["organization_city"], "San Francisco")
        self.assertEqual(result["organization_state"], "California")
        self.assertEqual(result["organization_country"], "United States")
        self.assertEqual(result["organization_location"], "San Francisco, California, United States")
        self.assertEqual(result["employee_count"], 150)
        self.assertEqual(result["annual_revenue"], 10000000)
        self.assertEqual(result["industry"], "Technology")
        self.assertEqual(result["keywords"], "saas, software")
        self.assertEqual(result["description"], "A technology company")
        self.assertEqual(result["founded_year"], 2010)
        self.assertEqual(result["funding_stage"], "Series B")
        self.assertEqual(result["total_funding"], 5000000)
        self.assertEqual(result["technology_stack"], "React, Python, AWS")
        self.assertEqual(result["apollo_organization_id"], "123456")
        self.assertEqual(result["phone"], "+1-555-123-4567")
        self.assertEqual(result["facebook_url"], "https://facebook.com/example-corp")
        self.assertEqual(result["twitter_url"], "https://twitter.com/example_corp")
        
        # Check that additional_properties contains the raw data
        self.assertIn("additional_properties", result)
        self.assertIn("apollo_organization_data", result["additional_properties"])

    @patch('src.dhisana.utils.apollo_tools.fetch_apollo_data')
    @patch('src.dhisana.utils.apollo_tools.get_apollo_access_token')
    async def test_search_companies_with_apollo_page(self, mock_get_token, mock_fetch_data):
        """Test the paginated company search function."""
        mock_get_token.return_value = "test_api_key"
        mock_fetch_data.return_value = self.mock_apollo_response
        
        query = CompanyQueryFilters(
            organization_locations=["San Francisco, CA"],
            min_employees=100,
            max_employees=1000,
            organization_industries=["Technology"]
        )
        
        result = await search_companies_with_apollo_page(
            query=query,
            page=1,
            per_page=25,
            tool_config=self.tool_config
        )
        
        # Check pagination metadata
        self.assertEqual(result["current_page"], 1)
        self.assertEqual(result["per_page"], 25)
        self.assertEqual(result["total_entries"], 100)
        self.assertEqual(result["total_pages"], 4)
        self.assertTrue(result["has_next_page"])
        self.assertEqual(result["next_page"], 2)
        
        # Check results
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["organization_name"], "Example Corp")
        self.assertEqual(result["results"][1]["organization_name"], "Test Inc")
        
        # Verify API call was made correctly
        mock_fetch_data.assert_called_once()
        call_args = mock_fetch_data.call_args
        payload = call_args[1]["payload"]
        self.assertEqual(payload["page"], 1)
        self.assertEqual(payload["per_page"], 25)
        self.assertIn("organization_locations", payload)
        self.assertIn("organization_num_employees_ranges", payload)

    def test_company_query_filters_initialization(self):
        """Test that CompanyQueryFilters can be initialized with various parameters."""
        query = CompanyQueryFilters(
            organization_locations=["San Francisco, CA", "New York, NY"],
            organization_industries=["Technology", "Finance"],
            min_employees=100,
            max_employees=1000,
            revenue_range_min=1000000,
            revenue_range_max=100000000,
            q_keywords="enterprise software",
            q_organization_domains=["example.com", "test.com"],
            organization_latest_funding_stage_cd=["3", "4"],
            currently_using_any_of_technology_uids=["salesforce", "hubspot"],
            sort_by_field="employee_count",
            sort_ascending=False
        )
        
        self.assertEqual(len(query.organization_locations), 2)
        self.assertEqual(len(query.organization_industries), 2)
        self.assertEqual(query.min_employees, 100)
        self.assertEqual(query.max_employees, 1000)
        self.assertEqual(query.revenue_range_min, 1000000)
        self.assertEqual(query.revenue_range_max, 100000000)
        self.assertEqual(query.q_keywords, "enterprise software")
        self.assertEqual(len(query.q_organization_domains), 2)
        self.assertEqual(len(query.organization_latest_funding_stage_cd), 2)
        self.assertEqual(len(query.currently_using_any_of_technology_uids), 2)
        self.assertEqual(query.sort_by_field, "employee_count")
        self.assertFalse(query.sort_ascending)

    @patch('src.dhisana.utils.apollo_tools.fetch_apollo_data')
    @patch('src.dhisana.utils.apollo_tools.get_apollo_access_token')
    async def test_search_companies_with_apollo_basic(self, mock_get_token, mock_fetch_data):
        """Test the basic company search function."""
        mock_get_token.return_value = "test_api_key"
        mock_fetch_data.return_value = self.mock_apollo_response
        
        payload = {
            "organization_locations": ["San Francisco, CA"],
            "page": 1,
            "per_page": 25
        }
        
        result = await search_companies_with_apollo(
            tool_config=self.tool_config,
            dynamic_payload=payload
        )
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Example Corp")
        self.assertEqual(result[1]["name"], "Test Inc")
        
        # Verify API call was made
        mock_fetch_data.assert_called_once()


if __name__ == '__main__':
    # Run async tests
    unittest.main()
