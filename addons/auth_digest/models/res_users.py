import logging
import hashlib
import hmac

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

INDEX_SIZE = 8 # FIXME DRY odoo/addons/base/models/res_users.py


class APIKeys(models.Model):
    _inherit = 'res.users.apikeys'

    def _auth_digest_function(self, algorithm):
        algo, sess, _ = algorithm.partition('-sess')
        return {
            'MD5': lambda data: hashlib.md5(data.encode('utf-8')).hexdigest(),
            'SHA-256': lambda data: hashlib.sha256(data.encode('utf-8')).hexdigest(),
            'SHA-512-256': lambda data: hashlib.sha512(data.encode('utf-8')).hexdigest()[:64],
        }[algo], sess

    def _check_digest_credentials(self, user_id, auth, method, realm):
        self.env.cr.execute('SELECT key FROM res_users_apikeys WHERE user_id = %s AND scope = %s', [user_id, 'digest'])
        for key, in self.env.cr.fetchall():
            # Calculate response for qop=auth
            # https://en.wikipedia.org/wiki/Digest_access_authentication
            # https://tools.ietf.org/html/rfc2617
            digest, sess = self._auth_digest_function(auth['algorithm'])
            ha1 = digest(f"{auth.username}:{realm}:{key}")
            if sess:
                ha1 = digest(f"{ha1}:{auth.nonce}:{auth.cnonce}")
            ha2 = digest(f"{method}:{auth.uri}")
            response = digest(f"{ha1}:{auth.nonce}:{auth.nc}:{auth.cnonce}:{auth.qop}:{ha2}")

            # Compare response in constant time
            if hmac.compare_digest(response, auth.response):
                return user_id

    def _generate(self, scope, name):
        key = super()._generate(scope, name)
        if scope == 'digest':
            # Need actual (unhashed) key to calculate digest response.
            self.env.cr.execute("UPDATE res_users_apikeys SET key = %s WHERE user_id = %s and index = %s", [key, self.env.user.id, key[:INDEX_SIZE]])
        return key
