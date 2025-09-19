import pygame, sys, random

# --- Initialization ---
pygame.init()
WIDTH, HEIGHT = 1920, 1080
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird HD")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 50, bold=True)

# --- Game constants ---
GRAVITY = 0.5
JUMP_STRENGTH = -10
PIPE_SPEED = 6
PIPE_GAP = 250
PIPE_WIDTH = 100
FLOOR_HEIGHT = 150

# --- Colors ---
SKY_TOP = (135, 206, 250)     # lighter blue
SKY_BOTTOM = (70, 130, 180)   # darker blue
PIPE_COLOR = (34, 139, 34)    # forest green
PIPE_BORDER = (0, 100, 0)
FLOOR_TOP = (85, 107, 47)
FLOOR_BOTTOM = (139, 69, 19)
TEXT_COLOR = (255, 255, 255)

# --- Bird (use image) ---
bird_surface = pygame.image.load("bird.png").convert_alpha()
bird_surface = pygame.transform.scale(bird_surface, (80, 60))  # upscale for 1080p
bird_rect = bird_surface.get_rect(center=(WIDTH//4, HEIGHT//2))
bird_movement = 0

# --- Pipes ---
pipe_list = []

def create_pipe():
    """Return rects for a new top and bottom pipe."""
    pipe_height = random.randint(300, 700)
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
        pygame.draw.rect(win, PIPE_BORDER, pipe, 6)

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

# --- Background ---
clouds = []
for i in range(5):
    cx = random.randint(0, WIDTH)
    cy = random.randint(100, 400)
    size = random.randint(50, 120)
    clouds.append([cx, cy, size])

def draw_background(scroll):
    # Sky gradient
    for i in range(HEIGHT):
        ratio = i / HEIGHT
        r = SKY_TOP[0] * (1 - ratio) + SKY_BOTTOM[0] * ratio
        g = SKY_TOP[1] * (1 - ratio) + SKY_BOTTOM[1] * ratio
        b = SKY_TOP[2] * (1 - ratio) + SKY_BOTTOM[2] * ratio
        pygame.draw.line(win, (int(r), int(g), int(b)), (0, i), (WIDTH, i))

    # Moving clouds
    for cloud in clouds:
        cx, cy, size = cloud
        pygame.draw.circle(win, (255, 255, 255), (cx, cy), size)
        pygame.draw.circle(win, (255, 255, 255), (cx+size, cy+20), size//1.5)
        pygame.draw.circle(win, (255, 255, 255), (cx-size, cy+20), size//1.5)
        cloud[0] -= 1  # move left
        if cloud[0] < -200:
            cloud[0] = WIDTH + 200
            cloud[1] = random.randint(100, 400)

# --- Floor ---
floor_x = 0
def draw_floor():
    global floor_x
    floor_x -= PIPE_SPEED
    if floor_x <= -WIDTH:
        floor_x = 0
    pygame.draw.rect(win, FLOOR_BOTTOM, (0, HEIGHT - FLOOR_HEIGHT, WIDTH, FLOOR_HEIGHT))
    pygame.draw.rect(win, FLOOR_TOP, (floor_x, HEIGHT - FLOOR_HEIGHT, WIDTH, 40))
    pygame.draw.rect(win, FLOOR_TOP, (floor_x + WIDTH, HEIGHT - FLOOR_HEIGHT, WIDTH, 40))

# --- Game loop ---
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1500)

game_active = True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_movement = JUMP_STRENGTH
            if event.key == pygame.K_SPACE and not game_active:
                # Reset game
                game_active = True
                pipe_list.clear()
                bird_rect.center = (WIDTH//4, HEIGHT//2)
                bird_movement = 0
                score = 0

        if event.type == SPAWNPIPE and game_active:
            pipe_list.extend(create_pipe())

    # --- Background ---
    draw_background(scroll=True)

    if game_active:
        # Bird physics
        bird_movement += GRAVITY
        bird_rect.centery += bird_movement

        # Draw Bird
        rotated_bird = pygame.transform.rotozoom(bird_surface, -bird_movement * 2, 1)
        win.blit(rotated_bird, bird_rect)

        # Pipes
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        # Collision
        game_active = check_collision(pipe_list, bird_rect)

        # Score
        score += 0.01
        draw_text(str(int(score)), 70, TEXT_COLOR, (WIDTH//2, 100))

    else:
        # Update high score
        high_score = max(score, high_score)
        draw_text(f"Score: {int(score)}", 60, TEXT_COLOR, (WIDTH//2, HEIGHT//2 - 80))
        draw_text(f"High Score: {int(high_score)}", 50, TEXT_COLOR, (WIDTH//2, HEIGHT//2))
        draw_text("Press SPACE to restart", 40, (255, 255, 0), (WIDTH//2, HEIGHT//2 + 80))

    # Floor
    draw_floor()

    pygame.display.update()
    clock.tick(60)
    