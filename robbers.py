class Cell():
    origin = 'C'

    def __init__(self, row, column, content):
        self.coord = (row, column)
        self.neighbors = []
        self.paths = [[]]
        if column > 0:
            self.neighbors.append((row, column-1))
        if column < columns-1:
            self.neighbors.append((row, column+1))
        if row > 0:
            self.neighbors.append((row-1, column))
        if row < rows-1:
            self.neighbors.append((row+1, column))
        self.content = content
        if content == self.origin:
            self.dist = 0
        else:
            self.dist = rows*columns

    def addpath(self, prevcell):
        if self.content != 'x':
            if prevcell.dist+1 < self.dist:
                self.dist = prevcell.dist+1
                self.paths = []
            if prevcell.dist+1 == self.dist:
                for path in prevcell.paths:
                    p = path.copy()
                    p.append(prevcell.coord)
                    self.paths.append(p)


input = """
.....
...C.
.B.x.
.....
...F.
.....
"""
rows, columns = 6, 5

input = """
C....
...B.
xx.x.
.....
.F...
.....
.....
"""
rows, columns = 7, 5

def createcells():
    cells = {}
    unvisited = []
    dest = None
    lines = input.strip().splitlines()

    for i in range(rows):
        for j in range(columns):
            c = Cell(i, j, lines[i][j])
            cells[(i,j)] = c
            unvisited.append(c)
            if c.content == 'F':
                dest = c
    unvisited.sort(key= lambda x: x.dist, reverse=True)

    return cells, unvisited, dest

def solve(cells, unvisited):
    while unvisited:
        c = unvisited.pop()
        for coord in c.neighbors:
            n = cells[coord]
            n.addpath(c)
        unvisited.sort(key= lambda x: x.dist, reverse=True)

def printcells(cells):
    for i in range(rows):
        for j in range(columns):
            print(cells[(i,j)].content, end=' ')
        print()

if __name__ == '__main__':
    Cell.origin = 'C'
    cells, unvisited, dest = createcells()
    solve(cells, unvisited)
    for path in dest.paths:
        print(path)

    exit()
    paths = dest.paths
    Cell.origin = 'B'
    cells, unvisited, dest = createcells()
    for path in paths:
        for coord in path:
            cells[coord].content = 'x'
    printcells(cells)
    solve(cells, unvisited)
    print(dest.dist, dest.paths)
