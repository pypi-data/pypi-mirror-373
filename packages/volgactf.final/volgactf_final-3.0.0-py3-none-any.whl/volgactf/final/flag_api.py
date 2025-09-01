# -*- coding: utf-8 -*-
from enum import Enum
import grequests
import requests
import dateutil.parser


class SubmitResult(Enum):
    SUCCESS = 0  # submitted flag has been accepted
    ERROR_UNKNOWN = 1  # generic error
    ERROR_ACCESS_DENIED = 2  # the attacker does not appear to be a team
    ERROR_COMPETITION_NOT_STARTED = 3  # contest has not been started yet
    ERROR_COMPETITION_PAUSED = 4  # contest has been paused
    ERROR_COMPETITION_FINISHED = 5  # contest has been completed
    ERROR_FLAG_INVALID = 6  # submitted data has invalid format
    ERROR_RATELIMIT = 7  # attack attempts limit exceeded
    ERROR_FLAG_EXPIRED = 8  # submitted flag has expired
    ERROR_FLAG_YOUR_OWN = 9  # submitted flag belongs to the attacking team
    ERROR_FLAG_SUBMITTED = 10  # submitted flag has been accepted already
    ERROR_FLAG_NOT_FOUND = 11  # submitted flag has not been found
    ERROR_SERVICE_STATE_INVALID = 12  # the attacking team service is not up


class GetInfoResult(Enum):
    SUCCESS = 0  # submitted flag has been accepted
    ERROR_UNKNOWN = 1  # generic error
    ERROR_ACCESS_DENIED = 2  # getinfo calls are allowed from a team's subnet
    ERROR_NOT_FOUND = 3  # flag is invalid
    ERROR_RATELIMIT = 4  # rate limit exceeded


class FlagAPIHelper(object):
    def __init__(self, endpoint, exception_handler=None, proxy=None, verify=True):
        self._endpoint = endpoint
        self._url_path = 'api/flag/v1'
        self._exception_handler = exception_handler
        self._proxies = dict()
        if proxy is not None:
            self._proxies[endpoint] = proxy
        self._verify = verify

    @property
    def submit_url(self):
        return '{0}/{1}/submit'.format(
            self._endpoint,
            self._url_path
        )

    def _safe_create_submit_result(self, text):
        try:
            r = SubmitResult[text]
        except KeyError:
            r = SubmitResult.ERROR_UNKNOWN

        return r

    def submit(self, *flags):
        u = self.submit_url
        h = {'Content-Type': 'text/plain'}
        pending = (grequests.post(u, data=f, headers=h, proxies=self._proxies, verify=self._verify) for f in flags)
        responses = grequests.map(pending,
                                  exception_handler=self._exception_handler)
        results = list()
        possible_codes = [
            requests.codes.ok,
            requests.codes.bad_request,
            requests.codes.forbidden,
            requests.codes.request_entity_too_large,
            requests.codes.too_many_requests
        ]

        for r in responses:
            if r is None:
                continue
            flag = r.request.body
            if r.status_code in possible_codes:
                results.append(dict(
                    flag=flag,
                    code=self._safe_create_submit_result(r.text)
                ))
            else:
                results.append(dict(
                    flag=flag,
                    code=SubmitResult.ERROR_UNKNOWN
                ))

        return results

    @property
    def get_info_url_base(self):
        return '{0}/{1}/info/'.format(
            self._endpoint,
            self._url_path
        )

    def construct_get_info_url(self, flag):
        return self.get_info_url_base + flag

    def _safe_create_get_info_result(self, text):
        try:
            r = GetInfoResult[text]
        except KeyError:
            r = GetInfoResult.ERROR_UNKNOWN

        return r

    def get_info(self, *flags):
        pending = (grequests.get(self.construct_get_info_url(f), proxies=self._proxies, verify=self._verify) for f in flags)
        responses = grequests.map(pending,
                                  exception_handler=self._exception_handler)
        results = list()
        possible_error_codes = [
            requests.codes.forbidden,
            requests.codes.not_found,
            requests.codes.too_many_requests
        ]

        for r in responses:
            if r is None:
                continue
            flag = r.request.url[len(self.get_info_url_base):]
            if r.status_code == requests.codes.ok:
                data = r.json()
                results.append(dict(
                    flag=flag,
                    code=GetInfoResult.SUCCESS,
                    team=data['team'],
                    service=data['service'],
                    round=data['round'],
                    nbf=dateutil.parser.parse(data['nbf']),
                    exp=dateutil.parser.parse(data['exp'])
                ))
            elif r.status_code in possible_error_codes:
                results.append(dict(
                    flag=flag,
                    code=self._safe_create_get_info_result(r.text)
                ))
            else:
                results.append(dict(
                    flag=flag,
                    code=GetInfoResult.ERROR_UNKNOWN
                ))

        return results
