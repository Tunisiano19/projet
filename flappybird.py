import pygame, sys, random

# --- Initialization ---
pygame.init()
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Mini — Auto Fix")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 40, bold=True)

# --- Game constants ---
FPS = 60
GRAVITY = 0.5             # pixels/frame^2
JUMP_STRENGTH = -10       # set vertical velocity on flap (pixels/frame)
PIPE_SPEED = 5            # pixels/frame
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
BUTTON_COLOR = (255, 200, 100)
BUTTON_HOVER = (255, 230, 180)

# --- Bird (image) ---
bird_surface = pygame.image.load("bird.png").convert_alpha()
bird_surface = pygame.transform.scale(bird_surface, (50, 40))
bird_rect = bird_surface.get_rect(center=(WIDTH//4, HEIGHT//2))
bird_movement = 0

# --- Pipes stored as pairs (bottom, top) ---
pipe_pairs = []

def create_pipe():
    pipe_height = random.randint(150, 400)
    bottom_pipe = pygame.Rect(WIDTH + 100, pipe_height, PIPE_WIDTH, HEIGHT - pipe_height - FLOOR_HEIGHT)
    top_pipe = pygame.Rect(WIDTH + 100, 0, PIPE_WIDTH, pipe_height - PIPE_GAP)
    return bottom_pipe, top_pipe

def move_pipes(pairs):
    for bottom, top in pairs:
        bottom.x -= PIPE_SPEED
        top.x -= PIPE_SPEED
    return [pair for pair in pairs if pair[0].right > 0]

def draw_pipes(pairs):
    for bottom, top in pairs:
        pygame.draw.rect(win, PIPE_COLOR, bottom, border_radius=10)
        pygame.draw.rect(win, PIPE_BORDER, bottom, 4, border_radius=10)
        pygame.draw.rect(win, PIPE_COLOR, top, border_radius=10)
        pygame.draw.rect(win, PIPE_BORDER, top, 4, border_radius=10)

def check_collision(pairs, bird_rect):
    if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT - FLOOR_HEIGHT:
        return False
    for bottom, top in pairs:
        if bird_rect.colliderect(bottom) or bird_rect.colliderect(top):
            return False
    return True

# --- Score ---
score = 0
high_score = 0

def draw_text(text, size, color, center):
    surface = pygame.font.SysFont("Arial", size, bold=True).render(text, True, color)
    rect = surface.get_rect(center=center)
    win.blit(surface, rect)

# --- Clouds (smooth, parallax) ---
clouds = []
for i in range(6):
    cx = random.randint(0, WIDTH)
    cy = random.randint(50, 250)
    size = random.randint(30, 60)
    speed = random.uniform(0.5, 2)
    clouds.append([cx, cy, size, speed])

def draw_background():
    # Sky gradient
    for i in range(HEIGHT):
        ratio = i / HEIGHT
        r = SKY_TOP[0] * (1 - ratio) + SKY_BOTTOM[0] * ratio
        g = SKY_TOP[1] * (1 - ratio) + SKY_BOTTOM[1] * ratio
        b = SKY_TOP[2] * (1 - ratio) + SKY_BOTTOM[2] * ratio
        pygame.draw.line(win, (int(r), int(g), int(b)), (0, i), (WIDTH, i))

    # Clouds (ellipses, parallax)
    for cloud in clouds:
        cx, cy, size, speed = cloud
        pygame.draw.ellipse(win, (255, 255, 255), (cx, cy, size*2, size))
        pygame.draw.ellipse(win, (255, 255, 255), (cx - size//2, cy + 10, size*2, size))
        pygame.draw.ellipse(win, (255, 255, 255), (cx + size//2, cy + 10, size*2, size))
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

# --- Smarter Auto decision (predictive) ---
# This function returns True when the bot should flap this frame.
def auto_should_flap(pairs, bird_rect, bird_v):
    """
    Predictive and stable auto-flap:
    - Only flap if bird is below the target gap minus margin
    - Do not flap if bird is above the gap
    """
    # Find next pipe
    next_pair = None
    min_dx = float("inf")
    for bottom, top in pairs:
        dx = bottom.centerx - bird_rect.centerx
        if dx > 0 and dx < min_dx:
            min_dx = dx
            next_pair = (bottom, top)

    if not next_pair:
        return False  # No pipe ahead

    bottom, top = next_pair
    gap_center = (top.bottom + bottom.top) / 2.0

    # Margin to avoid overshooting
    margin = PIPE_GAP * 0.15

    # If bird is too high, do nothing
    if bird_rect.centery < gap_center - margin:
        return False

    # If bird is too low, flap
    if bird_rect.centery > gap_center + margin:
        return True

    # If bird is within margin, let gravity do its job
    return False

# --- Buttons (auto-size to text) ---
def draw_button(text, center):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    surface = FONT.render(text, True, (0, 0, 0))
    w, h = surface.get_size()
    rect = pygame.Rect(0, 0, w + 40, h + 20)
    rect.center = center

    if rect.collidepoint(mouse):
        pygame.draw.rect(win, BUTTON_HOVER, rect, border_radius=15)
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(win, BUTTON_COLOR, rect, border_radius=15)

    win.blit(surface, surface.get_rect(center=rect.center))
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
        draw_text("💀 Game Over! 💀", 50, (255, 50, 50), (WIDTH//2, HEIGHT//2 - 120))
        draw_text(f"Score: {int(last_score)}", 40, TEXT_COLOR, (WIDTH//2, HEIGHT//2 - 50))
        draw_text(f"High Score: {int(high_score)}", 35, TEXT_COLOR, (WIDTH//2, HEIGHT//2))
        if draw_button("🏠 Return Home", (WIDTH//2, HEIGHT//2 + 100)):
            return
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

# --- Main loop & timers ---
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1500)

while True:
    mode = home_screen()
    game_active = True
    waiting_start = (mode == "manual")     # manual waits for your first press
    pipe_pairs.clear()
    bird_rect.center = (WIDTH//4, HEIGHT//2)
    bird_movement = 0
    score = 0
    # cooldown between programmed flaps (frames) so we don't spam every frame
    auto_flap_cooldown = 0

    while True:
        # --- events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_active and mode == "manual":
                    if waiting_start:
                        waiting_start = False  # start game on first space
                    bird_movement = JUMP_STRENGTH

            if event.type == SPAWNPIPE and game_active and not waiting_start:
                pipe_pairs.append(create_pipe())

        # --- background ---
        draw_background()

        if game_active:
            if waiting_start:
                draw_text("Press SPACE to start!", 35, (255, 255, 0), (WIDTH//2, HEIGHT//2))
            else:
                # physics
                bird_movement += GRAVITY

                # AUTO MODE: decide whether to flap (predictive)
                if mode == "auto":
                    if auto_flap_cooldown > 0:
                        auto_flap_cooldown -= 1
                    should = auto_should_flap(pipe_pairs, bird_rect, bird_movement)
                    if should and auto_flap_cooldown == 0:
                        bird_movement = JUMP_STRENGTH
                        auto_flap_cooldown = 4   # small cooldown (frames)

                # apply vertical movement
                bird_rect.centery += bird_movement

            # draw bird
            rotated_bird = pygame.transform.rotozoom(bird_surface, -bird_movement * 2, 1)
            win.blit(rotated_bird, bird_rect)

            # pipes (only move when not waiting)
            if not waiting_start:
                pipe_pairs = move_pipes(pipe_pairs)
            draw_pipes(pipe_pairs)

            # collision (only check after started)
            if not waiting_start:
                game_active = check_collision(pipe_pairs, bird_rect)

            # score
            if not waiting_start:
                score += 0.01
                draw_text(str(int(score)), 50, TEXT_COLOR, (WIDTH//2, 50))

        else:
            # game over -> show game over screen and return to home
            high_score = max(score, high_score)
            pygame.display.update()
            game_over_screen(score, high_score)
            break

        # floor & flip
        draw_floor()
        pygame.display.update()
        clock.tick(FPS)
