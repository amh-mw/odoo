import logging

from werkzeug.http import parse_www_authenticate_header

from odoo.http import Controller, request, route
from odoo.tests import HttpCase, tagged
from odoo.tools import config

HOST = '127.0.0.1'

_logger = logging.getLogger(__name__)


class TestAuthBasicTokenController(Controller):
    @route('/test_auth_basic_token', type='http', auth='basic_token')
    def route_auth_basic_token(self, login, basic_token):
        return request.make_response('OK')


class TestAuthBasicToken(HttpCase):
    def setUp(self):
        super().setUp()
        self.opener.cookies.pop('session_id', None) # real clients do not start with a session
        self.env.user = self.user = self.env.ref('base.user_admin')
        self.basic_token = self.env['res.users.apikeys']._generate('basic', 'HTTP Basic')

    def test_success(self):
        response = self.url_open('/test_auth_basic_token', params={'login': self.user.login, 'basic_token': self.basic_token})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, 'OK')

    def test_bogus_login(self):
        response = self.url_open('/test_auth_basic_token', params={'login': 'bogus', 'basic_token': self.basic_token})
        self.assertEqual(response.status_code, 403)
        self.assertNotIn('WWW-Authenticate', response.headers)

    def test_bogus_basic_token(self):
        response = self.url_open('/test_auth_basic_token', params={'login': self.user.login, 'basic_token': 'bogus'})
        self.assertEqual(response.status_code, 403)
        self.assertNotIn('WWW-Authenticate', response.headers)
