from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit
from wsgiref.util import setup_testing_defaults

from django.test import TransactionTestCase, override_settings

from config import wsgi


@override_settings(
    ALLOWED_HOSTS=["cms.example"],
    DEBUG_PROPAGATE_EXCEPTIONS=True,
    OIDC_OP_AUTHORIZATION_ENDPOINT="https://proconnect.example/authorize",
    OIDC_RP_CLIENT_ID="test-client",
)
@patch("config.wsgi.CLEVER_PROXY_IPS", {"192.0.2.9"})
class ProConnectProxySchemeTestCase(TransactionTestCase):
    def redirect_uri(self, remote_addr, **headers):
        environ = {
            "HTTP_HOST": "cms.example",
            "PATH_INFO": "/oidc/authenticate/",
            "REMOTE_ADDR": remote_addr,
            **headers,
        }
        setup_testing_defaults(environ)
        start_response = Mock()
        with patch("sites_conformes.core.middleware.CmsDsfrConfig.for_request") as site_config:
            site_config.return_value.iframe_allow_origins = ""
            response = wsgi.application(environ, start_response)
            response.close()
        status, response_headers = start_response.call_args.args
        self.assertEqual(status, "302 Found")
        location = dict(response_headers)["Location"]
        return parse_qs(urlsplit(location).query)["redirect_uri"][0]

    def test_uses_the_protocol_appended_by_the_clever_cloud_proxy(self):
        redirect_uri = self.redirect_uri(
            "192.0.2.9",
            HTTP_FORWARDED='proto=http, Proto="HTTPS";for="203.0.113.5:62560";by=192.0.2.9',
            HTTP_X_FORWARDED_PROTO="http",
        )
        self.assertEqual(redirect_uri, "https://cms.example/oidc/callback/")

    def test_preserves_http_when_the_proxy_reports_http(self):
        redirect_uri = self.redirect_uri("192.0.2.9", HTTP_FORWARDED="proto=https, proto=http;by=192.0.2.9")
        self.assertEqual(redirect_uri, "http://cms.example/oidc/callback/")

    def test_ignores_forwarded_headers_from_other_peers(self):
        redirect_uri = self.redirect_uri("203.0.113.5", HTTP_FORWARDED="proto=https", HTTP_X_FORWARDED_PROTO="https")
        self.assertEqual(redirect_uri, "http://cms.example/oidc/callback/")

    def test_ignores_x_forwarded_proto_without_a_forwarded_protocol(self):
        redirect_uri = self.redirect_uri(
            "192.0.2.9", HTTP_FORWARDED="proto=https, by=192.0.2.9", HTTP_X_FORWARDED_PROTO="https"
        )
        self.assertEqual(redirect_uri, "http://cms.example/oidc/callback/")
