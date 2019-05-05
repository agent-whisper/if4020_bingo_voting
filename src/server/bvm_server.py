#TODO: Authorization for some request
import json
import yaml

from src.bingovoting.machines import PedersenBVM
import flask

server = flask.Flask(__name__)

OK = 200
ACCEPTED = 202
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
NOT_ACCEPTABLE = 406

try:
    with open('src/server/config.yml', 'r') as stream:
        config = yaml.safe_load(stream)
except FileNotFoundError:
    server.logger.error('[server.py] Config file not found')
    exit()

bvm_machine = PedersenBVM(config['bvm'])

@server.route('/')
def index():
    return 'It works!'

@server.route('/status')
def ping():
    return json.dumps({
        'status': OK,
        'description': 'BVM server is running',
    })

@server.route('/candidates/labels/')
def get_candidate_labels():
    data = bvm_machine.get_candidate_labels()
    return json.dumps({
        'data': data,
        'count': len(data),
        'status': OK
    })

@server.route('/candidates/dummy_votes/')
def get_all_unused_candidate_dummy_votes():
    response = bvm_machine.get_all_dummy_votes()
    return json.dumps({
        'data': response,
        'status': OK,
    })

@server.route('/candidates/dummy_votes/<string:status>')
def get_all_candidate_dummy_votes(status):
    response = bvm_machine.get_all_dummy_votes(status)
    return json.dumps({
        'data': response,
        'status': OK,
    })

@server.route('/candidates/commitments/')
def get_all_unused_candidate_commitments():
    response = bvm_machine.get_all_candidate_commitments()
    return json.dumps({
        'data': response,
        'status': OK,
    })

@server.route('/candidates/<string:label>/')
def get_candidate_data(label):
    try:
        data = bvm_machine.get_candidate_data(label)
    except ValueError as e:
        return json.dumps({
            'status': NOT_FOUND,
            'description': str(e)
        })
    return json.dumps({
        'label': label,
        'data': data,
        'status': OK,
    })

@server.route('/candidates/<string:label>/dummy_votes/')
def get_unused_candidate_dummy_votes(label):
    try:
        data = bvm_machine.get_candidate_dummy_votes(label)
    except ValueError as e:
        return json.dumps({
            'status': NOT_FOUND,
            'description': str(e),
        })
    return json.dumps({
        'label': label,
        'data': data,
        'count': len(data),
        'status': OK,
    })

@server.route('/candidates/<string:label>/dummy_votes/<string:status>')
def get_candidate_dummy_votes(label, status):
    try:
        data = bvm_machine.get_candidate_dummy_vote(label, status)
    except ValueError as e:
        return json.dumps({
            'status': NOT_FOUND,
            'description': str(e),
        })
    return json.dumps({
        'label': label.upper(),
        'data': data,
        'count': len(data),
        'status': OK,
    })

@server.route('/candidates/<string:label>/dummy_commitments/')
def get_all_candidate_commitments(label):
    try:
        data = bvm_machine.get_candidate_commitments(label)
    except ValueError as e:
        return json.dumps({
            'status': NOT_FOUND,
            'description': str(e),
        })
    return json.dumps({
        'label': label.upper(),
        'data': data,
        'count': len(data),
        'status': OK,
    })

@server.route('/candidates/<string:label>/commitments/<string:status>')
def get_used_candidate_commitments(label, status):
    try:
        data = bvm_machine.get_candidate_commitments(label, status)
    except ValueError as e:
        return json.dumps({
            'status': NOT_FOUND,
            'description': str(e)
        })
    return json.dumps({
        'label': label,
        'data': data,
        'count': len(data),
        'status': OK,
    })

@server.route('/fresh_votes/')
def get_fresh_votes():
    data = bvm_machine.get_fresh_votes()
    return json.dumps({
        'data': data,
        'count': len(data),
        'status': OK,
    })

@server.route('/fresh_votes/commitments/')
def get_fresh_votes_commitments():
    data = bvm_machine.get_fresh_votes_commitments()
    return json.dumps({
        'data': data,
        'count': len(data),
        'status': OK,
    })

@server.route('/vote/collect', methods=['POST'])
def vote():
    picked_candidate = flask.request.form['pick']
    try:
        vote_response = bvm_machine.vote(picked_candidate)
    except ValueError as e:
        return json.dumps({
            'status': NOT_FOUND,
            'description': str(e),
        })
    return json.dumps({
        'data': vote_response,
        'status': OK,
    })

@server.route('/vote/verify', methods=['POST'])
def verify_vote():
    try:
        m = int(flask.request.form['vote'])
        c = int(flask.request.form['commitment'])
        r = int(flask.request.form['r'])
        verify_result = bvm_machine.verify_vote(c, m, r)
    except KeyError as e:
        return json.dumps({
            'status': BAD_REQUEST,
            'description': 'Bad post request: ' + str(e),
        })
    except TypeError as e:
        return json.dumps({
            'status': BAD_REQUEST,
            'description': 'Bad post request: ' + str(e),
        })
    return json.dumps({
        'data': verify_result,
        'status': OK,
    })

@server.route('/ballots/')
def get_ballots():
    data = bvm_machine.get_ballots()
    return json.dumps({
        'data': data,
        'count': len(data),
        'status': OK,
    })

@server.route('/poll/')
@server.route('/poll/result/')
def get_poll_result():
    data = bvm_machine.get_poll_result()
    vote_collected, registered_voter = bvm_machine.get_vote_count()
    return json.dumps({
        'data': data,
        'received_vote_count': vote_collected,
        'registered_voter_count': registered_voter,
        'status': OK,
    })