# N queens problem.
# Place N queens on an NxN chessboard so that no two queens are attacking each other.
# There are multiple solutions for N >= 4.

from constraint import Problem

# N = 8 solves in 0.1s
# N = 10 solves in 0.9s
# N = 12 solves in 21s
N = 12

problem = Problem()
values = list(range(N))
problem.addVariables(values, values)
def ok(d):
	return lambda x, y: x - y not in (-d, 0, d)
for row1 in values:
	for row2 in values:
		if row1 < row2:
			problem.addConstraint(ok(row2 - row1), (row1, row2))
for solution in problem.getSolutions():
	print(solution)
