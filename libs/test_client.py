import time

from django.test.client import Client

import oauth2 as oauth
from piston.models import Consumer as ConsumerModel
from test_utils import RequestFactory

class TestClient(object):

    def __init__(self):
        ConsumerModel.objects.create(name='test', key='test', 
            secret='test', status='accepted')

        self.url = 'http://testserver/subscriptions/subscribe/'
        self.consumer = oauth.Consumer(key='test', secret='test')
        self.signature_method = oauth.SignatureMethod_HMAC_SHA1()
        # we're only using 2-legged auth, no need for tokens
        self.token = None

        self.params = {
            'oauth_version': '1.0',
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': int(time.time()),
        }
        self.c = Client()
        self.rf = RequestFactory()

    def tearDown(self):
        ConsumerModel.objects.filter(key='test').delete()

    def headers(self, method='POST', **kwargs):
        params = self.params.copy()
        params.update(kwargs)
        req = oauth.Request(method=method, url=self.url, parameters=params)
        req.sign_request(self.signature_method, self.consumer, self.token)
        return req.to_header()
    
    def subscribe(self, **kwargs):
        header = self.headers(**kwargs)
        return self.c.post(self.url, kwargs, **header)

    def subscribe_request(self, **kwargs):
        header = self.headers(**kwargs)
        return self.rf.post(self.url, kwargs, **header)

    def read(self, **kwargs):
        header = self.headers(method="GET", **kwargs)
        return self.c.get(self.url, kwargs, **header)
