
import unittest
import json
import responses
from ibm_ai_openscale_cli.utility_classes.utils import executeCommandWithResult,\
        jsonFileToDict, remove_port_from_url, update_url


class TestUtils(unittest.TestCase):
    def test_executeCommandWithResult(self):
        response = executeCommandWithResult('pwd -P')
        assert 'aios-fast-path' in response


    def test_jsonFileToDict(self):

        response = jsonFileToDict(filename="openscale_fastpath_cli/tests/test_props/testfile.json")

        expected_response = {
            'id': 'crn:v1:public:public:service_name:global:a/foo:instance_ids::',
            'guid': 'bar',
            'name': 'openscale-fake-instance',
            'region_id': 'us-south',
            'created_at': '2018-04-19T00:18:53.302077457Z',
            'resource_plan_id': '2fdf0c08-2d32-4f46-84b5-32e0c92fffd8',
            'resource_group_id': '0be5ad401ae913d8ff665d92680664ed',
            'crn': 'crn:v1:public:public:service_name:global:a/foo:instance_ids::', #pragma: allowlist secret
            'resource_id': 'dff97f5c-bc5e-4455-b470-411c3edbe49c'}
        assert response == expected_response


    def test_remove_port_from_url(self):

        url = 'https://resource-controller.cloud.ibm.com:8080'
        expected_response = 'https://resource-controller.cloud.ibm.com'
        response = remove_port_from_url(url)

        assert response == expected_response


    def test_update_url(self):
        url = 'https://resource-controller.cloud.ibm.com:8080'
        new_hostname = 'resource-manager.cloud.ibm.com'

        response = update_url(url, new_hostname)
        expected_response = 'https://resource-manager.cloud.ibm.com:8080'

        assert response == expected_response
