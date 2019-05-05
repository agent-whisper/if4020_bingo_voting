import json
import yaml

import flask
from src.bingovoting.boards import PedersenBoard

OK = 200
ACCEPTED = 202
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
NOT_ACCEPTABLE = 406

board_client = flask.Flask(__name__)
try:
    with open('src/client/board_config.yml', 'r') as stream:
        config = yaml.safe_load(stream)
except FileNotFoundError:
    board_client.logger.error('[client.py] Config file not found')
    exit()
bvm_board = PedersenBoard(config)

@board_client.route('/')
def index():
    return flask.render_template(
        'board/index.html',
        pre_voting_uri=flask.url_for('publish_dummy_commitments'),
        voting_phase_uri=flask.url_for('show_current_board'),
        result_uri=flask.url_for('show_result'),
    )

@board_client.route('/board/pre-voting/')
def publish_dummy_commitments():
    candidate_data = bvm_board.get_all_dummy_commitments()
    return flask.render_template(
        'board/pre_voting.html',
        candidate_data=candidate_data['data'],
        home_uri=flask.url_for('index'),
    )

@board_client.route('/board/voting_phase/')
def show_current_board():
    ballots = bvm_board.get_ballots()
    return flask.render_template(
        'board/current_ballots.html',
        ballot_list=ballots['data'],
        home_uri=flask.url_for('index'),
        refresh_uri=flask.url_for('show_current_board'),
    )

@board_client.route('/board/result/')
def show_result():
    poll_result = bvm_board.get_poll_result()
    unused_dummy_votes = bvm_board.publish_unused_dummy_votes()
    return flask.render_template(
        'board/poll_result.html',
        received_votes_count=poll_result['received_vote_count'],
        registered_votes_count=poll_result['registered_voter_count'],
        poll_data=poll_result['data'],
        unused_dummy_vote=unused_dummy_votes['data'],
        home_uri=flask.url_for('index'),
        refresh_uri=flask.url_for('show_result'),
    )