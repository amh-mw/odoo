import logging

from werkzeug.datastructures import MIMEAccept
from werkzeug.exceptions import NotAcceptable
from werkzeug.http import parse_accept_header

from odoo.http import content_disposition, Controller, request, route

_logger = logging.getLogger(__name__)


class CalendarController(Controller):
    @route('/calendar/ical/<string:login>/<string:basic_token>/public.ics', type='http', auth='basic_url')
    def calendar_ical(self, login, basic_token):
        return self._calendar_ics()

    @route('/calendar/ical.ics', type='http', auth='digest')
    def calendar_ics(self):
        return self._calendar_ics()

    def _calendar_ics(self):
        accept = parse_accept_header(request.httprequest.headers.get('Accept'), MIMEAccept)
        if accept and not accept.best_match(['text/calendar']):
            raise NotAcceptable()

        domain = [('user_id', '=', request.uid)] # FIXME: Match user.partner_id instead
        data = request.env['calendar.event'].with_user(request.uid).search(domain).ics()
        headers = [
            ('Content-Disposition', content_disposition('calendar.ics')),
            ('Content-Length', len(data)),
            ('Content-Type', 'text/calendar'),
        ]
        return request.make_response(data, headers)
