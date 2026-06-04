import tkinter as tk
import random

WIDTH = 640
HEIGHT = 480
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 12
BALL_SIZE = 14
BRICK_ROWS = 5
BRICK_COLS = 8
BRICK_WIDTH = 70
BRICK_HEIGHT = 20
BRICK_PADDING = 8
TOP_OFFSET = 50
LIVES = 3

class BreakoutGame:
    def __init__(self, root):
        self.root = root
        self.root.title("블럭깨기 게임")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#111")
        self.canvas.pack()

        self.score = 0
        self.lives = LIVES
        self.game_over = False

        self._create_bricks()
        self._create_paddle()
        self._create_ball()
        self._create_text()

        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        self.root.bind("<space>", self.restart)

        self._game_loop()

    def _create_bricks(self):
        self.bricks = []
        colors = ["#ff5f5f", "#ffaf3f", "#ffd75f", "#5fd7ff", "#5fff9f"]
        for row in range(BRICK_ROWS):
            brick_row = []
            y = TOP_OFFSET + row * (BRICK_HEIGHT + BRICK_PADDING)
            for col in range(BRICK_COLS):
                x = BRICK_PADDING + col * (BRICK_WIDTH + BRICK_PADDING)
                brick = self.canvas.create_rectangle(
                    x, y, x + BRICK_WIDTH, y + BRICK_HEIGHT,
                    fill=colors[row % len(colors)], outline="#222"
                )
                brick_row.append(brick)
            self.bricks.append(brick_row)

    def _create_paddle(self):
        x = (WIDTH - PADDLE_WIDTH) / 2
        y = HEIGHT - 40
        self.paddle = self.canvas.create_rectangle(
            x, y, x + PADDLE_WIDTH, y + PADDLE_HEIGHT,
            fill="#eee"
        )
        self.paddle_speed = 0

    def _create_ball(self):
        self.ball_x = WIDTH / 2
        self.ball_y = HEIGHT / 2
        self.ball = self.canvas.create_oval(
            self.ball_x - BALL_SIZE / 2,
            self.ball_y - BALL_SIZE / 2,
            self.ball_x + BALL_SIZE / 2,
            self.ball_y + BALL_SIZE / 2,
            fill="#fff"
        )
        self.ball_dx = random.choice([-4, 4])
        self.ball_dy = -4

    def _create_text(self):
        self.score_text = self.canvas.create_text(
            10, 10, anchor="nw", fill="#fff",
            font=("Helvetica", 14, "bold"), text=f"Score: {self.score}"
        )
        self.lives_text = self.canvas.create_text(
            WIDTH - 10, 10, anchor="ne", fill="#fff",
            font=("Helvetica", 14, "bold"), text=f"Lives: {self.lives}"
        )
        self.message_text = self.canvas.create_text(
            WIDTH / 2, HEIGHT / 2, fill="#fff",
            font=("Helvetica", 24, "bold"), text=""
        )

    def move_left(self, event):
        self.paddle_speed = -8

    def move_right(self, event):
        self.paddle_speed = 8

    def restart(self, event):
        if self.game_over:
            self.canvas.delete("all")
            self.score = 0
            self.lives = LIVES
            self.game_over = False
            self._create_bricks()
            self._create_paddle()
            self._create_ball()
            self._create_text()

    def _update_paddle(self):
        if self.paddle_speed == 0:
            return
        x1, y1, x2, y2 = self.canvas.coords(self.paddle)
        new_x1 = x1 + self.paddle_speed
        new_x2 = x2 + self.paddle_speed
        if new_x1 < 0:
            new_x1 = 0
            new_x2 = PADDLE_WIDTH
        if new_x2 > WIDTH:
            new_x2 = WIDTH
            new_x1 = WIDTH - PADDLE_WIDTH
        self.canvas.coords(self.paddle, new_x1, y1, new_x2, y2)

    def _update_ball(self):
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        self.canvas.move(self.ball, self.ball_dx, self.ball_dy)
        x1, y1, x2, y2 = self.canvas.coords(self.ball)

        if x1 <= 0 or x2 >= WIDTH:
            self.ball_dx *= -1
        if y1 <= 0:
            self.ball_dy *= -1

        if y2 >= HEIGHT:
            self.lives -= 1
            self.canvas.itemconfigure(self.lives_text, text=f"Lives: {self.lives}")
            if self.lives == 0:
                self._end_game(False)
            else:
                self._reset_ball()
            return

        if self._hit_paddle(x1, y1, x2, y2):
            self.ball_dy *= -1
            self.ball_y = y1 - BALL_SIZE / 2

        self._hit_brick(x1, y1, x2, y2)

    def _hit_paddle(self, x1, y1, x2, y2):
        paddle_coords = self.canvas.coords(self.paddle)
        return self._check_collision((x1, y1, x2, y2), paddle_coords)

    def _hit_brick(self, x1, y1, x2, y2):
        overlapping = self.canvas.find_overlapping(x1, y1, x2, y2)
        for item in overlapping:
            if item == self.paddle or item == self.ball:
                continue
            for row in self.bricks:
                if item in row:
                    self.canvas.delete(item)
                    row.remove(item)
                    self.score += 10
                    self.canvas.itemconfigure(self.score_text, text=f"Score: {self.score}")
                    self.ball_dy *= -1
                    if all(len(r) == 0 for r in self.bricks):
                        self._end_game(True)
                    return

    def _check_collision(self, rect1, rect2):
        left1, top1, right1, bottom1 = rect1
        left2, top2, right2, bottom2 = rect2
        return not (right1 < left2 or left1 > right2 or bottom1 < top2 or top1 > bottom2)

    def _reset_ball(self):
        self.canvas.coords(
            self.ball,
            WIDTH / 2 - BALL_SIZE / 2,
            HEIGHT / 2 - BALL_SIZE / 2,
            WIDTH / 2 + BALL_SIZE / 2,
            HEIGHT / 2 + BALL_SIZE / 2,
        )
        self.ball_x = WIDTH / 2
        self.ball_y = HEIGHT / 2
        self.ball_dx = random.choice([-4, 4])
        self.ball_dy = -4

    def _end_game(self, won):
        self.game_over = True
        message = "You Win! Press Space to Restart" if won else "Game Over! Press Space to Restart"
        self.canvas.itemconfigure(self.message_text, text=message)

    def _game_loop(self):
        if not self.game_over:
            self._update_paddle()
            self._update_ball()
        self.root.after(16, self._game_loop)

if __name__ == "__main__":
    root = tk.Tk()
    BreakoutGame(root)
    root.mainloop()
