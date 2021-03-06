# Star Battle solver via CSP.

# Uses a partial solve done manually to speed things up.

from constraint import Problem
from itertools import combinations

N = 2  # number of stars per row/column/group

# From 2017 MIT Mystery Hunt. 
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

# partial solution: known cells are marked 0/1.
# This speeds up the solution from 13s to 6s.
partial = """
..........
.0..00000.
....00..0.
..........
........0.
..........
..........
..........
..........
..........
"""
partial = partial.strip().splitlines()

# Transform the map into a list of lists
grid = [list(row.strip()) for row in grid.splitlines() if row.strip()]
groupnames = sorted(set(char for row in grid for char in row))
# Cells corresponding to each group
groupcells = { groupname: [] for groupname in groupnames }
for j, row in enumerate(grid):
	for i, char in enumerate(row):
		groupcells[char].append((i, j))

S = len(grid)  # size of the grid
assert all(len(row) == S for row in grid)
assert len(groupnames) == S

rownames = list(range(S))
columnnames = list(range(S))

# All length-N sequences of x's such that 0 <= x_i < S for all i, and x_i + 1 < x_(i+1).
# This is all possible layouts of N stars in a length-S row.
spaced = lambda x: all(x[i] + 1 < x[i+1] for i in range(len(x) - 1))
layouts = [layout for layout in combinations(range(S), N) if spaced(layout)]

# Whether the layout matches the partial solution for the row.
def matchpartial(layout, prow):
	for col, value in enumerate(prow):
		if value != "." and (value == "1") != (col in layout):
			return False
	return True

# Two layouts may be used on adjacent rows if none of their entries are adjacent.
okadjacent = lambda x, y: not any(abs(a - b) <= 1 for a in x for b in y)

# Returns the constraint for a column, i.e. that exactly N rows have an element in that column.
def okcolumn(columnname):
	return lambda *layouts: sum(columnname in layout for layout in layouts) == N

# Returns the constraint and corresponding set of rows for the given group name.
# i.e. that the number of stars in the group is equal to N.
def okgroup(groupname):
	cells = groupcells[groupname]
	rows = sorted(set(j for i, j in cells))
	# For each row under consideration, construct a set of all cells in that row.
	cellsperrow = [set(i for i, j in cells if j == row) for row in rows]
	# The number of stars in the group is the sum of the intersection of this set with the row's layout.
	constraint = lambda *layouts: sum(len(cells & set(layout)) for cells, layout in zip(cellsperrow, layouts)) == N
	return constraint, rows

problem = Problem()
for row in rownames:
	problem.addVariable(row, [layout for layout in layouts if matchpartial(layout, partial[row])])
for row1, row2 in zip(rownames[:-1], rownames[1:]):
	problem.addConstraint(okadjacent, (row1, row2))
for column in columnnames:
	problem.addConstraint(okcolumn(column), rownames)
for groupname in groupnames:
	constraint, rows = okgroup(groupname)
	problem.addConstraint(constraint, rows)

for solution in problem.getSolutions():
	for row in rownames:
		layout = solution[row]
		print(" ".join("*" if i in layout else "." for i in range(S)))
	print()

