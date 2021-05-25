from random import randint

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы выстрелили за пределы доски"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту точку"

class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"

class Ship:
    def __init__(self, ship_coord, lengh, direction):
        self.ship_coord = ship_coord
        self.lengh = lengh
        self.direction = direction
        self.lifes = lengh

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.lengh):
            co_x = self.ship_coord.x
            co_y = self.ship_coord.y

            if self.direction == 0:
                co_x += i
            elif self.direction == 1:
                co_y += i

            ship_dots.append(Dot(co_x, co_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hid = False, size = 6):
        self.hid = hid
        self.size = size
        self.count = 0
        self.busy = []
        self.ships = []
        self.field = [["O"]*size for _ in range(size)]

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        around = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in around:
                co = Dot(d.x + dx, d.y + dy)
                if not(self.out(co)) and co not in self.busy:
                    if verb:
                        self.field[co.x][co.y] = "T"
                    self.busy.append(co)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lifes -= 1
                self.field[d.x][d.y] = "X"
                if ship.lifes == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
        self.field[d.x][d.y] = "T"
        print("Промах!")
        return False

    def begin(self):
        self.busy = []

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d

class User(Player):
    def ask(self):
        while True:
            coords = input("Ваш ход: ").split()
            if len(coords) != 2:
                print("Введите 2 координаты через пробел")
                continue
            x, y = coords
            if not(x.isdigit()) or not(y.isdigit()):
                print("Введите числа")
                continue
            x, y = int(x), int(y)
            return Dot(x-1, y-1)

class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" Формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")
        print("-------------------")
        print(" Выйграет тот, кто ")
        print(" уничтожит корбали ")
        print(" противника ПЕРВЫЙ ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("-" * 20)
                print("Ход пользователя!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ход компьютера!")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.ai.board.count == 7:
                print("-"*20)
                print("Выйграл пользователь!")
                break
            if self.us.board.count == 7:
                print("-" * 20)
                print("Выйграл компьютер!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


ga = Game()
ga.start()
