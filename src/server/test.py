from src.bingovoting.machines import PedersenBVM
import yaml

with open('config.yml', 'r') as stream:
    cnf = yaml.safe_load(stream)

config = {
    'security' : 5,
    'num_of_voters' : 10,
    'candidate_labels' : ['yes', 'no', 'abstain']
}
print(cnf['bvm'])
print(config)

bvm = PedersenBVM(config)

candidates = (bvm.get_candidate_list())

# print('before voting\n')
# for c in candidates:
#     print(c)
#     print(bvm.get_candidate_data(c))


# print('\n\nduring voting\n')
# print(bvm.vote('yes'))
# print(bvm.vote('yes'))
# print(bvm.vote('no'))
# print(bvm.vote('yes'))
# print(bvm.vote('no'))
# print(bvm.vote('yes'))
# print(bvm.vote('abstain'))

# print('\n\nafter voting\n')
# for c in candidates:
#     print(c)
#     print(bvm.get_candidate_data(c))

# print(bvm.get_poll_result())
"""
published = 7
non-voter = 3

yes
    used = 3
    unused = 7
no
    used = 5
    unused = 5

abstain
    used = 6
    unused = 4
"""