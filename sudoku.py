class Board():
    def __init__(self, digits, input):
        lines = input.strip().splitlines()
        self.cells = {}
        self.relations = {}
        self.digits = digits
        self.empty = []

        for i in range(digits):
            for j in range(digits):
                self.cells[(i, j)] = [i for i in range(1, digits+1)]
                self.relations[(i, j)] = []
                self.empty.append((i, j))

        for i in range(0, digits*2-1):
            for j in range((i+1)%2, digits*2-1, 2):
                char = lines[i][j]
                if char == "v":
                    self.relations[((i-1)//2, j//2)].append((((i+1)//2, j//2), "<"))
                    self.relations[((i+1)//2, j//2)].append((((i-1)//2, j//2), ">"))
                elif char == ">":
                    self.relations[(i//2, (j-1)//2)].append(((i//2, (j+1)//2), "<"))
                    self.relations[(i//2, (j+1)//2)].append(((i//2, (j-1)//2), ">"))
                elif char == "<":
                    self.relations[(i//2, (j-1)//2)].append(((i//2, (j+1)//2), ">"))
                    self.relations[(i//2, (j+1)//2)].append(((i//2, (j-1)//2), "<"))
                elif char == "^":
                    self.relations[((i-1)//2, j//2)].append((((i+1)//2, j//2), ">"))
                    self.relations[((i+1)//2, j//2)].append((((i-1)//2, j//2), "<"))

    def fillcell(self, row, column, value):
        self.cells[(row, column)] = [value]
        self.empty.remove((row, column))
        return self.getpropositions(row, column)

    def getpropositions(self, row, column):
        props = []
        val = self.cells[(row, column)]
        if len(val) == 1:
            for i in range(self.digits):
                if i != column and len(self.cells[(row, i)]) > 1:
                    props.append(((row, i), "!", val))
                if i != row and len(self.cells[(i, column)]) > 1:
                    props.append(((i, column), "!", val))
        for rel in self.relations[(row, column)]:
            if len(self.cells[rel[0]]) > 1:
                props.append((rel[0], rel[1], val))
        return props

    def resolve(self, prop):
        changed = False
        print(self.cells[prop[0]], end=' ')
        if prop[1] == '!':
            try:
                self.cells[prop[0]].remove(prop[2][0])
                changed = True
            except ValueError:
                pass
        elif prop[1] == '>':
            for v in range(prop[2][0]+1):
                try:
                    self.cells[prop[0]].remove(v)
                    changed = True
                except ValueError:
                    pass
        elif prop[1] == '<':
            for v in range(prop[2][-1], self.digits+1):
                try:
                    self.cells[prop[0]].remove(v)
                    changed = True
                except ValueError:
                    pass

        print(self.cells[prop[0]])

        if len(self.cells[prop[0]]) == 1:
            try:
                self.empty.remove(prop[0])
            except ValueError:
                pass

        if changed:
            props = []
            if len(self.cells[prop[0]]) == 1 or self.relations[prop[0]]:
                props.extend(self.getpropositions(prop[0][0], prop[0][1]))
            return props

input = """
-.3.-.-.-
.........
-.-.-.-.-
.........
-.-.2.-.-
v.....v..
-.5.-.-.-
v.....v..
-.-.-.2>-
"""

if __name__ == "__main__":
    board = Board(5, input)
    lines = input.strip().splitlines()
    stack = []
    for i in range(5):
        for j in range(5):
            char = lines[i*2][j*2]
            if char.isdigit():
                stack.extend(board.fillcell(i, j, int(char)))
    count = 0
    while stack and board.empty:
        p = stack.pop()
        print(count, len(stack), end=' ')
        props = board.resolve(p)
        if props:
            stack.extend(props)
        count += 1

    for coord, val in board.cells.items():
        print(coord, val)
