# ABC End View solver

# Each letter must appear exactly once in each row and column. Not every cell is filled.
# Some rows and columns' ends are specified. These mean that the filled cell closest to that
# end must have the given letter.

from constraint import Problem, AllDifferentConstraint
from itertools import permutations

# Example puzzle from:
# https://www.janko.at/Raetsel/Abc-End-View/550.a.htm
# Solves in 1.2s

letters = "ABCDEF"

# Row end constraints, from top to bottom
left = ".F.CBE."
right = "FBE.CAB"
# Column end constraints, from left to right
top = "ECAD.A."
bottom = "AFCFE.B"

N = len(letters)
S = len(left)  # size of the grid.
B = S - N  # number of blanks per row/column.

# Each variable represents the column position of the given letter in the given row.
variables = [letter + str(row) for letter in letters for row in range(S)]
problem = Problem()
problem.addVariables(variables, list(range(S)))

# Within a row, each letter must be in a different column.
for row in range(S):
	rowvars = [letter + str(row) for letter in letters]
	problem.addConstraint(AllDifferentConstraint(), rowvars)

# The columns that a single given letter appears in must be all different.
for letter in letters:
	lettervars = [letter + str(row) for row in range(S)]
	problem.addConstraint(AllDifferentConstraint(), lettervars)

# Left constraints: if specified, the column of the letter given in the constraint must be
# less than the column of every other letter in that row.
for row, letter in enumerate(left):
	if letter == ".": continue
	for other in letters:
		if other != letter:
			problem.addConstraint(lambda x, y: x < y, (letter + str(row), other + str(row)))
# Right constraints: if specified, the column of the letter given in the constraint must be
# greater than the column of every other letter in that row.
for row, letter in enumerate(right):
	if letter == ".": continue
	for other in letters:
		if other != letter:
			problem.addConstraint(lambda x, y: x > y, (letter + str(row), other + str(row)))

# Top constraints are implemented by finding the topmost variable that appears in a given column,
# and checking whether it's the correct letter. We order the letters so that the correct letters
# are the 0th, Nth, 2Nth, etc. Thus the constraint is equivalent to whether the index of the first
# variable whose value is the given col is divisible by N.
# Bottom constraints work the same way.
def tbconstraint(col):
	def ok(*values):
		for j, value in enumerate(values):
			if value == col:
				return j % N == 0
		return False
	return ok

# Order the variables in the given set of rows such that the ones with the given letter appear at
# indices that are divisible by N.
def orderedvars(rows, letter):
	values = []
	for j, row in enumerate(rows):
		values.append(letter + str(row))
		# No need to check the incorrect letters on the last row in the list.
		# (This makes a huge difference in runtime!)
		if j < len(rows) - 1:
			values += [other + str(row) for other in letters if other != letter]
	return values

# Top constraints. We only have to check the top B+1 rows.
for col, letter in enumerate(top):
	if letter == ".": continue
	problem.addConstraint(tbconstraint(col), orderedvars(range(B+1), letter))
# Bottom constraints. We only have to check the bottom B+1 rows, starting from the bottom.
for col, letter in enumerate(bottom):
	if letter == ".": continue
	problem.addConstraint(tbconstraint(col), orderedvars(range(S-1, S-B-2, -1), letter))

for solution in problem.getSolutions():
	grid = [["." for col in range(S)] for row in range(S)]
	for value, col in solution.items():
		letter = value[0]
		row = int(value[1:])
		grid[row][col] = letter
	print("\n".join(" ".join(row) for row in grid))

