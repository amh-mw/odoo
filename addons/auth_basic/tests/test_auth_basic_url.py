import logging

from werkzeug.http import parse_www_authenticate_header

from odoo.http import Controller, request, route
from odoo.tests import HttpCase, tagged
from odoo.tools import config

HOST = '127.0.0.1'

_logger = logging.getLogger(__name__)


class TestAuthBasicUrlController(Controller):
    @route('/test_auth_basic_url/<login>/<basic_token>', type='http', auth='basic_url')
    def route_auth_basic_url(self, login, basic_token):
        return request.make_response('OK')


class TestAuthBasicUrl(HttpCase):
    def setUp(self):
        super().setUp()
        self.opener.cookies.pop('session_id', None) # real clients do not start with a session
        self.env.user = self.user = self.env.ref('base.user_admin')
        self.basic_token = self.env['res.users.apikeys']._generate('basic', 'HTTP Basic')

    def test_success(self):
        response = self.url_open(f"/test_auth_basic_url/{self.user.login}/{self.basic_token}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, 'OK')

    def test_bogus_login(self):
        response = self.url_open(f"/test_auth_basic_url/bogus/{self.basic_token}")
        self.assertEqual(response.status_code, 403)
        self.assertNotIn('WWW-Authenticate', response.headers)

    def test_bogus_basic_token(self):
        response = self.url_open(f"/test_auth_basic_url/{self.user.login}/bogus")
        self.assertEqual(response.status_code, 403)
        self.assertNotIn('WWW-Authenticate', response.headers)
