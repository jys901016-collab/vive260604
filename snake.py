import random
import tkinter as tk

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
UPDATE_DELAY = 120

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game")
        self.canvas = tk.Canvas(
            root,
            width=CELL_SIZE * GRID_WIDTH,
            height=CELL_SIZE * GRID_HEIGHT,
            bg="black",
        )
        self.canvas.pack()

        self.direction = "Right"
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.grow_snake = False
        self.food = None
        self.score = 0

        self.draw_grid()
        self.place_food()
        self.draw_snake()
        self.draw_food()

        self.root.bind("<Up>", lambda event: self.change_direction("Up"))
        self.root.bind("<Down>", lambda event: self.change_direction("Down"))
        self.root.bind("<Left>", lambda event: self.change_direction("Left"))
        self.root.bind("<Right>", lambda event: self.change_direction("Right"))

        self.status_text = self.canvas.create_text(
            10,
            10,
            anchor="nw",
            fill="white",
            font=("Consolas", 12),
            text=f"Score: {self.score}",
        )

        self.running = True
        self.update()

    def draw_grid(self):
        for x in range(0, GRID_WIDTH * CELL_SIZE, CELL_SIZE):
            self.canvas.create_line(x, 0, x, GRID_HEIGHT * CELL_SIZE, fill="#111111")
        for y in range(0, GRID_HEIGHT * CELL_SIZE, CELL_SIZE):
            self.canvas.create_line(0, y, GRID_WIDTH * CELL_SIZE, y, fill="#111111")

    def change_direction(self, direction):
        opposite = {
            "Up": "Down",
            "Down": "Up",
            "Left": "Right",
            "Right": "Left",
        }
        if direction != opposite.get(self.direction):
            self.direction = direction

    def place_food(self):
        empty_cells = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in self.snake
        ]
        self.food = random.choice(empty_cells)

    def draw_snake(self):
        self.canvas.delete("snake")
        for index, (x, y) in enumerate(self.snake):
            color = "#00FF00" if index == 0 else "#00CC00"
            self.canvas.create_rectangle(
                x * CELL_SIZE,
                y * CELL_SIZE,
                (x + 1) * CELL_SIZE,
                (y + 1) * CELL_SIZE,
                fill=color,
                outline="",
                tags="snake",
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

    def update_score(self):
        self.canvas.itemconfigure(self.status_text, text=f"Score: {self.score}")

    def game_over(self):
        self.running = False
        self.canvas.create_text(
            GRID_WIDTH * CELL_SIZE // 2,
            GRID_HEIGHT * CELL_SIZE // 2,
            text="Game Over",
            fill="white",
            font=("Consolas", 32, "bold"),
        )
        self.canvas.create_text(
            GRID_WIDTH * CELL_SIZE // 2,
            GRID_HEIGHT * CELL_SIZE // 2 + 40,
            text=f"Final Score: {self.score}",
            fill="white",
            font=("Consolas", 16),
        )

    def update(self):
        if not self.running:
            return

        head_x, head_y = self.snake[0]
        if self.direction == "Up":
            head_y -= 1
        elif self.direction == "Down":
            head_y += 1
        elif self.direction == "Left":
            head_x -= 1
        elif self.direction == "Right":
            head_x += 1

        new_head = (head_x, head_y)

        if (
            head_x < 0
            or head_x >= GRID_WIDTH
            or head_y < 0
            or head_y >= GRID_HEIGHT
            or new_head in self.snake
        ):
            self.game_over()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.update_score()
            self.place_food()
            self.draw_food()
        else:
            self.snake.pop()

        self.draw_snake()
        self.root.after(UPDATE_DELAY, self.update)

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
