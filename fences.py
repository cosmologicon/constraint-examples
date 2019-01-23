

from constraint import Problem, SomeNotInSetConstraint

# http://web.mit.edu/puzzle/www/2018/full/puzzle/good_fences_make_sad_and_disgusted_neighbors.html
grid = """50141
420112
3244323
42453422
152324125
 34215200
  3301330
   020363
    10033"""

#grid = """12
#541
# 02"""
 
#grid = """0"""

grid = {
	(x, y): int(c)
	for y, row in enumerate(grid.splitlines())
	for x, c in enumerate(row)
	if c.isdigit()
}
eways = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1)]
def neighbor(cell0, cell1):
	x0, y0 = cell0
	x1, y1 = cell1
	return (x1 - x0, y1 - y0) in eways

edges = set(
	tuple(sorted([(x, y), (x + dx, y + dy)]))
	for x, y in grid
	for dx, dy in eways
)
edgetrios = set(
	(edge0, edge1, edge2)
	for edge0 in edges
	for edge1 in edges
	for edge2 in edges
	if edge0 < edge1 < edge2
	and len(set(edge0 + edge1 + edge2)) == 3
)
def isadjacent(edge0, edge1):
	if edge0 == edge1: return False
	return all(neighbor(cell0, cell1) or cell0 == cell1 for cell0 in edge0 for cell1 in edge1)

aedges = set((edge0, edge1) for edge0 in edges for edge1 in edges if isadjacent(edge0, edge1))

edges = sorted(edges)

problem = Problem()
problem.addVariables(grid, [False, True])  # False = sad, True = disgusted
problem.addVariables(edges, [False, True])

def sadsumequals(n):
	def ok(cell, *neighbors):
		return cell or sum(not x for x in neighbors) == n
	return ok
def dissumequals(n):
	def ok(cell, *edges):
		return not cell or sum(edges) == n
	return ok

for edgetrio in edgetrios:
	problem.addConstraint(SomeNotInSetConstraint([True]), edgetrio)

for cell in grid:
	ns = [c for c in grid if neighbor(cell, c)]
	nedges = [edge for edge in edges if cell in edge]
	problem.addConstraint(sadsumequals(grid[cell]), [cell] + ns)
	problem.addConstraint(dissumequals(grid[cell]), [cell] + nedges)

# All edges must be connected.
def allconnected(*values):
	ons = set(edge for edge, value in zip(edges, values) if value)
	regions = []
	for edge, value in zip(edges, values):
		if not value: continue
		if sum(p in ons and ((p, edge) in aedges) for p in edges) != 2:
			return False
		thisregion = set([edge])
		otherregions = []
		for region in regions:
			if any((edge, p) in aedges for p in region):
				thisregion |= region
			else:
				otherregions.append(region)
		regions = otherregions + [thisregion]
	return len(regions) <= 1
problem.addConstraint(allconnected, edges)

print("starting...")
	
for solution in problem.getSolutions():
	print(solution)
	exit()

