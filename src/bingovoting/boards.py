import requests
from requests.exceptions import ConnectionError

class PedersenBoard:
    PING_URI = '/status'
    POLL_RESULT_URI = '/poll/result/'
    FRESH_COMMITMENTS_URI = '/fresh_votes/commitments/'
    UNUSED_DUMMY_VOTES_URI = '/candidates/dummy_votes/'
    UNUSED_DUMMY_COMMITMENTS_URI = '/candidates/commitments/'
    BALLOTS_URI = '/ballots/'

    def __init__(self, config):
        self.config = {
            'ip': config['client_ip'],
            'port': config['client_port'],
            'protocol': ('https' if config['client_protocol']=='https' else 'http'),
        }
        self.bvm_server_config = {
            'protocol': ('https' if config['server_protocol']=='https' else 'http'),
            'ip': config['server_ip'],
            'port': config['server_port'],
        }
        try:
            requests.get(self._bvm_uri(self.PING_URI))
        except ConnectionError:
            raise ConnectionError('[BVM Board] Cannot connect to bvm server at', self._bvm_uri())
    
    def get_poll_result(self):
        response = requests.get(self._bvm_uri(self.POLL_RESULT_URI))
        return response.json()

    def get_fresh_commitments(self):
        response = requests.get(self._bvm_uri(self.FRESH_COMMITMENTS_URI))
        return response.json()

    def get_all_unused_dummy_votes(self):
        response = requests.get(self._bvm_uri(self.UNUSED_DUMMY_VOTES_URI))
        return response.json()

    def get_all_unused_commitments(self):
        response = requests.get(self._bvm_uri(self.UNUSED_DUMMY_COMMITMENTS_URI))
        return response.json()

    def get_ballots(self):
        response = requests.get(self._bvm_uri(self.BALLOTS_URI))
        return response.json()

    def get_own_uri(self):
        protocol = self.config['protocol']
        ip = self.config['ip']
        port = self.config['port']
        return '{}://{}:{}'.format(protocol, ip, port)

    def _bvm_uri(self, uri_type=''):
        protocol = self.bvm_server_config['protocol']
        ip = self.bvm_server_config['ip']
        port = self.bvm_server_config['port']
        return '{}://{}:{}{}'.format(protocol, ip, port, uri_type)