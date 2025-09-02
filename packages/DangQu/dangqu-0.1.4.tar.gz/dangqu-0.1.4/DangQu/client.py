import json
import datetime
import functools

import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


class TimedCache:
    def __init__(self, duration):
        self.cache = {}
        self.duration = datetime.timedelta(seconds=duration)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapped(*args):
            now = datetime.datetime.now()
            if args in self.cache and now - self.cache[args][1] < self.duration:
                return self.cache[args][0]
            else:
                result = func(*args)
                self.cache[args] = (result, now)
                return result

        return wrapped


class DangquSdk:

    def __init__(self, domain, token_url, client_id, client_secret):
        self.doamin = domain
        self.logical_url = f'{domain}/openapis/api/Workflow/Workflow/WorkflowInstance'

        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url

        self.client = BackendApplicationClient(client_id=client_id)
        self.oauth = OAuth2Session(client=self.client)

    @property
    @TimedCache(60 * 60 * 2)
    def token(self):
        token = self.oauth.fetch_token(
            token_url=self.token_url,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        return token

    def execute_dangqu_request(self, host_tenant: str, unified_id: str, request_body: dict):
        body = {
            "isSync"            : True,
            "isReturnResult"    : True,
            "hostTenant"        : host_tenant,
            "unifiedId"         : unified_id,
            "inputParameterJson": json.dumps(request_body)
        }

        _headers = {'Authorization': 'Bearer %s' % self.token.get('access_token', '')}
        response = requests.post(self.logical_url, headers=_headers, json=body)

        return response
