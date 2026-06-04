import random
import tkinter as tk

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
UPDATE_DELAY = 120

DIRECTIONS = {
    "Up": (0, -1),
    "Down": (0, 1),
    "Left": (-1, 0),
    "Right": (1, 0),
}
OPPOSITE = {
    "Up": "Down",
    "Down": "Up",
    "Left": "Right",
    "Right": "Left",
}

class Snake:
    def __init__(self, positions, direction, color, tag):
        self.segments = positions
        self.direction = direction
        self.color = color
        self.tag = tag
        self.score = 0
        self.alive = True

    @property
    def head(self):
        return self.segments[0]

    def occupies(self, cell):
        return cell in self.segments

    def move(self, grow=False):
        dx, dy = DIRECTIONS[self.direction]
        head_x, head_y = self.head
        next_head = (head_x + dx, head_y + dy)
        self.segments.insert(0, next_head)
        if not grow:
            self.segments.pop()
        return next_head

    def is_crash(self):
        head = self.head
        return self.segments.count(head) > 1

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake vs AI")
        self.canvas = tk.Canvas(
            root,
            width=CELL_SIZE * GRID_WIDTH,
            height=CELL_SIZE * GRID_HEIGHT,
            bg="black",
        )
        self.canvas.pack()

        self.human_snake = Snake(
            positions=[(5, GRID_HEIGHT // 2), (4, GRID_HEIGHT // 2), (3, GRID_HEIGHT // 2)],
            direction="Right",
            color="#00FF00",
            tag="human",
        )
        self.ai_snake = Snake(
            positions=[(GRID_WIDTH - 6, GRID_HEIGHT // 2), (GRID_WIDTH - 5, GRID_HEIGHT // 2), (GRID_WIDTH - 4, GRID_HEIGHT // 2)],
            direction="Left",
            color="#00BFFF",
            tag="ai",
        )

        self.food = None
        self.running = True

        self.draw_grid()
        self.place_food()
        self.draw_food()
        self.draw_snake(self.human_snake)
        self.draw_snake(self.ai_snake)
        self.draw_status()

        self.root.bind("<Up>", lambda event: self.change_direction("Up"))
        self.root.bind("<Down>", lambda event: self.change_direction("Down"))
        self.root.bind("<Left>", lambda event: self.change_direction("Left"))
        self.root.bind("<Right>", lambda event: self.change_direction("Right"))

        self.update()

    def draw_grid(self):
        for x in range(0, GRID_WIDTH * CELL_SIZE, CELL_SIZE):
            self.canvas.create_line(x, 0, x, GRID_HEIGHT * CELL_SIZE, fill="#111111")
        for y in range(0, GRID_HEIGHT * CELL_SIZE, CELL_SIZE):
            self.canvas.create_line(0, y, GRID_WIDTH * CELL_SIZE, y, fill="#111111")

    def change_direction(self, direction):
        if direction != OPPOSITE[self.human_snake.direction]:
            self.human_snake.direction = direction

    def place_food(self):
        empty_cells = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if not self.human_snake.occupies((x, y)) and not self.ai_snake.occupies((x, y))
        ]
        self.food = random.choice(empty_cells)

    def draw_snake(self, snake):
        self.canvas.delete(snake.tag)
        for index, (x, y) in enumerate(snake.segments):
            color = snake.color if index == 0 else snake.color
            self.canvas.create_rectangle(
                x * CELL_SIZE,
                y * CELL_SIZE,
                (x + 1) * CELL_SIZE,
                (y + 1) * CELL_SIZE,
                fill=color,
                outline="",
                tags=snake.tag,
            )

    def draw_food(self):
        self.canvas.delete("food")
        x, y = self.food
        self.canvas.create_oval(
            x * CELL_SIZE + 4,
            y * CELL_SIZE + 4,
            (x + 1) * CELL_SIZE - 4,
            (y + 1) * CELL_SIZE - 4,
            fill="red",
            outline="",
            tags="food",
        )

    def draw_status(self):
        self.canvas.delete("status")
        self.canvas.create_text(
            10,
            10,
            anchor="nw",
            fill="white",
            font=("Consolas", 12),
            text=f"Human Score: {self.human_snake.score}",
            tags="status",
        )
        self.canvas.create_text(
            CELL_SIZE * GRID_WIDTH - 10,
            10,
            anchor="ne",
            fill="white",
            font=("Consolas", 12),
            text=f"AI Score: {self.ai_snake.score}",
            tags="status",
        )
        self.canvas.create_text(
            CELL_SIZE * GRID_WIDTH // 2,
            10,
            anchor="n",
            fill="white",
            font=("Consolas", 12),
            text="Arrow keys으로 사람 뱀 조작",
            tags="status",
        )

    def ai_choose_direction(self):
        best = None
        best_distance = float("inf")
        for direction, (dx, dy) in DIRECTIONS.items():
            if direction == OPPOSITE[self.ai_snake.direction]:
                continue
            head_x, head_y = self.ai_snake.head
            next_cell = (head_x + dx, head_y + dy)
            if self.is_cell_blocked(next_cell, attacker=self.ai_snake):
                continue
            distance = abs(next_cell[0] - self.food[0]) + abs(next_cell[1] - self.food[1])
            if distance < best_distance:
                best_distance = distance
                best = direction

        if best:
            return best

        for direction, (dx, dy) in DIRECTIONS.items():
            if direction == OPPOSITE[self.ai_snake.direction]:
                continue
            head_x, head_y = self.ai_snake.head
            next_cell = (head_x + dx, head_y + dy)
            if not self.is_cell_blocked(next_cell, attacker=self.ai_snake):
                return direction

        return self.ai_snake.direction

    def is_cell_blocked(self, cell, attacker):
        x, y = cell
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return True
        if attacker.occupies(cell):
            return True
        other = self.human_snake if attacker is self.ai_snake else self.ai_snake
        if other.occupies(cell):
            return True
        return False

    def update(self):
        if not self.running:
            return

        self.ai_snake.direction = self.ai_choose_direction()

        human_next = self.next_position(self.human_snake)
        ai_next = self.next_position(self.ai_snake)

        human_crash = self.will_crash(self.human_snake, human_next, ai_next)
        ai_crash = self.will_crash(self.ai_snake, ai_next, human_next)

        if human_next == ai_next:
            human_crash = True
            ai_crash = True

        if human_crash:
            self.human_snake.alive = False
        if ai_crash:
            self.ai_snake.alive = False

        if not self.human_snake.alive or not self.ai_snake.alive:
            self.game_over()
            return

        human_grow = human_next == self.food
        ai_grow = ai_next == self.food

        self.human_snake.move(grow=human_grow)
        self.ai_snake.move(grow=ai_grow)

        if human_grow or ai_grow:
            self.place_food()
            self.draw_food()
            if human_grow:
                self.human_snake.score += 1
            if ai_grow:
                self.ai_snake.score += 1

        self.draw_snake(self.human_snake)
        self.draw_snake(self.ai_snake)
        self.draw_status()

        self.root.after(UPDATE_DELAY, self.update)

    def next_position(self, snake):
        dx, dy = DIRECTIONS[snake.direction]
        head_x, head_y = snake.head
        return (head_x + dx, head_y + dy)

    def will_crash(self, snake, next_head, other_next):
        x, y = next_head
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return True
        if next_head in snake.segments:
            return True
        other = self.ai_snake if snake is self.human_snake else self.human_snake
        if next_head in other.segments:
            return True
        if next_head == other_next:
            return True
        return False

    def game_over(self):
        self.running = False
        winner = "무승부"
        if self.human_snake.alive and not self.ai_snake.alive:
            winner = "사람 승리"
        elif self.ai_snake.alive and not self.human_snake.alive:
            winner = "AI 승리"
        elif self.human_snake.score > self.ai_snake.score:
            winner = "사람 승리"
        elif self.ai_snake.score > self.human_snake.score:
            winner = "AI 승리"

        self.canvas.create_text(
            CELL_SIZE * GRID_WIDTH // 2,
            CELL_SIZE * GRID_HEIGHT // 2 - 20,
            text="Game Over",
            fill="white",
            font=("Consolas", 32, "bold"),
        )
        self.canvas.create_text(
            CELL_SIZE * GRID_WIDTH // 2,
            CELL_SIZE * GRID_HEIGHT // 2 + 20,
            text=f"Winner: {winner}",
            fill="white",
            font=("Consolas", 18),
        )
        self.canvas.create_text(
            CELL_SIZE * GRID_WIDTH // 2,
            CELL_SIZE * GRID_HEIGHT // 2 + 50,
            text=f"Human: {self.human_snake.score}   AI: {self.ai_snake.score}",
            fill="white",
            font=("Consolas", 14),
        )

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
