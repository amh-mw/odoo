import logging

import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from werkzeug.http import parse_www_authenticate_header
import vobject

from odoo.tests import HttpCase, tagged
from odoo.tools import config

HOST = '127.0.0.1'

_logger = logging.getLogger(__name__)


class TestCalendarICS(HttpCase):
    def setUp(self):
        super().setUp()
        self.opener.cookies.pop('session_id', None) # external consumers do not start with a session id
        self.env.user = self.user = self.env.ref('base.user_admin')
        self.basic_token = self.env['res.users.apikeys']._generate('basic', 'HTTP Basic')
        self.digest_token = self.env['res.users.apikeys']._generate('digest', 'HTTP Digest')

    def test_private_success(self):
        response = self.url_open('/calendar/ical.ics', auth=HTTPDigestAuth(self.user.login, self.digest_token))
        self.assertEqual(response.status_code, 200)
        self.assertRegex(response.text, r'^BEGIN:VCALENDAR')
        vcalendar = vobject.readOne(response.text)
        self.assertEqual('VCALENDAR', vcalendar.name)
        vevents = list(vcalendar.components())
        self.assertEqual(3, len(vevents))
        self.assertEqual(vevents[0].summary.value, "Changes in Designing")
        self.assertEqual(vevents[1].summary.value, "Pricing Discussion")
        self.assertEqual(vevents[2].summary.value, "Follow-up for Project proposal")

    def test_private_unauthorized(self):
        response = self.url_open('/calendar/ical.ics')
        self.assertEqual(response.status_code, 401)
        www_authenticate = parse_www_authenticate_header(response.headers['WWW-Authenticate'])
        self.assertEqual(www_authenticate.type, 'digest')

    def test_private_unacceptable(self):
        response = self.url_open('/calendar/ical.ics', auth=HTTPDigestAuth(self.user.login, self.digest_token), headers={'Accept': 'image/jpeg'})
        self.assertEqual(response.status_code, 406)

    def test_public_success(self):
        response = self.url_open(f"/calendar/ical/{self.user.login}/{self.basic_token}/public.ics")
        self.assertEqual(response.status_code, 200)
        self.assertRegex(response.text, r'^BEGIN:VCALENDAR')

    def test_public_forbidden(self):
        response = self.url_open(f"/calendar/ical/{self.user.login}/bogus/public.ics")
        self.assertEqual(response.status_code, 403)
        self.assertNotIn('WWW-Authenticate', response.headers)

    def test_public_unacceptable(self):
        response = self.url_open(f"/calendar/ical/{self.user.login}/{self.basic_token}/public.ics", headers={'Accept': 'image/jpeg'})
        self.assertEqual(response.status_code, 406)
        self.assertNotIn('WWW-Authenticate', response.headers)
