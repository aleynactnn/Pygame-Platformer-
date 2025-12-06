import pgzrun

WIDTH = 800
HEIGHT = 600
Y0 = 300

MUSHROOM_FRAMES = {
    "idle": [f"player/idle/idle_{i}" for i in range(1, 9)],
    "run": [f"player/run/walk_{i}" for i in range(1, 8)],
    "jump": [f"player/jump/jump_{i}" for i in range(1, 7)],
}
FROG_FRAMES = [f"enemies/{i:02d}" for i in range(1, 10)]
COIN_FRAMES = [f"items/{i}" for i in range(1, 4)]

score = 0
camera_x = 0
camera_y = 0
game_state = "menu"
sound_on = True
music_on = True
left_boundary = 500
right_boundary = 1950
boxes = []

class Character:
    def __init__(self, frames, position, animation_speed=0.2):
        self.frames = frames
        self.current_animation = "idle"
        self.frame_indices = {"idle": 0, "run": 0, "jump": 0}
        self.animation_timer = 0
        self.animation_speed = animation_speed
        self.actor = Actor(self.frames[self.current_animation][0], position)

    def update_animation(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_indices[self.current_animation] = (self.frame_indices[self.current_animation] + 1) % len(self.frames[self.current_animation])
            self.actor.image = self.frames[self.current_animation][self.frame_indices[self.current_animation]]

    def set_animation(self, animation_name):
        if self.current_animation != animation_name:
            self.current_animation = animation_name
            self.frame_indices[self.current_animation] = 0
            self.actor.image = self.frames[self.current_animation][0]

    def draw(self, screen, camera_x, camera_y):
        x = self.actor.x - camera_x
        y = self.actor.y - camera_y
        screen.blit(self.actor.image,(x, y))


class Mushroom(Character):
    def __init__(self, position):
        super().__init__(MUSHROOM_FRAMES, position)
        self.gravity = 0

    def update(self, dt):
        if self.gravity != 0:
            self.set_animation("jump")
        elif not (keyboard.left or keyboard.right):
            self.set_animation("idle")
        else:
            self.set_animation("run")

        self.update_animation(dt)

        if keyboard.left:
            new_x = self.actor.x-2
            if new_x > left_boundary:
                self.actor.x = new_x
        if keyboard.right:
            new_x = self.actor.x + 2
            if new_x < right_boundary:
                self.actor.x = new_x

        if keyboard.up and self.gravity == 0:
            self.set_animation("jump")
            self.gravity = 8

        if self.gravity != 0:
            new_y = self.actor.y - self.gravity
            self.actor.y = new_y
            self.gravity -= dt * 10

            if self.actor.y >= Y0 - 15:
                self.actor.y = Y0 - 15
                self.gravity = 0
class Frog:
    def __init__(self, x, y, points):
        self.actor = Actor(FROG_FRAMES[0], (x, y))
        self.image_index = 0
        self.animation_timer = 0
        self.points = points
        self.patrol_point_index = 0
        self.speed = 1

    def update(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= 0.2:
            self.animation_timer = 0
            self.image_index = (self.image_index + 1) % len(FROG_FRAMES)
            self.actor.image = FROG_FRAMES[self.image_index]

        target_x = self.points[self.patrol_point_index]
        diff_x = target_x - self.actor.x
        distance = abs(diff_x)

        if distance > self.speed:
            self.actor.x += self.speed * (diff_x / distance)
        else:
            self.patrol_point_index = (self.patrol_point_index + 1) % len(self.points)

    def draw(self, screen, camera_x, camera_y):
        x = self.actor.x - camera_x
        y = self.actor.y - camera_y
        screen.blit(self.actor.image, (x, y))

class Coin:
    def __init__(self, x, y):
        self.actor = Actor(COIN_FRAMES[0], (x, y))
        self.image_index = 0
        self.animation_timer = 0

    def update(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= 0.2:
            self.animation_timer = 0
            self.image_index = (self.image_index + 1) % len(COIN_FRAMES)
            self.actor.image = COIN_FRAMES[self.image_index]

    def draw(self, screen, camera_x, camera_y):
        x = self.actor.x - camera_x
        y = self.actor.y - camera_y
        screen.blit(self.actor.image, (x, y))

mushroom = None
frogs = []
coins = []

def start_game():
    global mushroom, frogs, coins, boxes, score, camera_x, camera_y, left_boundary, right_boundary

    mushroom = Mushroom((200, Y0 - 15))
    score = 0
    camera_x = 0
    camera_y = 0
    left_boundary = 40
    right_boundary = 1950

    frogs = []
    for i in range(5):
        points = [400 + i * 300, 600 + i * 300]
        frog = Frog(400 + i * 300, Y0 + 10, points)
        frogs.append(frog)

    coins = []
    for i in range(5):
        coin = Coin(600 + i * 300, Y0)
        coins.append(coin)

    boxes = []
    for i in range(100):
        box1 = Actor("tiles/floor2.png", (i * 64, Y0 + 45))
        box2 = Actor("tiles/floor1.png", (i * 64, Y0 + 25))
        boxes.append(box1)
        boxes.append(box2)

    for i in range(10):
        y = Y0 + 25 - (i * 64)
        left_wall = Actor("tiles/floor2.png", (-200, y))
        right_wall = Actor("tiles/floor2.png", (2000, y))
        boxes.append(left_wall)
        boxes.append(right_wall)

def draw():
    screen.clear()

    if game_state == "menu":
        screen.blit("menu_background", (0, 0))
        screen.draw.text("Play", center=(400, 275), fontsize=30, color="black")
        screen.draw.text("Sound: ON" if sound_on else "Sound: OFF", center=(400, 325), fontsize=30, color="black")
        screen.draw.text("Music: ON" if music_on else "Music: OFF", center=(400, 375), fontsize=30, color="black")
        screen.draw.text("Exit", center=(400, 425), fontsize=30, color="black")

    elif game_state == "game":
        screen.blit("background.png", (0, 0))

        for box in boxes:
            box_x = box.x - camera_x
            box_y = box.y - camera_y
            screen.blit(box.image, (box_x, box_y))

        mushroom.draw(screen, camera_x, camera_y)

        for frog in frogs:
            frog.draw(screen, camera_x, camera_y)

        for coin in coins:
            coin.draw(screen, camera_x, camera_y)

        screen.draw.text(f"Score: {score}", center=(WIDTH // 2, 30), fontsize=40, color="black")

    elif game_state == "game_over":
        screen.draw.text("GAME OVER!", center=(400, 300), fontsize=50, color="orange")
        screen.draw.text("Click mouse to return to the main menu", center=(400, 350), fontsize=30, color="brown")

    elif game_state == "win":
        screen.draw.text("YOU WIN YAYY!", center=(400, 300), fontsize=50, color="green")
        screen.draw.text("Click mouse to return to the main menu", center=(400, 350), fontsize=30, color="white")

def update(dt):
    global score, camera_x, camera_y, game_state

    if game_state == "game":
        mushroom.update(dt)
        camera_x = mushroom.actor.x - (WIDTH // 2)
        camera_y = mushroom.actor.y - (HEIGHT // 2)

        for frog in frogs:
            frog.update(dt)
            if mushroom.actor.colliderect(frog.actor):
                game_state = "game_over"
                return

        for coin in coins[:]:
            coin.update(dt)
            if mushroom.actor.colliderect(coin.actor):
                coins.remove(coin)
                score += 1
                if sound_on:
                    sounds.handle_coins.play()

        if score >= 5:
            game_state = "win"

def on_mouse_down(pos):
    global game_state, sound_on, music_on

    if game_state == "menu":
        play_button = Rect((300, 250), (200, 50))
        sound_button = Rect((300, 300), (200, 50))
        music_button = Rect((300, 350), (200, 50))
        exit_button = Rect((300, 400), (200, 50))

        if play_button.collidepoint(pos):
            start_game()
            game_state = "game"
        elif sound_button.collidepoint(pos):
            sound_on = not sound_on
        elif music_button.collidepoint(pos):
            music_on = not music_on
            if music_on:
                sounds.exploration.play(-1)
            else:
                sounds.exploration.stop()
        elif exit_button.collidepoint(pos):
            exit()

    elif game_state == "game_over" or game_state == "win":
        game_state = "menu"

start_game()
if music_on:
    sounds.exploration.play(-1)

pgzrun.go()
