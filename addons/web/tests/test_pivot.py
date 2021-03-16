# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging

from odoo.http import content_disposition, WebRequest
from odoo.tests import HttpCase


class TestPivot(HttpCase):
    def setUp(self):
        super().setUp()
        self.data = {
            'csrf_token': WebRequest.csrf_token(self),
            'data': json.dumps({
                'col_group_headers': [],
                'measure_count': 0,
                'measure_headers': [],
                'origin_count': 0,
                'origin_headers': [],
                'rows': [],
                'title': 'dummy',
            }),
            'token': 'dummy',
        }

    def test_export_xls(self):
        self.authenticate('admin', 'admin')
        response = self.url_open('/web/pivot/export_xls', data=self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Disposition'], content_disposition('dummy.xls'))
