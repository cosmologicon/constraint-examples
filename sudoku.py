# Sudoku solver

from constraint import Problem, AllDifferentConstraint, InSetConstraint

# Example from Wikipedia.
# Solves in 0.1s
grid = """
53..7....
6..195...
.98....6.
8...6...3
4..8.3..1
7...2...6
.6....28.
...419..5
....8..79
"""
grid = [list(row.strip()) for row in grid.splitlines() if row.strip()]
S = len(grid)
cellnames = [(i,j) for j, row in enumerate(grid) for i, val in enumerate(row)]
lookup = { (i,j): grid[i][j] for i, j in cellnames }

problem = Problem()
problem.addVariables(cellnames, [str(j) for j in range(1, 10)])

for j in range(9):
	# Cells in a column must all be different
	problem.addConstraint(AllDifferentConstraint(), [(i, j) for i in range(9)])
	# Cells in a row must all be different
	problem.addConstraint(AllDifferentConstraint(), [(j, i) for i in range(9)])
for i in range(3):
	for j in range(3):
		# Cells in a 3x3 group must all be different
		problem.addConstraint(AllDifferentConstraint(), [(i*3+a, j*3+b) for a in range(3) for b in range(3)])
for cell, value in lookup.items():
	if value != ".":
		problem.addConstraint(InSetConstraint([str(value)]), [cell])

for solution in problem.getSolutions():
	print("\n".join(" ".join(solution[(i, j)] for j in range(9)) for i in range(9)))
	print()

