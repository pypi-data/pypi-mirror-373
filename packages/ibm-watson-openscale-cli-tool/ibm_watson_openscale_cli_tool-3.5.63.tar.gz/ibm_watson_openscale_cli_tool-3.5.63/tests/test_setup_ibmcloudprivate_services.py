# coding=utf-8

import json
import responses
import argparse
import unittest
from ibm_ai_openscale_cli.setup_classes.setup_ibmcloudprivate_services import SetupIBMCloudPrivateServices

args = argparse.Namespace()
args.iam_token = False
args.username = "admin" #pragma: allowlist secret
args.password = "fake_password" #pragma: allowlist secret
args.datamart_id = "data-mart-id"
args.url = "https://resource-controller.cloud.ibm.com:8080"
args.wml = ""
args.wml_json = ""
args.v4 = True
args.iam_integration = False

class TestSetUpICP(unittest.TestCase):
    def test_setup_wml(self):
        sicps = SetupIBMCloudPrivateServices(args)

        response = sicps.setup_aios()

        expected_response = {
            "username": "admin", #pragma: allowlist secret
            "password": "fake_password", #pragma: allowlist secret
            "url": "https://resource-controller.cloud.ibm.com:8080", 
            "hostname": "https://resource-controller.cloud.ibm.com", 
            "port": "8080", 
            "data_mart_id": "data-mart-id"
        }
        
        assert len(response) == 6
        assert response == expected_response

    def test_setup_aios(self):
        sicps = SetupIBMCloudPrivateServices(args)

        response = sicps.setup_wml()

        expected_response = {
            "username": "admin", #pragma: allowlist secret
            "password": "fake_password", #pragma: allowlist secret
            "instance_id": "wml_local", 
            "version": "4.0", 
            "url": "https://resource-controller.cloud.ibm.com"
        }
        
        assert len(response) == 5
        assert response == expected_response
