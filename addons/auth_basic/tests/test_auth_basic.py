import logging

from requests.auth import HTTPBasicAuth
from werkzeug.http import parse_www_authenticate_header

from odoo.http import Controller, request, route
from odoo.tests import HttpCase, tagged
from odoo.tools import config

HOST = '127.0.0.1'

_logger = logging.getLogger(__name__)


class TestAuthBasicController(Controller):
    @route('/test_auth_basic', type='http', auth='basic')
    def route_auth_basic(self):
        return request.make_response('OK')


class TestAuthBasic(HttpCase):
    def setUp(self):
        super().setUp()
        self.opener.cookies.pop('session_id', None) # real clients do not start with a session
        self.env.user = self.user = self.env.ref('base.user_admin')

    def test_success(self):
        basic_token = self.env['res.users.apikeys']._generate('basic', 'HTTP Basic')
        response = self.url_open('/test_auth_basic', auth=HTTPBasicAuth(self.user.login, basic_token))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, 'OK')

    def test_unset(self):
        response = self.url_open('/test_auth_basic')
        self.assertEqual(response.status_code, 401)
        www_authenticate = parse_www_authenticate_header(response.headers['WWW-Authenticate'])
        self.assertEqual(www_authenticate.type, 'basic')

    def test_unauthorized(self):
        self.env['res.users.apikeys']._generate('basic', 'HTTP Basic')
        response = self.url_open('/test_auth_basic')
        self.assertEqual(response.status_code, 401)
        www_authenticate = parse_www_authenticate_header(response.headers['WWW-Authenticate'])
        self.assertEqual(www_authenticate.type, 'basic')
