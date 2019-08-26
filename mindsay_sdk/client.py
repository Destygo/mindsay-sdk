import getpass
import logging
from typing import Any, Dict, List

import requests

logger = logging.getLogger('mindsay')

SUPPORTED_LANGUAGES = ('fr_FR', 'en_EN', 'es_ES', 'it_IT', 'de_DE', 'nl_NL')


class Client(requests.Session):

    def __init__(self, email: str, production: bool = False):
        super().__init__()

        if production:
            logger.warning('Connecting to Mindsay production...')
            self.base_url = 'https://bos.destygo.com/'
        else:
            logger.warning('Connecting to Mindsay staging... '
                           'Remember to connect to the Mindsay WiFi or set up a SSH tunnel!')
            self.base_url = 'https://staging-bos.destygo.com/'

        self._user_sign_in(email)

    def _user_sign_in(self, email: str):
        password = getpass.getpass(prompt='Password: ')
        response = self.post('users/sign_in', json={'user': {'email': email, 'password': password}})
        response.raise_for_status()
        self.headers['Authorization'] = response.headers['Authorization']
        if response.json()['otp_required_for_login']:
            self._user_code_auth(email)

    def _user_code_auth(self, email: str):
        otp_attempt = getpass.getpass(prompt='Email code: ')
        response = self.post('users/code_auth', json={'user': {'email': email, 'otp_attempt': otp_attempt}})
        response.raise_for_status()
        self.cookies = response.cookies

    def get_current_environment(self) -> dict:
        response = self.get('environment/base')
        response.raise_for_status()
        return response.json()

    def set_current_bot(self, bot_id: int):
        response = self.post('environment/set_current_bot', json={'bot_id': bot_id})
        response.raise_for_status()

    def set_current_instance(self, instance_id: int):
        """Set the instance for next operations"""
        response = self.post('environment/set_current_instance', json={'instance_id': instance_id})
        # NOTE: BOS returns a status code 200 when instance_id does not exist and an HTML error
        response.raise_for_status()
        logger.info('Switched to instance %s', response.json()['current_instance']['name'])

    def set_current_experiment(self, experiment_id: int):
        response = self.post('environment/set_current_experiment', json={'experiment_id': experiment_id})
        response.raise_for_status()

    def set_current_language(self, language: str):
        if language not in SUPPORTED_LANGUAGES:
            logger.error('Invalid language %s. Supported languages: %s', language, SUPPORTED_LANGUAGES)
        return self.post('environment/change_language', json={'language': language})

    def instances(self) -> List[Dict[str, Any]]:
        """Returns all instances"""
        # TODO: How to list only my instances ?
        response = self.get('/instances')
        response.raise_for_status()
        return response.json()

    def bots(self) -> List[Dict[str, Any]]:
        """Returns all bots"""
        # TODO: How to list bots only on current instance ?
        response = self.get('/bots')
        response.raise_for_status()
        return response.json()

    def experiments(self) -> List[Dict[str, Any]]:
        """Returns all experiments"""
        response = self.get('/experiments')
        response.raise_for_status()
        return response.json()

    def get(self, url, **kwargs):
        return super().get(self.base_url + url, **kwargs)

    def put(self, url, **kwargs):
        return super().put(self.base_url + url, **kwargs)

    def post(self, url, **kwargs):
        return super().post(self.base_url + url, **kwargs)

    def delete(self, url, **kwargs):
        return super().delete(self.base_url + url, **kwargs)
