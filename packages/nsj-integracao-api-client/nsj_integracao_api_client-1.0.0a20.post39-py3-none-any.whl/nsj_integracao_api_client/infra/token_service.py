
import base64

from nsj_gcf_utils.json_util import json_loads

class TokenService:

    def decode_token(self, token):
        data = token.split('.')[1]
        padding = '=' * (4 - len(data) % 4)
        str_token = base64.b64decode(data + padding).decode('utf-8')
        return  json_loads(str_token)
