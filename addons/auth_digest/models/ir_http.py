import logging

from werkzeug.datastructures import WWWAuthenticate
from werkzeug.exceptions import Unauthorized
from werkzeug.http import parse_authorization_header

from odoo import models
from odoo.http import request

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _auth_digest_nonce(cls):
        return request.csrf_token()

    @classmethod
    def _auth_digest_realm(cls):
        return 'digest_token'

    @classmethod
    def _auth_method_digest(cls):
        request.uid = request.session.uid
        if request.uid:
            return

        algorithm = 'MD5'
        qop = ('auth',)
        realm = cls._auth_digest_realm()
        stale = False
        try:
            auth = parse_authorization_header(request.httprequest.headers.get('Authorization'))
            if auth and auth.response and auth.opaque and (auth['algorithm'] == algorithm) and (auth.qop in qop):
                request.session.sid = auth.opaque # HACK: validate_csrf requires request.session.sid be set
                stale = not request.validate_csrf(auth.nonce)
                if not stale:
                    user = request.env['res.users'].search([('login', '=', auth.username)], limit=1)
                    if user.id and request.env['res.users.apikeys']._check_digest_credentials(user.id, auth, request.httprequest.method, realm):
                        request.uid = user.id
                        return
        except Exception as e:
            _logger.error(e)

        www_authenticate = WWWAuthenticate()
        www_authenticate.set_digest(
            algorithm=algorithm,
            nonce=cls._auth_digest_nonce(),
            opaque=request.session.sid,
            qop=qop,
            realm=realm,
            stale=stale)
        raise Unauthorized(www_authenticate=www_authenticate)
