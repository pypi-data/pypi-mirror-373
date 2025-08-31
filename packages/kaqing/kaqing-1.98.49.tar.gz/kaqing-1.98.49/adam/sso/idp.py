import base64
import getpass
import os
import traceback
import requests
from kubernetes import config
import yaml

from adam.k8s_utils.secrets import Secrets

from .cred_cache import CredCache
from .idp_session import IdpSession
from .idp_login import IdpLogin
from adam.config import Config
from adam.utils import log, log2

class Idp:
    ctrl_c_entered = False

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Idp, cls).__new__(cls)

        return cls.instance

    def login(app_host: str, username: str = None, idp_uri: str = None, forced = False, use_token_from_env = True, use_cached_creds = True) -> IdpLogin:
        session: IdpSession = IdpSession.create(username, app_host, app_host, idp_uri=idp_uri)

        if use_token_from_env:
            if l0 := session.login_from_env_var():
                return l0
        if port := os.getenv("SERVER_PORT"):
            token_server = Config().get('app.login.token-server-url', 'http://localhost:{port}').replace('{port}', port)
            res: requests.Response = requests.get(token_server)
            if res.status_code == 200 and res.text:
                return session.login_from_token(res.text)

        r: IdpLogin = None
        try:
            if username:
                log(f'{session.idp_host()} login: {username}')

            while not username or Idp.ctrl_c_entered:
                if Idp.ctrl_c_entered:
                    Idp.ctrl_c_entered = False

                default_user: str = None
                if use_cached_creds:
                    default_user = CredCache().get_username()
                    log2(f'User read from cache: {default_user}')

                if from_env := os.getenv('USERNAME'):
                    default_user = from_env
                if default_user and default_user != username:
                    session = IdpSession.create(default_user, app_host, app_host)

                    if forced:
                        username = default_user
                    else:
                        username = input(f'{session.idp_host()} login(default {default_user}): ') or default_user
                else:
                    username = input(f'{session.idp_host()} login: ')

            session2: IdpSession = IdpSession.create(username, app_host, app_host)
            if session.idp_host() != session2.idp_host():
                session = session2

                log(f'Switching to {session.idp_host()}...')
                log()
                log(f'{session.idp_host()} login: {username}')

            password = None
            while password == None or Idp.ctrl_c_entered: # exit the while loop even if password is empty string
                if Idp.ctrl_c_entered:
                    Idp.ctrl_c_entered = False

                default_pass = CredCache().get_password() if use_cached_creds else None
                if default_pass:
                    if forced:
                        password = default_pass
                    else:
                        password = getpass.getpass(f'Password(default ********): ') or default_pass
                else:
                    password = getpass.getpass(f'Password: ')

            if username and password:
                try:
                    kubeconfig_string = base64.b64decode(password.encode('ascii')).decode('utf-8')
                    if kubeconfig_string.startswith('apiVersion: '):
                        kubeconfig_dict = yaml.safe_load(kubeconfig_string)
                        config.kube_config.load_kube_config_from_dict(kubeconfig_dict)
                        log2('Kubectl file loaded')
                        Secrets.list_secrets(os.getenv('NAMESPACE'))

                        # if listing secrets does not fail, the kubeconfig string is good
                        log2('Accepted kubeconfig file as password.')
                        r = IdpLogin(None, None, None, username)
                        log(f"You're signed in as {username}")

                        return r
                except:
                    log2(traceback.format_exc)
                    pass

                r = session.authenticator.authenticate(session.idp_uri, app_host, username, password)
                if r:
                    log(f"You're signed in as {username}")

                return r
        finally:
            if r and Config().get('app.login.cache-creds', True):
                CredCache().cache(username, password)
            elif username and Config().get('app.login.cache-username', True):
                CredCache().cache(username)

        return None