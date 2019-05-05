import json
import yaml

import flask
from src.bingovoting.booths import PedersenBooth

OK = 200
ACCEPTED = 202
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
NOT_ACCEPTABLE = 406

booth_client = flask.Flask(__name__)
try:
    with open('src/client/booth_config.yml', 'r') as stream:
        config = yaml.safe_load(stream)
except FileNotFoundError:
    booth_client.logger.error('[client.py] Config file not found')
    exit()
bvm_booth = PedersenBooth(config)

@booth_client.route('/')
def index():
    return flask.render_template('booth/index.html', vote_form_uri=flask.url_for('open_vote_form'))

@booth_client.route('/vote/form/')
def open_vote_form():
    candidate_labels = bvm_booth.get_candidate_labels()
    return flask.render_template(
        'booth/vote_form.html', 
        send_vote_uri=flask.url_for('send_vote'),
        candidate_labels=candidate_labels,
    )

@booth_client.route('/vote/form/send', methods=['POST'])
def send_vote():
    response = bvm_booth.send_vote(flask.request.form['pick'])
    ballot_data = response['data']['ballot']
    ballot_id = response['data']['id']
    accepted = response['data']['accepted']
    return flask.render_template(
        'booth/ballot.html',
        home_uri=flask.url_for('index'),
        accepted=accepted,
        ballot_data=ballot_data,
        id=ballot_id,
    )