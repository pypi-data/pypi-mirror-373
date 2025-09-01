# -*- coding: utf-8 -*-
from enum import Enum

import grequests
import requests


class ListResult(Enum):
    SUCCESS = 0
    ERROR = 1


class GetServiceStatusResult(Enum):
    UP = 0
    NOT_UP = 1
    ERROR_ACCESS_DENIED = 2
    ERROR_NOT_FOUND = 3
    ERROR_RATELIMIT = 4
    ERROR_UNKNOWN = 5


class ServiceAPIHelper(object):
    def __init__(self, endpoint, exception_handler=None, proxy=None, verify=True):
        self._endpoint = endpoint
        self._url_path = 'api/service/v1'
        self._exception_handler = exception_handler
        self._proxies = dict()
        if proxy is not None:
            self._proxies[endpoint] = proxy
        self._verify = verify

    @property
    def list_url(self):
        return '{0}/{1}/list'.format(
            self._endpoint,
            self._url_path
        )

    def list(self):
        try:
            r = requests.get(self.list_url, proxies=self._proxies, verify=self._verify)
            if r is not None and r.status_code == requests.codes.ok:
                data = r.json()
                return dict(
                    code=ListResult.SUCCESS,
                    list=data
                )
            else:
                return dict(code=ListResult.ERROR)
        except Exception:
            return dict(code=ListResult.ERROR)

    @property
    def get_status_url_base(self):
        return '{0}/{1}/status/'.format(
            self._endpoint,
            self._url_path
        )

    def construct_get_status_url(self, service_id):
        return self.get_status_url_base + str(service_id)

    def _safe_create_get_status_result(self, text):
        try:
            r = GetServiceStatusResult[text]
        except KeyError:
            r = GetServiceStatusResult.ERROR_UNKNOWN

        return r

    def get_status(self, *service_ids):
        pending = (grequests.get(self.construct_get_status_url(s), proxies=self._proxies, verify=self._verify) for s in service_ids)
        responses = grequests.map(pending,
                                  exception_handler=self._exception_handler)
        results = list()
        possible_codes = [
            requests.codes.ok,
            requests.codes.forbidden,
            requests.codes.not_found,
            requests.codes.too_many_requests
        ]

        for r in responses:
            if r is None:
                continue
            service_id = int(r.request.url[len(self.get_status_url_base):])
            if r.status_code in possible_codes:
                results.append(dict(
                    service_id=service_id,
                    code=self._safe_create_get_status_result(r.text)
                ))
            else:
                results.append(dict(
                    service_id=service_id,
                    code=GetServiceStatusResult.ERROR_UNKNOWN
                ))

        return results

    def is_up(self, service_id):
        return self.get_status(service_id)[0]['code'] == GetServiceStatusResult.UP
