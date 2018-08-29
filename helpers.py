def linear_combination_of_lists(ds,weights):
	new_lists = [times_list(ds[i],weights[i]) for i in range(len(ds))]
	return add_list_of_lists(new_lists)
def times_list(a, scalar):
	return [scalar * i for i in a]
def add_list_of_lists(ls):
	new_list = []
	for element_index in range(len(ls[0])):
		sum = 0
		for list_index in range(len(ls)):
			sum += ls[list_index][element_index]
		new_list.append(sum)
	return new_list
def sum_over_list(l):
	sum = 0
	for i in l:
		sum+= i
	return sum
def dot(a,b):
	sum = 0
	for i in range(len(a)):
		sum += a[i] * b[i]
	return sum
def uniform(length):
	p = 1.0/length
	return [p for i in range(length)]