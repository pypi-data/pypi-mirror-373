import unittest
from unittest.mock import patch
import argparse
import responses
from ibm_ai_openscale_cli.openscale.openscale import OpenScale

class TestOpenscale(unittest.TestCase):

    def setUp(self):
        args = argparse.Namespace()
        args.apikey = 'XXX-YYY-ZZZZ' #pragma: allowlist secret
        args.datamart_id = 'XX-YY-ZZ'
        args.datamart_name = 'Sample DataMart'
        args.env = 'ypprod'
        args.env_dict = {
            'name': 'YPPROD', 
            'api': 'https://api.ng.bluemix.net',
            'aios_url': 'https://api.aiopenscale.cloud.ibm.com',
            'iam_url': 'https://iam.cloud.ibm.com/identity/token',
            'uaa_url': 'https://login.ng.bluemix.net/UAALoginServerWAR/oauth/token',
            'resource_controller_url': 'https://resource-controller.cloud.ibm.com',
            'resource_group_url': 'https://resource-manager.cloud.ibm.com'
            }
        args.keep_schema = False
        args.is_icp = False
        args.service_name = 'WML' 
        args.wos_sdk_timeout = 60
        self.args = args  
        self.aios_credentials = {
            'apikey': 'XXX-YYY-ZZZZ', #pragma: allowlist secret
            'url': 'https://api.aiopenscale.cloud.ibm.com', 
            'data_mart_id': 'XX-YY-ZZ', 
            'headers': {'Origin': 'cli://fastpath'}
        }

    @responses.activate
    def test_get_datamart_id(self):
        with patch('ibm_ai_openscale_cli.openscale.openscale.APIClient') as MockClass:
            instance = MockClass.return_value
            instance.method.return_value = {'access_token' : 'foo-token'} #pragma: allowlist secret
            os = OpenScale(self.args, self.aios_credentials, database_credentials = None, ml_engine_credentials = None)
            self.assertEqual(os.get_datamart_id(), self.args.datamart_id)
    