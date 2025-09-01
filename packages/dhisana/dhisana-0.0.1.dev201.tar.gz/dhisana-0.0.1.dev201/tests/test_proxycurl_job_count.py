#!/usr/bin/env python3
"""
Test file for the proxycurl_job_count function.
"""

import unittest
from dhisana.utils.proxycurl_search_leads import JobSearchParams


class TestProxycurlJobCount(unittest.TestCase):
    """Test class for proxycurl_job_count function."""
    
    def test_job_search_params_validation(self):
        """Test JobSearchParams validation."""
        # Test valid parameters
        params = JobSearchParams(
            search_id="1035",
            keyword="engineer",
            job_type="full-time",
            experience_level="mid_senior_level",
            when="past-month",
            flexibility="remote",
            geo_id=92000000
        )
        
        self.assertEqual(params.search_id, "1035")
        self.assertEqual(params.keyword, "engineer")
        self.assertEqual(params.job_type, "full-time")
        self.assertEqual(params.experience_level, "mid_senior_level")
        self.assertEqual(params.when, "past-month")
        self.assertEqual(params.flexibility, "remote")
        self.assertEqual(params.geo_id, 92000000)
    
    def test_job_search_params_optional_fields(self):
        """Test JobSearchParams with optional fields."""
        # Test with minimal parameters
        params = JobSearchParams()
        
        self.assertIsNone(params.search_id)
        self.assertIsNone(params.keyword)
        self.assertIsNone(params.job_type)
        self.assertIsNone(params.experience_level)
        self.assertIsNone(params.when)
        self.assertIsNone(params.flexibility)
        self.assertIsNone(params.geo_id)
    
    def test_job_search_params_partial_fields(self):
        """Test JobSearchParams with some fields set."""
        params = JobSearchParams(
            search_id="1035",
            keyword="engineer"
        )
        
        self.assertEqual(params.search_id, "1035")
        self.assertEqual(params.keyword, "engineer")
        self.assertIsNone(params.job_type)
        self.assertIsNone(params.experience_level)


if __name__ == "__main__":
    unittest.main()
