import logging

from werkzeug.datastructures import WWWAuthenticate
from werkzeug.exceptions import Unauthorized
from werkzeug.http import parse_authorization_header

from odoo import models, registry
from odoo.api import Environment
from odoo.exceptions import AccessDenied
from odoo.http import request

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _auth_basic_realm(cls):
        return 'basic_token'

    @classmethod
    def _auth_method_basic(cls):
        try:
            auth = parse_authorization_header(request.httprequest.headers.get('Authorization'))
            if auth and auth.type == 'basic':
                if cls.authenticate_basic_token(auth['username'], auth['password']):
                    return
        except Exception as e:
            _logger.error(e)

        www_authenticate = WWWAuthenticate()
        www_authenticate.set_basic(realm=cls._auth_basic_realm())
        raise Unauthorized(www_authenticate=www_authenticate)

    @classmethod
    def _auth_method_basic_token(cls):
        login = request.httprequest.args.get('login')
        basic_token = request.httprequest.args.get('basic_token')
        if cls.authenticate_basic_token(login, basic_token):
            return

        raise AccessDenied()

    @classmethod
    def _auth_method_basic_url(cls):
        _, args = cls._match(request.httprequest.path)
        login = args.get('login')
        basic_token = args.get('basic_token')
        if cls.authenticate_basic_token(login, basic_token):
            return

        raise AccessDenied()

    @classmethod
    def authenticate_basic_token(cls, login, basic_token):
        if login and basic_token:
            User = request.env['res.users']
            domain = User._get_login_domain(login)
            user = User.search(domain, limit=1)
            if user.id and request.env['res.users.apikeys']._check_credentials(scope='basic', key=basic_token) == user.id:
                request.uid = user.id
                return request.uid
