"""Tests for certbot_dns_desec.dns_desec."""

import json
import unittest
from unittest.mock import patch

import mock
import requests_mock
from certbot import errors
from certbot.compat import os
from certbot.plugins import dns_test_common
from certbot.plugins.dns_test_common import DOMAIN
from certbot.tests import util as test_util

FAKE_TOKEN = "faketoken"
FAKE_ENDPOINT = "mock://endpoint"


class AuthenticatorTest(
    test_util.TempDirTestCase, dns_test_common.BaseAuthenticatorTest
):
    TXT = {'"preexisting" "TXT record 1/2"', '"preexisting TXT record 2/2"'}

    def setUp(self):
        super(AuthenticatorTest, self).setUp()

        from certbot_dns_desec.dns_desec import Authenticator

        path = os.path.join(self.tempdir, "file.ini")
        dns_test_common.write(
            {
                "desec_token": FAKE_TOKEN,
                "desec_endpoint": FAKE_ENDPOINT,
            },
            path,
        )

        super(AuthenticatorTest, self).setUp()
        self.config = mock.MagicMock(
            desec_credentials=path, desec_propagation_seconds=0
        )  # don't wait during tests

        self.auth = Authenticator(self.config, "desec")
        self.mock_zone = {'name': DOMAIN, 'minimum_ttl': 42}

        self.mock_client = mock.MagicMock()
        self.mock_client.get_authoritative_zone.return_value = self.mock_zone
        self.mock_client.get_txt_rrset.return_value = self.TXT
        # _get_desec_client | pylint: disable=protected-access
        self.auth._get_desec_client = mock.MagicMock(return_value=self.mock_client)

    @test_util.patch_display_util()
    def test_perform(self, unused_mock_get_utility):
        self.auth.perform([self.achall])
        validation = self.achall.validation(self.achall.account_key)

        self.mock_client.get_authoritative_zone.assert_called_once_with(f'_acme-challenge.{DOMAIN}')
        self.mock_client.get_txt_rrset.assert_called_once_with(self.mock_zone, "_acme-challenge")
        self.mock_client.set_txt_rrset.assert_called_once_with(self.mock_zone, "_acme-challenge",
                                                               self.TXT | {f'"{validation}"'})

    def test_cleanup(self):
        # _attempt_cleanup | pylint: disable=protected-access
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])

        self.mock_client.get_authoritative_zone.assert_called_once_with(f'_acme-challenge.{DOMAIN}')
        self.mock_client.get_txt_rrset.assert_called_once_with(self.mock_zone, "_acme-challenge")
        self.mock_client.set_txt_rrset.assert_called_once_with(self.mock_zone, "_acme-challenge", self.TXT)


class DesecConfigClientTest(unittest.TestCase):
    record_name = "foo"
    record_content = ["bar"]
    record_ttl = 42

    def setUp(self):
        from certbot_dns_desec.dns_desec import _DesecConfigClient

        self.adapter = requests_mock.Adapter()

        self.client = _DesecConfigClient(FAKE_ENDPOINT, FAKE_TOKEN)
        self.client.session.mount("mock", self.adapter)

    def _register_response(self, url, response=None, requires_token=True, status=200):
        def additional_matcher(request):
            okay = True
            okay &= request.headers["Content-Type"] == "application/json"
            if requires_token:
                okay &= request.headers["Authorization"] == f"Token {FAKE_TOKEN}"
            return okay

        self.adapter.register_uri(
            method=requests_mock.ANY,
            url=url,
            text=json.dumps(response),
            additional_matcher=additional_matcher,
            status_code=status,
        )

    def test_get_authoritative_zone(self):
        self._register_response(
            url=f"{FAKE_ENDPOINT}/domains/?owns_qname=_acme-challenge.{DOMAIN}",
            response=[
                {
                    "created": "2021-06-14T14:30:35.463899Z",
                    "minimum_ttl": 3600,
                    "name": 'name.to.be.extracted',
                    "published": "2021-06-14T14:30:35.772212Z",
                    "touched": "2021-06-14T14:30:35.772212Z"
                }
            ]
        )

        zone = self.client.get_authoritative_zone(f"_acme-challenge.{DOMAIN}")
        self.assertEqual(zone['name'], 'name.to.be.extracted')
        self.assertEqual(zone['minimum_ttl'], 3600)

    def test_set_txt_rrset(self):
        self._register_response(
            url=f"{FAKE_ENDPOINT}/domains/{DOMAIN}/rrsets/",
            response=[
                {
                    "created": "2021-05-13T09:38:41.576975Z",
                    "domain": DOMAIN,
                    "subname": "_acme_challenge",
                    "name": self.record_name,
                    "records": [self.record_content],
                    "ttl": self.record_ttl,
                    "type": "TXT",
                    "touched": "2021-05-13T09:38:41.585257Z"
                }
            ]
        )

        self.client.set_txt_rrset(
            {'name': DOMAIN, 'minimum_ttl': self.record_ttl}, self.record_name, self.record_content
        )

    def test_set_txt_rrset_fail_to_find_domain(self):
        self._register_response(
            url=f"{FAKE_ENDPOINT}/domains/{DOMAIN}/rrsets/",
            response={"detail": "Not found."},
            status=404,
        )
        with self.assertRaises(errors.PluginError):
            self.client.set_txt_rrset(
                {'name': DOMAIN, 'minimum_ttl': self.record_ttl}, self.record_name, self.record_content
            )

    def test_set_txt_rrset_fail_to_authenticate(self):
        self._register_response(
            url=f"{FAKE_ENDPOINT}/domains/{DOMAIN}/rrsets/",
            response={"detail": "Invalid token."},
            status=403,
        )
        with self.assertRaises(errors.PluginError):
            self.client.set_txt_rrset(
                {'name': DOMAIN, 'minimum_ttl': self.record_ttl}, self.record_name, self.record_content
            )

    @patch('time.sleep', return_value=None)
    def test_set_txt_rrset_throttling_retry(self, patched_time_sleep):
        self.adapter.register_uri(
            'PUT',
            f"{FAKE_ENDPOINT}/domains/{DOMAIN}/rrsets/",
            [
                dict(status_code=429, headers={'Retry-After': '2'}),
                dict(status_code=429, headers={'Retry-After': '31'}),
                dict(status_code=200),
            ]
        )
        self.client.set_txt_rrset(
            {'name': DOMAIN, 'minimum_ttl': self.record_ttl}, self.record_name, self.record_content
        )
        self.assertEqual(patched_time_sleep.call_args_list, [mock.call(2), mock.call(31)])

    @patch('time.sleep', return_value=None)
    def test_set_txt_rrset_throttling_retry_fail(self, patched_time_sleep):
        self.adapter.register_uri(
            'PUT',
            f"{FAKE_ENDPOINT}/domains/{DOMAIN}/rrsets/",
            [
                dict(status_code=429, headers={'Retry-After': '2'}),
            ] * 4
        )
        with self.assertRaises(errors.PluginError):
            self.client.set_txt_rrset(
                {'name': DOMAIN, 'minimum_ttl': self.record_ttl}, self.record_name, self.record_content
            )
        self.assertEqual(patched_time_sleep.call_args_list, [mock.call(2)] * 3)

    def test_set_txt_rrset_throttling_no_retry(self):
        self.adapter.register_uri(
            'PUT',
            f"{FAKE_ENDPOINT}/domains/{DOMAIN}/rrsets/",
            [
                dict(status_code=429),  # no Retry-After header
            ]
        )
        with self.assertRaises(errors.PluginError):
            self.client.set_txt_rrset(
                {'name': DOMAIN, 'minimum_ttl': self.record_ttl}, self.record_name, self.record_content
            )
        self.adapter.register_uri(
            'PUT',
            f"{FAKE_ENDPOINT}/domains/{DOMAIN}/rrsets/",
            [
                dict(status_code=429, headers={'Retry-After': 'asdf'}),  # Retry-After header not int
            ]
        )
        with self.assertRaises(errors.PluginError):
            self.client.set_txt_rrset(
                {'name': DOMAIN, 'minimum_ttl': self.record_ttl}, self.record_name, self.record_content
            )


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
