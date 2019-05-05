import requests
from requests.exceptions import ConnectionError

class PedersenBooth:
    CANDIDATE_LABEL_URI = '/candidates/labels'
    SEND_VOTE = '/vote/collect'

    def __init__(self, config):
        self.bvm_server_config = {
            'protocol': ('https' if config['protocol']=='https' else 'http'),
            'ip': config['server_ip'],
            'port': config['server_port'],
        }
        try:
            self.candidate_labels = self._init_candidate_labels()
        except ConnectionError:
            raise ConnectionError('Cannot connect to server at', self._bvm_uri())

    def get_candidate_labels(self):
        return self.candidate_labels

    def send_vote(self, picked_candidate):
        encrypted_vote = picked_candidate
        data = {'pick': encrypted_vote}
        response = requests.post(self._bvm_uri(self.SEND_VOTE), data)
        return response.json()

    def _bvm_uri(self, uri_type=''):
        protocol = self.bvm_server_config['protocol']
        ip = self.bvm_server_config['ip']
        port = self.bvm_server_config['port']
        return '{}://{}:{}{}'.format(protocol, ip, port, uri_type)

    def _init_candidate_labels(self):
        response = requests.get(self._bvm_uri(self.CANDIDATE_LABEL_URI))
        return response.json()['data']
