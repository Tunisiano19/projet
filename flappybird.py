import pygame, sys, random

# --- Initialization ---
pygame.init()
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Mini")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 40, bold=True)

# --- Game constants ---
GRAVITY = 0.5
JUMP_STRENGTH = -10
PIPE_SPEED = 5
PIPE_GAP = 170
PIPE_WIDTH = 80
FLOOR_HEIGHT = 100

# --- Colors ---
SKY_TOP = (135, 206, 250)
SKY_BOTTOM = (70, 130, 180)
PIPE_COLOR = (34, 139, 34)
PIPE_BORDER = (0, 100, 0)
FLOOR_TOP = (85, 107, 47)
FLOOR_BOTTOM = (139, 69, 19)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (255, 100, 100)
BUTTON_HOVER = (255, 180, 180)

# --- Bird (image) ---
bird_surface = pygame.image.load("bird.png").convert_alpha()
bird_surface = pygame.transform.scale(bird_surface, (50, 40))
bird_rect = bird_surface.get_rect(center=(WIDTH//4, HEIGHT//2))
bird_movement = 0

# --- Pipes ---
pipe_list = []

def create_pipe():
    pipe_height = random.randint(150, 400)
    bottom_pipe = pygame.Rect(WIDTH + 100, pipe_height, PIPE_WIDTH, HEIGHT - pipe_height - FLOOR_HEIGHT)
    top_pipe = pygame.Rect(WIDTH + 100, 0, PIPE_WIDTH, pipe_height - PIPE_GAP)
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.x -= PIPE_SPEED
    return [pipe for pipe in pipes if pipe.right > 0]

def draw_pipes(pipes):
    for pipe in pipes:
        pygame.draw.rect(win, PIPE_COLOR, pipe)
        pygame.draw.rect(win, PIPE_BORDER, pipe, 4)

def check_collision(pipes, bird_rect):
    if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT - FLOOR_HEIGHT:
        return False
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return False
    return True

# --- Score ---
score = 0
high_score = 0

def draw_text(text, size, color, center):
    surface = pygame.font.SysFont("Arial", size, bold=True).render(text, True, color)
    rect = surface.get_rect(center=center)
    win.blit(surface, rect)

# --- Background (clouds) ---
clouds = []
for i in range(6):
    cx = random.randint(0, WIDTH)
    cy = random.randint(50, 250)
    size = random.randint(30, 60)
    speed = random.uniform(0.5, 2)  # different speeds for parallax effect
    clouds.append([cx, cy, size, speed])

def draw_background():
    # Sky gradient
    for i in range(HEIGHT):
        ratio = i / HEIGHT
        r = SKY_TOP[0] * (1 - ratio) + SKY_BOTTOM[0] * ratio
        g = SKY_TOP[1] * (1 - ratio) + SKY_BOTTOM[1] * ratio
        b = SKY_TOP[2] * (1 - ratio) + SKY_BOTTOM[2] * ratio
        pygame.draw.line(win, (int(r), int(g), int(b)), (0, i), (WIDTH, i))

    # Clouds (elliptical blobs for realism)
    for cloud in clouds:
        cx, cy, size, speed = cloud
        color = (255, 255, 255)
        pygame.draw.ellipse(win, color, (cx, cy, size*2, size))
        pygame.draw.ellipse(win, color, (cx - size//2, cy + 10, size*2, size))
        pygame.draw.ellipse(win, color, (cx + size//2, cy + 10, size*2, size))

        cloud[0] -= speed
        if cloud[0] < -200:
            cloud[0] = WIDTH + 200
            cloud[1] = random.randint(50, 250)
            cloud[2] = random.randint(30, 60)
            cloud[3] = random.uniform(0.5, 2)

# --- Floor ---
floor_x = 0
def draw_floor():
    global floor_x
    floor_x -= PIPE_SPEED
    if floor_x <= -WIDTH:
        floor_x = 0
    pygame.draw.rect(win, FLOOR_BOTTOM, (0, HEIGHT - FLOOR_HEIGHT, WIDTH, FLOOR_HEIGHT))
    pygame.draw.rect(win, FLOOR_TOP, (floor_x, HEIGHT - FLOOR_HEIGHT, WIDTH, 30))
    pygame.draw.rect(win, FLOOR_TOP, (floor_x + WIDTH, HEIGHT - FLOOR_HEIGHT, WIDTH, 30))

# --- Auto bot logic ---
def auto_flap(pipe_list, bird_rect, bird_movement):
    """Smarter bot that always aims for the middle of the next pipe gap"""
    if pipe_list:
        next_pipe = None
        for pipe in pipe_list:
            if pipe.centerx > bird_rect.centerx:
                next_pipe = pipe
                break
        if next_pipe:
            if next_pipe.y == 0:  # top pipe
                gap_center = next_pipe.bottom + PIPE_GAP // 2
            else:  # bottom pipe
                gap_center = next_pipe.top - PIPE_GAP // 2
            if bird_rect.centery > gap_center or bird_movement > 5:
                bird_movement = JUMP_STRENGTH
    return bird_movement

# --- Buttons ---
def draw_button(text, center, w=250, h=60):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(0, 0, w, h)
    rect.center = center
    if rect.collidepoint(mouse):
        pygame.draw.rect(win, BUTTON_HOVER, rect, border_radius=15)
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(win, BUTTON_COLOR, rect, border_radius=15)
    draw_text(text, 30, (0, 0, 0), rect.center)
    return False

# --- Screens ---
def home_screen():
    while True:
        draw_background()
        draw_text("🎮 Flappy Bird Mini 🎮", 50, (255, 255, 0), (WIDTH//2, HEIGHT//2 - 120))
        if draw_button("Play in Auto Mode", (WIDTH//2, HEIGHT//2 - 20)):
            return "auto"
        if draw_button("Play in Manual Mode", (WIDTH//2, HEIGHT//2 + 60)):
            return "manual"
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def game_over_screen(last_score, high_score):
    while True:
        draw_background()
        draw_text("Game Over!", 50, (255, 50, 50), (WIDTH//2, HEIGHT//2 - 120))
        draw_text(f"Score: {int(last_score)}", 40, TEXT_COLOR, (WIDTH//2, HEIGHT//2 - 50))
        draw_text(f"High Score: {int(high_score)}", 35, TEXT_COLOR, (WIDTH//2, HEIGHT//2))
        if draw_button("🏠 Return Home", (WIDTH//2, HEIGHT//2 + 100)):
            return
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

# --- Main game ---
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1500)

while True:
    mode = home_screen()
    game_active = True
    waiting_start = (mode == "manual")
    pipe_list.clear()
    bird_rect.center = (WIDTH//4, HEIGHT//2)
    bird_movement = 0
    score = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_active and mode == "manual":
                    if waiting_start:
                        waiting_start = False  # start the game
                    bird_movement = JUMP_STRENGTH
            if event.type == SPAWNPIPE and game_active and not waiting_start:
                pipe_list.extend(create_pipe())

        draw_background()

        if game_active:
            if waiting_start:
                draw_text("Press SPACE to start!", 35, (255, 255, 0), (WIDTH//2, HEIGHT//2))
            else:
                bird_movement += GRAVITY
                if mode == "auto":
                    bird_movement = auto_flap(pipe_list, bird_rect, bird_movement)
                bird_rect.centery += bird_movement

            # Bird
            rotated_bird = pygame.transform.rotozoom(bird_surface, -bird_movement * 2, 1)
            win.blit(rotated_bird, bird_rect)

            # Pipes
            if not waiting_start:
                pipe_list = move_pipes(pipe_list)
            draw_pipes(pipe_list)

            # Collision
            if not waiting_start:
                game_active = check_collision(pipe_list, bird_rect)

            # Score
            if not waiting_start:
                score += 0.01
                draw_text(str(int(score)), 50, TEXT_COLOR, (WIDTH//2, 50))
        else:
            high_score = max(score, high_score)
            pygame.display.update()
            game_over_screen(score, high_score)
            break

        draw_floor()
        pygame.display.update()
        clock.tick(60)
