import json
from helpers import *
#This code could be optmized significantly, but is good enough for testing
with open("config.json","r") as fp:
	config = json.load(fp)
def powerset(a):
	subsets = []
	for i in range(2**len(a)):
		current_subset = [a[j] for j in range(len(a)) if (i % (2**(j+1))) - (i %(2**j)) == 0]
		subsets.append(current_subset)
	return subsets
all_rooms = list(config.keys())
all_sets_of_rooms = powerset(all_rooms)
def union_config_attributes(rooms, att):
	stuff = [c for r in rooms for c in config[r][att]]
	return stuff
all_words = union_config_attributes(all_rooms, "vocab")
all_cells = union_config_attributes(all_rooms,"cells")
num_all_cells = len(all_cells)

def probability_of_word(word, rooms, alpha = 0.01, all_room_words = all_words):
	rooms_vocab = union_config_attributes(rooms, "vocab")
	if word in rooms_vocab:
		d = 1
	else:
		d = 0
	return (d + alpha)/(len(rooms_vocab) + alpha * len(all_room_words))
def cell_to_room(cell):
	for r in all_rooms:
		if cell in config[r]["cells"]:
			return r
	return None
def rooms_to_belief(rooms, psi = .8, equal_density = True):
	if type(rooms) is type(""):
		rooms = [rooms]
	if equal_density:
		included_cells = union_config_attributes(rooms,"cells")
		excluded_cells = [i for i in all_cells if i not in included_cells]
		num_included_cells = len(included_cells)
		num_excluded_cells = len(excluded_cells)
		if num_included_cells == num_all_cells:
			included_prob = 1 / num_included_cells
		elif num_included_cells == 0:
			excluded_prob = 1 / num_excluded_cells
		else:
			included_prob = psi / num_included_cells
			excluded_prob = (1-psi) / num_excluded_cells

		belief = [included_prob if i in included_cells else excluded_prob for i in all_cells]
	else:
		num_rooms = len(rooms)
		excluded_cells = [i for i in all_cells if cell_to_room(i) not in rooms]
		num_excluded_cells = len(excluded_cells)
		if num_rooms > 0:
			if num_excluded_cells > 0:
				probability_per_included_room = psi/len(rooms)
				probability_per_excluded_cell = (1 - psi) / num_excluded_cells
			else:
				probability_per_included_room = 1/len(rooms)
		else:
			probability_per_excluded_cell = 1 / num_all_cells
		density_by_room = {r: probability_per_included_room/len(config[r]["cells"]) if r in rooms else probability_per_excluded_cell for r in all_rooms}
		belief = [density_by_room[cell_to_room(i)] for i in all_cells]
	total_prob = sum_over_list(belief)
	if abs(total_prob - 1) > 0.01:
		print("belief has volume " + str(total_prob))
		print(belief)
	return belief
belief_by_rooms_equal_density = [rooms_to_belief(r, equal_density=True) for r in all_sets_of_rooms]
belief_by_rooms_equal_probability = [rooms_to_belief(r, equal_density=False) for r in all_sets_of_rooms]

def room_prob_of_language(language, rooms):
	#This is a bad name
	rooms_vocab =union_config_attributes(rooms,"vocab")
	included_prob = 1
	for w in language:
		included_prob *= probability_of_word(w,rooms)
	excluded_prob = 1
	excluded_words = [w for w in rooms_vocab if w not in language]
	for w in excluded_words:
		excluded_prob *= (1 - probability_of_word(w,rooms))
	return included_prob * excluded_prob

def room_language_to_belief(language, init_belief, equal_density = True):
	if equal_density:
		belief_by_rooms = belief_by_rooms_equal_density
	else:
		belief_by_rooms = belief_by_rooms_equal_probability
	#The probability that a human holds the belief corresponding to each set of rooms
	probs_of_rooms = [dot(b,init_belief) for b in belief_by_rooms]
	language_prob_by_set_of_rooms = [room_prob_of_language(language, r) for r in all_sets_of_rooms]
	probs_of_l_and_r = [language_prob_by_set_of_rooms[i] * probs_of_rooms[i] for i in range(len(all_sets_of_rooms))]
	denominator = sum(probs_of_l_and_r)
	probs_of_r_given_l = [probs_of_l_and_r[i] / denominator for i in range(len(all_sets_of_rooms))]
	net_belief = linear_combination_of_lists(belief_by_rooms,probs_of_r_given_l)
	return net_belief
def belief_update(b_0, b_h):
	b_1_abnormal = [b_h[i] *b_0[i] for i in range(len(b_0))]
	denominator = sum(b_1_abnormal)
	b_1 = [b_1_abnormal[i] / denominator for i in range(len(b_0))]
	return b_1
def repeat_observations_and_updates(b0, language,equal_density = True, n = 10):
	b = b0
	beliefs = [b0]
	for i in range(n):
		bh = room_language_to_belief(language.split(" "), b, equal_density=equal_density)
		b = belief_update(b,bh)
		beliefs.append(b)
		print(b)
	return beliefs
rooms = ["kitchen","library"]
# rooms_vocab = get_vocab_for_rooms(rooms)
# language = ["kitchen","library"]
# language_prob = room_prob_of_language(language,rooms)
# print(language_prob)
# print({r: room_prob_of_language(["kitchen"],[r]) for r in config.keys()})
# print(room_prob_of_language(["library"],["library"]))
# print(union_config_attributes(rooms,"vocab"))
# b1 = rooms_to_belief(["kitchen","bedroom"], equal_density=False)
b0 = uniform(len(all_cells))
# b_h0 = room_language_to_belief("kitchen library".split(" "),b0)
# print(b_h0)
# # b2 = room_language_to_belief("kitchen library".split(" "), b1)
# # print(b2)
# b1 = belief_update(b0,b_h0)
# print(b1)
# b_h1 = room_language_to_belief("kitchen library".split(" "),b1)
# b2 = belief_update(b1,b_h1)
# print(b2)
bks = repeat_observations_and_updates(b0, "kitchen library", equal_density = True, n = 10)

#If the rooms contain more than psi of the cells, they will actually be considered less likely