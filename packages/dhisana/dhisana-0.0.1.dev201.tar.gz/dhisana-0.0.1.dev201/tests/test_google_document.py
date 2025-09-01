import unittest
from unittest.mock import patch, MagicMock
import asyncio
import sys
import types

# Add project src to path
sys.path.insert(0, 'src')

# Stub external dependencies and heavy internal modules
sys.modules['httpx'] = types.ModuleType('httpx')

pydantic_mod = types.ModuleType('pydantic')
class BaseModel:
    pass
pydantic_mod.BaseModel = BaseModel
sys.modules['pydantic'] = pydantic_mod

schemas_sales = types.ModuleType('dhisana.schemas.sales')
class MessageItem:
    pass
schemas_sales.MessageItem = MessageItem
sys.modules['dhisana.schemas.sales'] = schemas_sales

assistant_tool_mod = types.ModuleType('dhisana.utils.assistant_tool_tag')
def assistant_tool(func):
    return func
assistant_tool_mod.assistant_tool = assistant_tool
sys.modules['dhisana.utils.assistant_tool_tag'] = assistant_tool_mod

email_helpers_mod = types.ModuleType('dhisana.utils.email_parse_helpers')
sys.modules['dhisana.utils.email_parse_helpers'] = email_helpers_mod

schemas_common = types.ModuleType('dhisana.schemas.common')
class SendEmailContext: pass
class QueryEmailContext: pass
class ReplyEmailContext: pass
schemas_common.SendEmailContext = SendEmailContext
schemas_common.QueryEmailContext = QueryEmailContext
schemas_common.ReplyEmailContext = ReplyEmailContext
sys.modules['dhisana.schemas.common'] = schemas_common

google_mod = types.ModuleType('google')
sys.modules['google'] = google_mod

google_auth_mod = types.ModuleType('google.auth')
transport_mod = types.ModuleType('google.auth.transport')
requests_mod = types.ModuleType('google.auth.transport.requests')
class Request:
    pass
requests_mod.Request = Request
sys.modules['google.auth'] = google_auth_mod
sys.modules['google.auth.transport'] = transport_mod
sys.modules['google.auth.transport.requests'] = requests_mod

oauth2_mod = types.ModuleType('google.oauth2')
service_account_mod = types.ModuleType('google.oauth2.service_account')
class Credentials:
    def __init__(self):
        self.valid = True
    def with_subject(self, subject):
        return self
    def refresh(self, request):
        pass
    @classmethod
    def from_service_account_info(cls, info, scopes=None):
        return cls()
service_account_mod.Credentials = Credentials
oauth2_mod.service_account = service_account_mod
sys.modules['google.oauth2'] = oauth2_mod
sys.modules['google.oauth2.service_account'] = service_account_mod

googleapiclient_mod = types.ModuleType('googleapiclient')
discovery_mod = types.ModuleType('googleapiclient.discovery')
def build(*args, **kwargs):
    return MagicMock()
discovery_mod.build = build
errors_mod = types.ModuleType('googleapiclient.errors')
class HttpError(Exception):
    pass
errors_mod.HttpError = HttpError
http_mod = types.ModuleType('googleapiclient.http')
class MediaFileUpload:
    pass
class MediaIoBaseDownload:
    pass
http_mod.MediaFileUpload = MediaFileUpload
http_mod.MediaIoBaseDownload = MediaIoBaseDownload
sys.modules['googleapiclient'] = googleapiclient_mod
sys.modules['googleapiclient.discovery'] = discovery_mod
sys.modules['googleapiclient.errors'] = errors_mod
sys.modules['googleapiclient.http'] = http_mod

from dhisana.utils.google_workspace_tools import read_google_document


class TestGoogleDocument(unittest.TestCase):
    @patch('dhisana.utils.google_workspace_tools.build')
    @patch('dhisana.utils.google_workspace_tools.get_google_credentials')
    def test_read_google_document(self, mock_get_credentials, mock_build):
        mock_service = MagicMock()
        mock_docs = mock_service.documents.return_value
        mock_docs.get.return_value.execute.return_value = {
            'body': {
                'content': [
                    {'paragraph': {'elements': [{'textRun': {'content': 'Hello '}}]}},
                    {'paragraph': {'elements': [{'textRun': {'content': 'World'}}]}}
                ]
            }
        }
        mock_build.return_value = mock_service

        doc_url = 'https://docs.google.com/document/d/abc123/edit'
        result = asyncio.run(read_google_document(doc_url, 'user@example.com'))

        self.assertEqual(result, 'Hello World')

if __name__ == '__main__':
    unittest.main()
