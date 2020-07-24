import logging

import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from werkzeug.http import parse_www_authenticate_header

from odoo import models, fields
from odoo.http import Controller, request, route
from odoo.tests import HttpCase, tagged
from odoo.tools import config

HOST = '127.0.0.1'

_logger = logging.getLogger(__name__)


class TestAuthDigestController(Controller):
    @route('/test_auth_digest', type='http', auth='digest')
    def route_auth_digest(self):
        return request.make_response('OK')


class TestAuthDigest(HttpCase):
    def setUp(self):
        super().setUp()
        self.opener.cookies.pop('session_id', None) # real clients do not start with a session
        self.env.user = self.env.ref('base.user_admin')

    def test_success(self):
        digest_token = self.env['res.users.apikeys']._generate('digest', 'HTTP Digest')
        response = self.url_open('/test_auth_digest', auth=HTTPDigestAuth(self.env.user.login, digest_token))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, 'OK')
        self.assertIn('Set-Cookie', response.headers)

    def test_unset(self):
        response = self.url_open('/test_auth_digest')
        self.assertEqual(response.status_code, 401)
        www_authenticate = parse_www_authenticate_header(response.headers['WWW-Authenticate'])
        self.assertEqual(www_authenticate.type, 'digest')

    def test_unauthorized(self):
        self.env['res.users.apikeys']._generate('digest', 'HTTP Digest')
        response = self.url_open('/test_auth_digest')
        self.assertEqual(response.status_code, 401)
        www_authenticate = parse_www_authenticate_header(response.headers['WWW-Authenticate'])
        self.assertEqual(www_authenticate.type, 'digest')
