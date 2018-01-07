# Hitori solver

# No two cells with the same number in the same row/column may be unshaded.
# No two shaded cells may be adjacent (diagonal is okay).
# All unshaded cells must be connected (not counting diagonals).

from constraint import Problem, SomeNotInSetConstraint
from itertools import permutations

# Example from Wikipedia.
# Solves in 3m
grid = """
48163257
36721654
23482861
41657735
72318512
35673184
64235478
87142356
"""
grid = [list(row.strip()) for row in grid.splitlines() if row.strip()]
S = len(grid)

cellnames = [(i,j) for j, row in enumerate(grid) for i, val in enumerate(row)]
lookup = { (i,j): grid[i][j] for i, j in cellnames }

problem = Problem()
problem.addVariables(cellnames, [False, True])  # False = unshaded, True = shaded

def isadjacent(cell0, cell1):
	(i0, j0), (i1, j1) = cell0, cell1
	return abs(i0 - i1) + abs(j0 - j1) == 1

def issameroworcol(cell0, cell1):
	(i0, j0), (i1, j1) = cell0, cell1
	return i0 == i1 or j0 == j1

for cell0 in cellnames:
	for cell1 in cellnames:
		if cell0 < cell1:
			# cells in the same row or column with the same value cannot both be False
			if issameroworcol(cell0, cell1) and lookup[cell0] == lookup[cell1]:
				problem.addConstraint(SomeNotInSetConstraint([False]), [cell0, cell1])
			# adjacent cells cannot both be True
			if isadjacent(cell0, cell1):
				problem.addConstraint(SomeNotInSetConstraint([True]), [cell0, cell1])

# All unshaded cells must be connected.
def allconnected(*values):
	# Find all connected regions of unshaded cells and count them.
	regions = []
	for cellname, value in zip(cellnames, values):
		if value: continue
		thisregion = set([cellname]) # All cells encountered so far that are connected to this cell.
		otherregions = []  # All regions that are not connected to this cell.
		for region in regions:
			if any(isadjacent(cellname, p) for p in region):
				thisregion |= region
			else:
				otherregions.append(region)
		regions = otherregions + [thisregion]
	return len(regions) <= 1
problem.addConstraint(allconnected, cellnames)

for solution in problem.getSolutions():
	sgrid = { cell: "#" if solution[cell] else lookup[cell] for cell in cellnames }
	print("\n".join(" ".join(sgrid[(i, j)] for j in range(S)) for i in range(S)))
	print()

