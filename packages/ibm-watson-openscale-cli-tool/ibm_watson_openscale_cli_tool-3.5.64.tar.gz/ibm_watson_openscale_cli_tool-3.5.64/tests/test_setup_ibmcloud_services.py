# coding=utf-8

import json
import responses
import unittest
import argparse
from ibm_ai_openscale_cli.setup_classes.setup_ibmcloud_services import SetupIBMCloudServices

args = argparse.Namespace()
args.apikey = 'foo-key' #pragma: allowlist secret
args.url = 'https://api.aiopenscale.cloud.ibm.com'
args.headers = {'Origin': 'cli://fastpath'}
args.iam_token = False
args.env_dict = {
    'name': 'YPPROD', 
    'api': 'https://api.ng.bluemix.net', 
    'aios_url': 'https://api.aiopenscale.cloud.ibm.com', 
    'iam_url': 'https://iam.cloud.ibm.com/identity/token', 
    'uaa_url': 'https://login.ng.bluemix.net/UAALoginServerWAR/oauth/token', 
    'resource_controller_url': 'https://resource-controller.cloud.ibm.com', 
    'resource_group_url': 'https://resource-manager.cloud.ibm.com'
}

class TestSetUpServices(unittest.TestCase):
    @responses.activate
    def test_get_credentials(self):

        sics = SetupIBMCloudServices(args)
        response = sics._aios_credentials(data_mart_id="386f4391-e96c", crn="ahjkhjkkh:jgguijkh") #pragma: allowlist secret
        expected_response = {
            'apikey': 'foo-key', #pragma: allowlist secret
            'url': 'https://api.aiopenscale.cloud.ibm.com', 
            'data_mart_id': '386f4391-e96c', 
            'headers': {'Origin': 'cli://fastpath'},
            'crn': 'ahjkhjkkh:jgguijkh' #pragma: allowlist secret
        }
        assert response == expected_response