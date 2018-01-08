# Maysu solver

# Pairs of adjacent cells may be either linked with an edge or unlinked. Linked edges must form a
# single continuous chain that doesn't intersect itself. The chain must pass through every cell with
# a circle. If the circle is white it must pass straight through. If the circle is black it must
# make a 90 degree turn there.

from constraint import *

# 0 = white circle, 1 = black circle
# Example from Wikipedia. Sovles in about 5 minutes.
grid = """
..0.0.....
....0...1.
..1.1.0...
...0..0...
1....0...0
..0....0..
..1...0...
0...1....0
......00..
..1......1
"""

if False:
	# 6x6 example, solves in 0.1s
	grid = """
	...1..
	....0.
	.0....
	....1.
	.1....
	..0...
	"""
grid = [list(row.strip()) for row in grid.splitlines() if row.strip()]

W, H = len(grid[0]), len(grid)  # size of grid
cellnames = [(x, y) for x in range(W) for y in range(H)]
# Define an edge variable as an ordered pair of the two cells it connects.
edges = [
	((x, y), (x+1, y)) for x in range(W-1) for y in range(H)
] + [
	((x, y), (x, y+1)) for x in range(W) for y in range(H-1)
]

problem = Problem()
problem.addVariables(edges, [0, 1])  # 0 = no line, 1 = line

# Every cell must have exactly 0 or 2 edges with a line.
for cell in cellnames:
	celledges = [edge for edge in edges if cell in edge]
	problem.addConstraint(lambda *values: sum(values) in (0, 2), celledges)

for x, y in cellnames:
	if grid[y][x] == ".":
		continue

	# edges in each of the four directions
	left = lambda n=1: ((x-n, y), (x-n+1, y))
	right = lambda n=1: ((x+n-1, y), (x+n, y))
	up = lambda n=1: ((x, y-n), (x, y-n+1))
	down = lambda n=1: ((x, y+n-1), (x, y+n))
	celledges = [edge for edge in edges in cell in edge]

	if grid[y][x] == "0":
		# White circles: the chain must pass straight through the circle.
		problem.addConstraint(ExactSumConstraint(2), celledges)
		# Thus pairs of opposite edges must be the same.
		if 0 < x < W-1:
			problem.addConstraint(AllEqualConstraint(), [left(), right()])
		if 0 < y < H-1:
			problem.addConstraint(AllEqualConstraint(), [up(), down()])
		# And any edge opposite the side of the grid must be empty.
		if x == 0:
			problem.addConstraint(InSetConstraint([0]), [right()])
		if x == W-1:
			problem.addConstraint(InSetConstraint([0]), [left()])
		if y == 0:
			problem.addConstraint(InSetConstraint([0]), [down()])
		if y == H-1:
			problem.addConstraint(InSetConstraint([0]), [up()])
		# The chain must turn either before or after passing through the white circle.
		# Thus you can't have 4 edges in a row centered on the circle.
		if 1 < x < W-2:
			problem.addConstraint(SomeNotInSetConstraint([1]), [left(2), left(), right(), right(2)])
		if 1 < y < H-2:
			yedges = [((x, y+b), (x, y+b+1)) for b in (-2, -1, 0, 1)]
			problem.addConstraint(SomeNotInSetConstraint([1]), [up(2), up(), down(), down(2)])

	if grid[y][x] == "1":
		# Black circles: the chain must pass through the circle and turn there.
		problem.addConstraint(ExactSumConstraint(2), celledges)
		# Thus pairs of opposite edges must be different.
		if 0 < x < W-1:
			problem.addConstraint(AllDifferentConstraint(), [left(), right()])
		if 0 < y < H-1:
			problem.addConstraint(AllDifferentConstraint(), [up(), down()])
		# And any edge opposite the side of the grid must be filled.
		if x == 0:
			problem.addConstraint(InSetConstraint([1]), [right()])
		if x == W-1:
			problem.addConstraint(InSetConstraint([1]), [left()])
		if y == 0:
			problem.addConstraint(InSetConstraint([1]), [down()])
		if y == H-1:
			problem.addConstraint(InSetConstraint([1]), [up()])
		# The chain can't turn right before or after passing through the black circle.
		# Thus if the edge leading out of the circle is filled, so must the next one be.
		# If this takes it off the grid, then the edge can't be filled at all.
		imp = lambda p, q: not p or q
		if x == 1:
			problem.addConstraint(InSetConstraint([0]), [left()])
		elif x > 1:
			problem.addConstraint(imp, [left(), left(2)])
		if x == W-2:
			problem.addConstraint(InSetConstraint([0]), [right()])
		elif x < W-2:
			problem.addConstraint(imp, [right(), right(2)])
		if y == 1:
			problem.addConstraint(InSetConstraint([0]), [up()])
		elif y > 1:
			problem.addConstraint(imp, [up(), up(2)])
		if y == H-2:
			problem.addConstraint(InSetConstraint([0]), [down()])
		elif y < H-2:
			problem.addConstraint(imp, [down(), down(2)])
		
# All edges must be connected.
def isadjacent(edge0, edge1):
	return any(cell in edge1 for cell in edge0)
def allconnected(*values):
	# Find all connected regions of edges and count them.
	regions = []
	for edge, value in zip(edges, values):
		if not value: continue
		thisregion = set([edge]) # All edges encountered so far that are connected to this edge.
		otherregions = []  # All regions that are not connected to this edge.
		for region in regions:
			if any(isadjacent(edge, p) for p in region):
				thisregion |= region
			else:
				otherregions.append(region)
		regions = otherregions + [thisregion]
	return len(regions) <= 1
problem.addConstraint(allconnected, edges)

for solution in problem.getSolutions():
	lines = []
	for y in range(H):
		line = ""
		for x in range(W):
			line += grid[y][x]
			if x < W - 1:
				line += "#" if solution[((x,y), (x+1,y))] else " "
		lines.append(line)
		if y < H - 1:
			chars = ["#" if solution[((x,y), (x,y+1))] else " " for x in range(W)]
			lines.append(" ".join(chars))
	print("\n".join(" ".join(line) for line in lines))
	print()


