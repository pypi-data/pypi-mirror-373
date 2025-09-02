# coding=utf-8

import json
import responses
import argparse
import unittest
from ibm_ai_openscale_cli.setup_classes.resource_controller import ResourceController
from ibm_ai_openscale_cli.setup_classes.setup_ibmcloud_services import SetupIBMCloudServices
from ibm_ai_openscale_cli.setup_classes.token_manager import TokenManager
from ibm_ai_openscale_cli.setup_classes.setup_ibmcloud_services_rest import SetupIBMCloudServicesRest

base_url = 'https://resource-controller.cloud.ibm.com'
fake_access_token = 'foo_token'
resource_group_url = 'https://resource-manager.cloud.ibm.com'

fake_instance = {
    'id': 'crn:v1:public:public:service_name:global:a/foo:instance_ids::',
    'guid': 'bar',
    'name': 'openscale-fake-instance',
    'region_id': 'us-south',
    'created_at': '2018-04-19T00:18:53.302077457Z',
    'resource_plan_id': '2fdf0c08-2d32-4f46-84b5-32e0c92fffd8',
    'resource_group_id': '0be5ad401ae913d8ff665d92680664ed', #pragma: allowlist secret
    'resource_id': 'dff97f5c-bc5e-4455-b470-411c3edbe49c'
}
fake_key = {
    'id': 'crn:v1:staging:public:cloud-object-storage:global:a/4329073d16d2f3663f74bfa955259139:8d7af921-b136-4078-9666-081bd8470d94:resource-key:23693f48-aaa2-4079-b0c7-334846eff8d0',
    'guid': '23693f48-aaa2-4079-b0c7-334846eff8d0',
    'name': 'openscale-fastpath-credentials',
    'parameters': {
        'role_crn': 'crn:v1:bluemix:public:iam::::serviceRole:Writer'
    },
    'resource_group_id': '0be5ad401ae913d8ff665d92680664ed', #pragma: allowlist secret
    'resource_id': 'dff97f5c-bc5e-4455-b470-411c3edbe49c',
    'credentials': {
        'apikey': 'XXXX-YYYY-ZZZZ', #pragma: allowlist secret
        'url': 'https://cloud.ibm.com',
        'endpoints' : {
                    
        }
    }
}
 
args = argparse.Namespace()
args.is_icp = False
args.env = 'ypprod'
args.iam_token = True
args.iam_access_token = fake_access_token
args.env_dict = {
    'name': 'YPPROD', 
    'api': 'https://api.ng.bluemix.net', 
    'aios_url': 'https://api.aiopenscale.cloud.ibm.com', 
    'iam_url': 'https://iam.cloud.ibm.com/identity/token', 
    'uaa_url': 'https://login.ng.bluemix.net/UAALoginServerWAR/oauth/token', 
    'resource_controller_url': 'https://resource-controller.cloud.ibm.com', 
    'resource_group_url': 'https://resource-manager.cloud.ibm.com',
    'wml_v4_url': 'https://us-south.ml.cloud.ibm.com'
}
args.resource_group = 'default'
args.openscale_plan = "lite"
args.wml_plan = "lite"
args.apikey = "XXXX-YYYY-ZZZZ" #pragma: allowlist secret
args.wml = None
args.cos = None


class TestSetUpRestServices(unittest.TestCase):
    @responses.activate
    def test_get_credentials(self):
        
        sisr = SetupIBMCloudServicesRest(args)

        expected_instances = {
            'resources': [fake_instance],
            'rows_count': 1
        }
        responses.add(
            responses.GET,
            '{0}/v2/resource_instances?resource_id=foo'.format(base_url),
            body=json.dumps(expected_instances),
            status=200,
            content_type='application/json')

        expected_keys = {
            'resources': [fake_key],
            'rows_count': 1
        }
        responses.add(
            responses.GET,
            '{0}/v2/resource_instances/{1}/resource_keys'.format(
                base_url, fake_instance['guid']),
            body=json.dumps(expected_keys),
            status=200,
            content_type='application/json')

        params = {}
        params['resource_name'] = 'openscale-fake-instance'
        params['resource_id'] = 'foo'
        params['resource_plan_id'] = 'resource_plan_id'
        params['resource_group'] = 'resource_group'
        params['resource_group_name'] = 'resource_group_name'

        response = sisr._get_credentials(service_display_name= 'WML', params = params, is_rc_based = True)

        assert len(responses.calls) == 2
        assert response['id'] == fake_instance['guid']
        assert response['created_at'] == fake_instance['created_at']
        assert response['credentials'] == fake_key['credentials']

    @responses.activate
    def test_setup_aios(self):

        sisr = SetupIBMCloudServicesRest(args)

        expected_instances = {
            'resources': [fake_instance],
            'rows_count': 1
        }
        responses.add(
            responses.GET,
            '{0}/v2/resource_instances?resource_id=2ad019f3-0fd6-4c25-966d-f3952481a870'.format(base_url),
            body=json.dumps(expected_instances),
            status=200,
            content_type='application/json')


        expected_response = {
            'apikey': 'XXXX-YYYY-ZZZZ', #pragma: allowlist secret
            'iam_token': True,
            'url': 'https://api.aiopenscale.cloud.ibm.com',
            'data_mart_id': 'bar',
            'crn': 'crn:v1:public:public:service_name:global:a/foo:instance_ids::', #pragma: allowlist secret
            'headers': {'Origin': 'cli://fastpath'}
        }

        response = sisr.setup_aios()
        
        assert len(responses.calls) == 1
        assert response == expected_response


    @responses.activate
    def test_setup_wml(self):

        sisr = SetupIBMCloudServicesRest(args)

        expected_instances = {
            'resources': [fake_instance],
            'rows_count': 1
        }
        responses.add(
            responses.GET,
            '{0}/v2/resource_instances?resource_id=51c53b72-918f-4869-b834-2d99eb28422a'.format(base_url),
            body=json.dumps(expected_instances),
            status=200,
            content_type='application/json')

        expected_keys = {
            'resources': [fake_key],
            'rows_count': 1
        }
        responses.add(
            responses.GET,
            '{0}/v2/resource_instances/{1}/resource_keys'.format(
                base_url, fake_instance['guid']),
            body=json.dumps(expected_keys),
            status=200,
            content_type='application/json')

        expected_response = {
            'apikey': 'XXXX-YYYY-ZZZZ', #pragma: allowlist secret
            'url': 'https://us-south.ml.cloud.ibm.com',
            'instance_crn': 'crn:v1:public:public:service_name:global:a/foo:instance_ids::', #pragma: allowlist secret
            'instance_name': 'openscale-fake-instance',
            'token': True
        }

        response = sisr.setup_wml()
        assert response == expected_response


    @responses.activate
    def test_setup_cos(self):

        sisr = SetupIBMCloudServicesRest(args)

        expected_instances = {
            'resources': [fake_instance],
            'rows_count': 1
        }
        responses.add(
            responses.GET,
            '{0}/v2/resource_instances?resource_id=dff97f5c-bc5e-4455-b470-411c3edbe49c'.format(base_url),
            body=json.dumps(expected_instances),
            status=200,
            content_type='application/json')

        expected_keys = {
            'resources': [fake_key],
            'rows_count': 1
        }
        responses.add(
            responses.GET,
            '{0}/v2/resource_instances/{1}/resource_keys'.format(
                base_url, fake_instance['guid']),
            body=json.dumps(expected_keys),
            status=200,
            content_type='application/json')

        expected = {
            'resources' : [{
                'id': '0be5ad401ae913d8ff665d92680664ed',
                'guid': '23693f48-aaa2-4079-b0c7-334846eff8d0',
                'name': 'openscale-fastpath-credentials',
                'account_id' : '4329073d16d2f3663f74bfa955259139',
                'state': 'ACTIVE', 
                'default': False, 
                'crn': 'crn:v1:staging:public:cloud-object-storage:global:a/4329073d16d2f3663f74bfa955259139:8d7af921-b136-4078-9666-081bd8470d94:resource-key:23693f48-aaa2-4079-b0c7-334846eff8d0', #pragma: allowlist secret
                'resource_group_id': '0be5ad401ae913d8ff665d92680664ed', #pragma: allowlist secret
                'resource_id': 'dff97f5c-bc5e-4455-b470-411c3edbe49c',
                'credentials': {
                    'apikey': 'XXXX-YYYY-ZZZZ', #pragma: allowlist secret
                    'url': 'https://cloud.ibm.com',
                    'endpoints' : {

                    }
                }
            }]
        }


        responses.add(
            responses.GET,
            '{0}/v2/resource_groups'.format(base_url),
            body=json.dumps(expected),
            status=200,
            content_type='application/json')
        
        responses.add(
            responses.GET,
            '{0}/v2/resource_groups'.format(resource_group_url),
            body=json.dumps(expected),
            status=200,
            content_type='application/json')
        
        responses.add(
            responses.POST,
            '{0}/v2/resource_instances'.format(base_url),
            body=json.dumps(fake_instance),
            status=200,
            content_type='application/json')

        responses.add(
            responses.GET,
            '{0}/v2/resource_instances/23693f48-aaa2-4079-b0c7-334846eff8d0/resource_keys'.format(
                base_url),
            body=json.dumps(expected_keys),
            status=200,
            content_type='application/json')

        expected_response = {
            'apikey': 'XXXX-YYYY-ZZZZ', #pragma: allowlist secret
            'url': 'https://cloud.ibm.com',
            'endpoints' : {
                        
            }
        }

        response = sisr.setup_cos()
        assert len(responses.calls) == 5
        assert response == expected_response
