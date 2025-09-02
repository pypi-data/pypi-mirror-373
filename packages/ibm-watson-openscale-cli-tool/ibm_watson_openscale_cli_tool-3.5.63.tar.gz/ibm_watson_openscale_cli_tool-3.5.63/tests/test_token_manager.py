# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8

import responses
import json
import time
import unittest
from ibm_ai_openscale_cli.setup_classes.token_manager import TokenManager

class TestTokenManager(unittest.TestCase):
    @responses.activate
    def test_request_token(self):
        url = 'https://iam.cloud.ibm.com/identity/token'
        response = {
            "access_token": "oAeisG8yqPY7sFR_x66Z15", #pragma: allowlist secret
            "expires_in": 3600,
            "expiration": 1524167011,
            "refresh_token": "jy4gl91BQ" #pragma: allowlist secret
        }
        responses.add(responses.POST, url=url, body=json.dumps(response).encode("utf-8"), status=200)

        token_manager = TokenManager('apikey', 'access_token', url)
        token_manager._request_token()

        assert responses.calls[0].request.url == url
        assert responses.calls[0].response.text == str(response).replace("'", "\"")
        assert len(responses.calls) == 1


    @responses.activate
    def test_refresh_token(self):
        url = 'https://iam.cloud.ibm.com/identity/token'
        response = {
            "access_token": "oAeisG8yqPY7sFR_x66Z15", #pragma: allowlist secret
            "token_type": "Bearer",
            "expires_in": 3600,
            "expiration": 1524167011,
            "refresh_token": "jy4gl91BQ" #pragma: allowlist secret
        }
        responses.add(responses.POST, url=url, body=json.dumps(response).encode("utf-8"), status=200)

        token_manager = TokenManager('apikey', 'access_token', url)
        token_manager._refresh_token()

        assert responses.calls[0].request.url == url
        assert responses.calls[0].response.text == str(response).replace("'", "\"")
        assert len(responses.calls) == 1


    @responses.activate
    def test_is_token_expired(self):
        token_manager = TokenManager(
            'apikey', 'access_token', 'url')
        token_manager.token_info = {
            "access_token": "oAeisG8yqPY7sFR_x66Z15", #pragma: allowlist secret
            "token_type": "Bearer",
            "expires_in": 3600,
            "expiration": int(time.time()) + 6000,
            "refresh_token": "jy4gl91BQ" #pragma: allowlist secret
        }
        assert token_manager._is_token_expired() is False
        token_manager.token_info['expiration'] = int(time.time()) - 3600
        assert token_manager._is_token_expired()


    @responses.activate
    def test_is_refresh_token_expired(self):
        token_manager = TokenManager(
            'apikey', 'access_token', 'url')
        token_manager.token_info = {
            "access_token": "oAeisG8yqPY7sFR_x66Z15", #pragma: allowlist secret
            "token_type": "Bearer",
            "expires_in": 3600,
            "expiration": int(time.time()),
            "refresh_token": "jy4gl91BQ" #pragma: allowlist secret
        }
        assert token_manager._is_refresh_token_expired() is False
        token_manager.token_info['expiration'] = int(time.time()) - (8 * 24 * 3600)
        assert token_manager._is_token_expired()


    @responses.activate
    def test_get_token(self):
        url = 'https://iam.cloud.ibm.com/identity/token'
        token_manager = TokenManager('apikey', url=url)
        token_manager.user_access_token = 'user_access_token'

        # Case 1:
        token = token_manager.get_token()
        assert token == token_manager.user_access_token

        # Case 2:
        token_manager.user_access_token = ''
        response = {
            "access_token": "hellohello", #pragma: allowlist secret
            "token_type": "Bearer",
            "expires_in": 3600,
            "expiration": 1524167011,
            "refresh_token": "jy4gl91BQ" #pragma: allowlist secret
        }
        responses.add(responses.POST, url=url, body=json.dumps(response).encode("utf-8"), status=200)
        token = token_manager.get_token()
        assert token == 'hellohello'

        # Case 3:
        token_manager.token_info['expiration'] = int(
            time.time()) - (20 * 24 * 3600)
        token = token_manager.get_token()
        assert 'grant_type=urn' in responses.calls[1].request.body
        token_manager.token_info['expiration'] = int(time.time()) - 4000
        token = token_manager.get_token()
        assert 'grant_type=refresh_token' in responses.calls[2].request.body

        # Case 4
        token_manager.token_info = {
            'access_token': 'dummy', #pragma: allowlist secret
            'token_type': 'Bearer',
            'expires_in': 3600,
            'expiration': int(time.time()) + 3600,
            'refresh_token': 'jy4gl91BQ' #pragma: allowlist secret
        }
        token = token_manager.get_token()
        assert token == 'dummy'
