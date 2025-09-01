import requests
import webbrowser
import time

from pydantic import BaseModel
from typing import Optional
from urllib.parse import urljoin

from novara.config import config, ConfigManager, Token

from requests.exceptions import JSONDecodeError

class DeviceCodeResponse(BaseModel):
    device_code: str
    verification_uri: str
    verification_uri_complete: str
    user_code: str
    expires_in: int
    interval: int
    
class UserinfoModel(BaseModel):
    sub:str
    email:str
    email_verified:bool
    name:str
    given_name:str
    preferred_username:str
    nickname:str
    groups:list[str]

class AuthSession(requests.Session):
    userinfo: Optional[UserinfoModel] = None

    def __init__(self, config:ConfigManager):
        self.config = config
        super().__init__()

    def _request_token(self, from_user_info:bool = False) -> Optional[Token]:
        if self.config.token.is_valid() and not from_user_info and self.get_userinfo():
            return 

        if not self.config.idp_url or not self.config.client_id:
            raise Exception("IDP URL or Client ID not set in configuration")

        device_code_resp = requests.post(
            urljoin(self.config.idp_url, '/application/o/device/'),
            data={'client_id': self.config.client_id, 'scope': 'openid profile email'}, 
            allow_redirects=True
        )
        device_code_resp.raise_for_status()

        device_code = DeviceCodeResponse.model_validate(device_code_resp.json())

        print(f'Please visit {device_code.verification_uri} and enter code {device_code.user_code} or {device_code.verification_uri_complete}')
        webbrowser.open(device_code.verification_uri_complete)

        poll_count = device_code.expires_in // device_code.interval

        for _ in range(poll_count):
            token_resp = requests.post(
                urljoin(self.config.idp_url, '/application/o/token/'),
                data={
                    'client_id': self.config.client_id,
                    'device_code': device_code.device_code,
                    'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
                }
            )

            if token_resp.status_code == 400 and token_resp.json().get('error') == 'authorization_pending':
                time.sleep(device_code.interval)
                continue

            token_resp.raise_for_status()
            self.config.token = Token.model_validate(token_resp.json())
            self.config.save()
            break
        else:
            print('Authentication expired please try again')
            exit()

        if not self.get_userinfo():
            raise Exception("failed to retreive valide userinfo")

        return self.config.token
        
    def get_userinfo(self) -> Optional[UserinfoModel]:
        if not self.config.token.is_valid():
            self._request_token(from_user_info=True)
        
        resp = requests.get(
            urljoin(self.config.idp_url, '/application/o/userinfo/'), 
            headers={
                'Authorization': f'{self.config.token.token_type} {self.config.token.access_token}'
            }
        )
        
        if not resp.ok:
            return None
        
        self.userinfo = UserinfoModel.model_validate(resp.json())

        return self.userinfo
    
    def request(self, method, url:str, params = None, data = None, headers:Optional[dict[str, str]] = None, cookies = None, files = None, auth = None, timeout = None, allow_redirects = True, proxies = None, hooks = None, stream = None, verify = None, cert = None, json = None):
        if not self.config.token.is_valid():
            self._request_token()

        headers = (headers or {}) | {'Authorization': f'{self.config.token.token_type} {self.config.token.access_token}'}

        if not url.startswith(('http://', 'https://')):
            url = urljoin(self.config.server_url, url)
        
        return super().request(method, url, params, data, headers, cookies, files, auth, timeout, allow_redirects, proxies, hooks, stream, verify, cert, json)


request = AuthSession(config)