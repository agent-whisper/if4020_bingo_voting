from Crypto.Util import number
import random

from src.cryptography.pedersen import Pedersen

class PedersenBVM:
    UNUSED = False
    USED = True
    CANDIDATE_NOT_FOUND = lambda self, x: 'Candidate with label {} does not exists'.format(x)
    VOTE_IS_FULL = 'Vote is already full'
    VOTE_SUCCESS = 'Vote recorded successfully'
    INVALID_DUMMY_TYPE = lambda self, x: 'Valid type is "used" or "unused"; received: ' + str(x)

    def __init__(self, config):
        security = config['security']
        self.num_of_voters = config['num_of_voters']
        self.num_of_candidates = len(config['candidate_labels'])
        self.num_of_dummy_votes = self.num_of_voters * self.num_of_candidates
        self.param = Pedersen.generate_param(security)
        self._generate_dummy_votes()
        self.candidate_data = self._setup_candidates(config['candidate_labels'])
        self.fresh_votes = []
        self.ballots = []
        self.num_of_received_votes = 0

    def vote(self, picked_candidate):
        if self.vote_is_full():
            raise ValueError(self.VOTE_IS_FULL)
        picked_candidate = picked_candidate.upper()
        if not self.label_exists(picked_candidate):
            raise ValueError(self.CANDIDATE_NOT_FOUND(picked_candidate))

        new_number = self._generate_fresh_random_number()
        fresh_vote = self._commit_vote(new_number)
        self.fresh_votes.append(fresh_vote)
        new_ballot = {}
        new_ballot['content'] = {}
        for label in self.candidate_data:
            if label == picked_candidate:
                new_ballot['content'][label] = fresh_vote[1]
                continue
            new_ballot['content'][label] = self._pick_random_dummy_vote(label)

        self.num_of_received_votes += 1
        new_ballot['id'] = self.num_of_received_votes
        self.ballots.append(new_ballot)
        self._sort_ballot_by_id()
        
        vote_response = {}
        vote_response['ballot'] = new_ballot['content']
        vote_response['description'] = self.VOTE_SUCCESS
        vote_response['accepted'] = True
        vote_response['id'] = self.num_of_received_votes
        return vote_response

    def verify_vote(self, commitment, vote, r_values):
        return Pedersen.open(commitment, vote, r_values, self.param)

    def get_candidate_labels(self):
        candidate_labels = []
        for label in self.candidate_data:
            candidate_labels.append(label)
        return candidate_labels

    def get_candidate_data(self, label):
        if not self.label_exists(label):
            raise ValueError(self.CANDIDATE_NOT_FOUND(label))
        return self.candidate_data[label.upper()]

    def get_poll_result(self):
        poll_result = {}
        non_voters = (self.num_of_voters - self.num_of_received_votes)
        for label in self.candidate_data:
            label = label.upper()
            unused_dv = 0
            for dv in self.candidate_data[label]['dummy_votes']:
                if dv[3] is self.UNUSED:
                    unused_dv += 1
            print(label, unused_dv)
            tally = unused_dv - non_voters
            poll_result[label] = tally
        return poll_result

    def get_candidate_dummy_vote(self, label, status='all'):
        label = label.upper()
        if not self.label_exists(label):
            raise ValueError(self.CANDIDATE_NOT_FOUND(label))
        if status == 'all':
            return [dv[0] for dv in self.candidate_data[label]['dummy_votes']]
        elif status == 'used':
            response = []
            for dv in self.candidate_data[label]['dummy_votes']:
                if dv[3] == self.USED:
                    response.append(dv[0])
            return response
        elif status == 'unused':
            response = []
            for dv in self.candidate_data[label]['dummy_votes']:
                if dv[3] == self.UNUSED:
                    response.append(dv[0])
            return response
        else:
            raise ValueError(self.INVALID_DUMMY_TYPE(status))

    def get_candidate_commitments(self, label, status='all'):
        label = label.upper()
        if not self.label_exists(label):
            raise ValueError(self.CANDIDATE_NOT_FOUND(label))
        if status == 'all':
            return [dv[1] for dv in self.candidate_data[label]['dummy_votes']]
        elif status == 'used':
            response = []
            for dv in self.candidate_data[label]['dummy_votes']:
                if dv[3] == self.USED:
                    response.append(dv[1])
            return response
        elif status == 'unused':
            response = []
            for dv in self.candidate_data[label]['dummy_votes']:
                if dv[3] == self.UNUSED:
                    response.append(dv[1])
            return response
        else:
            raise ValueError(self.INVALID_DUMMY_TYPE(status))

    def get_fresh_votes(self):
        return [dv[0] for dv in self.fresh_votes]

    def get_fresh_votes_commitments(self):
        return [dv[1] for dv in self.fresh_votes]

    def get_ballots(self):
        return self.ballots

    def label_exists(self, label):
        return label.upper() in self.candidate_data

    def vote_is_full(self):
        return self.num_of_voters == self.num_of_received_votes

    def _generate_fresh_random_number(self):
        new_number = number.getRandomRange(1, 5*self.num_of_dummy_votes)
        while (self._number_is_already_used(new_number)):
            new_number = number.getRandomRange(1, 5*self.num_of_dummy_votes)
        return new_number

    def _number_is_already_used(self, new_number):
        for cnd in self.candidate_data:
            cnd_dv = [dv[0] for dv in self.candidate_data[cnd]['dummy_votes']]
            if new_number in cnd_dv:
                return True
        return False

    def _commit_vote(self, vote):
        c, r = Pedersen.commit(vote, self.param)
        return (vote, c, r)

    def _pick_random_dummy_vote(self, label):
        idx = [i for i in range(len(self.candidate_data[label]['dummy_votes']))]
        r = random.SystemRandom()
        r.shuffle(idx)
        for i in idx:
            dv = self.candidate_data[label]['dummy_votes'][i]
            if dv[3] is self.UNUSED:
                self.candidate_data[label]['dummy_votes'][i] = (*dv[:-1], self.USED)
                return dv[1]
        raise IndexError('All dummy votes taken')

    def _generate_dummy_votes(self):
        dummy_votes = []
        for _ in range(self.num_of_dummy_votes):
            new_dummy = number.getRandomRange(1, 5*self.num_of_dummy_votes)
            while new_dummy in dummy_votes:
                new_dummy = number.getRandomRange(1, 5*self.num_of_dummy_votes)
            dummy_votes.append(new_dummy)
        return dummy_votes

    def _setup_candidates(self, cadidate_labels):
        unused_dummy_votes = self._generate_dummy_votes()
        candidate_data = {}
        for label in cadidate_labels:
            label = label.upper()
            label = label.replace(' ', '-')
            candidate_data[label] = {}
            candidate_data[label]['dummy_votes'] = []
            for _ in range(self.num_of_voters):
                random.shuffle(unused_dummy_votes)
                dv = unused_dummy_votes.pop()
                candidate_data[label]['dummy_votes'].append((*self._commit_vote(dv), self.UNUSED))
        return candidate_data

    def _sort_ballot_by_id(self):
        temp_list = sorted(self.ballots, key = lambda k:k['id'])
        self.ballots = temp_list