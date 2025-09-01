# -*- coding: utf-8 -*-
from enum import Enum

import jwt
import requests


class GetPublicKeyResult(Enum):
    SUCCESS = 0
    ERROR = 1


class DecodeResult(Enum):
    SUCCESS = 0
    ERROR = 1


class CapsuleAPIHelper(object):
    def __init__(self, endpoint, proxy=None, verify=True):
        self._endpoint = endpoint
        self._proxies = dict()
        if proxy is not None:
            self._proxies[endpoint] = proxy
        self._verify = verify
        self._url_path = 'api/capsule/v1'

    @property
    def public_key_url(self):
        return '{0}/{1}/public_key'.format(
            self._endpoint,
            self._url_path
        )

    def get_public_key(self):
        try:
            r = requests.get(self.public_key_url, proxies=self._proxies, verify=self._verify)
            if r is not None and r.status_code == requests.codes.ok:
                return dict(
                    code=GetPublicKeyResult.SUCCESS,
                    public_key=r.text
                )
            else:
                return dict(code=GetPublicKeyResult.ERROR)
        except Exception:
            return dict(code=GetPublicKeyResult.ERROR)

    def decode(self, capsule):
        try:
            call = self.get_public_key()
            if call['code'] != GetPublicKeyResult.SUCCESS:
                raise Exception('Invalid public key')
            payload = jwt.decode(
                capsule,
                algorithms=['ES256', 'RS256'],
                key=call['public_key']
            )
            return dict(
                code=DecodeResult.SUCCESS,
                decoded=payload
            )
        except Exception:
            return dict(code=DecodeResult.ERROR)
