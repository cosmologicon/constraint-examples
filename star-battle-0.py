# Star Battle solver via CSP.

# Constraints for Star Battle are:
# * Exactly N stars in every row, column, and named group.
# * No two stars may be adjacent, even diagonally.

# This version uses a straightforward interpretation of the constraints. Each cell is a variable
# set to either 0 or 1. There are S variables and 3S^2 - S + 1 constraints.

from constraint import Problem, ExactSumConstraint, SomeNotInSetConstraint
from itertools import combinations

N = 2  # number of stars per row/column/group

# From 2017 MIT Mystery Hunt. Solves in about 13 seconds.
grid = """
AABBBBBBCC
ABBADDDDDC
AAAADECCCC
DDDDDEEFFF
DGGGGGEHHF
GGIIIIEHFF
GIIJJIEHHH
GIGGJIEEJH
GIIGJIJJJH
GGGGJJJHHH
"""

if False:  # 5x5 example
	N = 1
	grid = """
	AAABB
	ACCCD
	AACCD
	AEEEE
	AAAEE
	"""

# Transform the map into a list of lists
grid = [list(row.strip()) for row in grid.splitlines() if row.strip()]
groupnames = sorted(set(char for row in grid for char in row))
# Cells corresponding to each group
groupcells = { groupname: [] for groupname in groupnames }
for j, row in enumerate(grid):
	for i, char in enumerate(row):
		groupcells[char].append((i, j))
cellnames = sorted(cell for group in groupcells.values() for cell in group)

S = len(grid)  # size of the grid
assert all(len(row) == S for row in grid)
assert len(groupnames) == S

rownames = list(range(S))
columnnames = list(range(S))

def isadjacent(cell0, cell1):
	(i0, j0), (i1, j1) = cell0, cell1
	return abs(i0 - i1) <= 1 and abs(j0 - j1) <= 1

problem = Problem()
problem.addVariables(cellnames, [0, 1])  # 1 = has a star

# Each row, column, and group must have exactly N stars
for row in rownames:
	problem.addConstraint(ExactSumConstraint(N), [(x, y) for x, y in cellnames if y == row])
for col in columnnames:
	problem.addConstraint(ExactSumConstraint(N), [(x, y) for x, y in cellnames if x == col])
for cells in groupcells.values():
	problem.addConstraint(ExactSumConstraint(N), cells)

# Adjacent cells may not both have a star
for cell0 in cellnames:
	for cell1 in cellnames:
		if cell0 < cell1 and isadjacent(cell0, cell1):
			problem.addConstraint(SomeNotInSetConstraint([1]), [cell0, cell1])

for solution in problem.getSolutions():
	sgrid = { cell: "*" if solution[cell] else "." for cell in cellnames }
	print("\n".join(" ".join(sgrid[(i, j)] for j in range(S)) for i in range(S)))

