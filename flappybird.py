import pygame, sys, random

# --- Flappy Bird Mini  ---

pygame.init()
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Mini")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 36, bold=True)

# --- Constants ---
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -10
BASE_PIPE_SPEED = 5
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

# --- Resources ---
# Make sure 'bird.png' exists in the same folder as this script.
bird_surface = pygame.image.load("bird.png").convert_alpha()
bird_surface = pygame.transform.scale(bird_surface, (50, 40))
bird_rect = bird_surface.get_rect(center=(WIDTH // 4, HEIGHT // 2))

# --- Helper: Pipes ---
def create_pipe(gap=PIPE_GAP):
    pipe_height = random.randint(150, 400)
    bottom_pipe = pygame.Rect(WIDTH + 100, pipe_height, PIPE_WIDTH, HEIGHT - pipe_height - FLOOR_HEIGHT)
    top_pipe = pygame.Rect(WIDTH + 100, 0, PIPE_WIDTH, pipe_height - gap)
    return bottom_pipe, top_pipe

def move_pipes(pairs, speed):
    for bottom, top in pairs:
        bottom.x -= speed
        top.x -= speed
    return [pair for pair in pairs if pair[0].right > -50]

def draw_pipes(pairs):
    for bottom, top in pairs:
        pygame.draw.rect(win, PIPE_COLOR, bottom, border_radius=10)
        pygame.draw.rect(win, PIPE_BORDER, bottom, 4, border_radius=10)
        pygame.draw.rect(win, PIPE_COLOR, top, border_radius=10)
        pygame.draw.rect(win, PIPE_BORDER, top, 4, border_radius=10)

# --- Collision check (used only in manual mode) ---
def check_collision(pairs, bird_rect):
    if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT - FLOOR_HEIGHT:
        return False
    for bottom, top in pairs:
        if bird_rect.colliderect(bottom) or bird_rect.colliderect(top):
            return False
    return True

# --- UI: buttons ---
def draw_button(text, center):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    surface = FONT.render(text, True, (0, 0, 0))
    w, h = surface.get_size()
    rect = pygame.Rect(0, 0, w + 26, h + 14)
    rect.center = center

    if rect.collidepoint(mouse):
        pygame.draw.rect(win, BUTTON_HOVER, rect, border_radius=12)
        if click[0] == 1:
            # naive: returns True while mouse pressed; acceptable for menu clicks
            return True
    else:
        pygame.draw.rect(win, BUTTON_COLOR, rect, border_radius=12)

    win.blit(surface, surface.get_rect(center=rect.center))
    return False

# --- Background / floor ---
clouds = []
for i in range(6):
    clouds.append([random.randint(0, WIDTH), random.randint(50, 250), random.randint(30, 60), random.uniform(0.5, 2)])

def draw_background():
    # gradient sky
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(SKY_TOP[0] * (1 - t) + SKY_BOTTOM[0] * t)
        g = int(SKY_TOP[1] * (1 - t) + SKY_BOTTOM[1] * t)
        b = int(SKY_TOP[2] * (1 - t) + SKY_BOTTOM[2] * t)
        pygame.draw.line(win, (r, g, b), (0, y), (WIDTH, y))

    # clouds
    for c in clouds:
        cx, cy, size, speed = c
        pygame.draw.ellipse(win, (255, 255, 255), (cx, cy, size*2, size))
        cx -= speed
        c[0] = cx
        if cx < -200:
            c[0] = WIDTH + 200
            c[1] = random.randint(50, 250)
            c[2] = random.randint(30, 60)
            c[3] = random.uniform(0.5, 2)

floor_x = 0
def draw_floor(speed_x):
    global floor_x
    floor_x -= speed_x
    if floor_x <= -WIDTH:
        floor_x = 0
    pygame.draw.rect(win, FLOOR_BOTTOM, (0, HEIGHT - FLOOR_HEIGHT, WIDTH, FLOOR_HEIGHT))
    pygame.draw.rect(win, FLOOR_TOP, (floor_x, HEIGHT - FLOOR_HEIGHT, WIDTH, 30))
    pygame.draw.rect(win, FLOOR_TOP, (floor_x + WIDTH, HEIGHT - FLOOR_HEIGHT, WIDTH, 30))

# --- Screens ---
def home_screen():
    while True:
        draw_background()
        draw_text = FONT.render("Flappy Bird Mini", True, (255, 255, 0))
        win.blit(draw_text, draw_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 120)))

        if draw_button("Play in Auto Mode", (WIDTH//2, HEIGHT//2 - 20)):
            return "auto"
        if draw_button("Play in Manual Mode", (WIDTH//2, HEIGHT//2 + 60)):
            return "manual"

        pygame.display.update()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

def game_over_screen(last_score, high_score):
    while True:
        draw_background()
        title = FONT.render("Game Over!", True, (255, 50, 50))
        win.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 120)))

        s1 = FONT.render(f"Score: {int(last_score)}", True, TEXT_COLOR)
        s2 = FONT.render(f"High Score: {int(high_score)}", True, TEXT_COLOR)
        win.blit(s1, s1.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
        win.blit(s2, s2.get_rect(center=(WIDTH//2, HEIGHT//2 + 10)))

        if draw_button("Return Home", (WIDTH//2, HEIGHT//2 + 100)):
            return "home"
        if draw_button("Play Again", (WIDTH//2, HEIGHT//2 + 160)):
            return "retry"

        pygame.display.update()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

# --- Auto controller ---
def auto_controller(bird_rect, bird_v, pairs, pipe_speed, gap=PIPE_GAP):
    # if no pipes yet, gently move bird toward vertical center
    if not pairs:
        target = HEIGHT // 2
        error = target - bird_rect.centery
        # gentle approach
        desired = error * 0.04
        # smoothing
        new_v = bird_v * 0.85 + desired * 0.15
        max_step = 8
        new_v = max(-max_step, min(max_step, new_v))
        bird_rect.centery += new_v
        return new_v

    # find next pipe
    next_pipe = None
    min_dx = float('inf')
    for bottom, top in pairs:
        dx = bottom.centerx - bird_rect.centerx
        if dx > 0 and dx < min_dx:
            min_dx = dx
            next_pipe = (bottom, top)

    if not next_pipe:
        # same as no pipes
        return auto_controller(bird_rect, bird_v, [], pipe_speed, gap)

    bottom, top = next_pipe
    gap_center = (top.bottom + bottom.top) / 2.0

    # estimate frames until we reach the pipe
    frames_ahead = max(1.0, min_dx / max(1.0, pipe_speed))

    # desired per-frame move to reach gap center roughly in frames_ahead
    error = gap_center - bird_rect.centery
    desired_per_frame = error / frames_ahead

    # add some anticipation (aim slightly above center if speed increasing)
    # clamp and smooth
    max_step = 10 + pipe_speed * 0.5
    desired_per_frame = max(-max_step, min(max_step, desired_per_frame))

    # smooth velocity blending to avoid jitter
    new_v = bird_v * 0.7 + desired_per_frame * 0.3
    # safety clamp
    new_v = max(-max_step, min(max_step, new_v))

    # apply movement
    bird_rect.centery += new_v

    # keep bird inside reasonable bounds (don't fly out of screen)
    if bird_rect.centery < 20:
        bird_rect.centery = 20
        new_v = 0
    if bird_rect.bottom > HEIGHT - FLOOR_HEIGHT - 2:
        bird_rect.bottom = HEIGHT - FLOOR_HEIGHT - 2
        new_v = 0

    return new_v

# --- Main game runner ---
SPAWNPIPE = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWNPIPE, 1500)

high_score = 0

def run_game(mode):
    global high_score
    # game state
    pipe_pairs = []
    bird_rect.center = (WIDTH // 4, HEIGHT // 2)
    bird_v = 0.0
    score = 0.0
    running = True
    waiting_start = (mode == "manual")
    pipe_speed = BASE_PIPE_SPEED

    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    # instant exit to home
                    return "home"
                if ev.key == pygame.K_SPACE and mode == "manual":
                    if waiting_start:
                        waiting_start = False
                    bird_v = JUMP_STRENGTH
            if ev.type == SPAWNPIPE and not waiting_start:
                pipe_pairs.append(create_pipe())

        draw_background()

        if waiting_start:
            # waiting to start - show message
            text = FONT.render("Press SPACE to start!", True, (255, 255, 0))
            win.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))
        else:
            if mode == "manual":
                # normal physics
                bird_v += GRAVITY
                bird_rect.centery += bird_v
            else:
                # AUTO MODE: position controller drives bird; collisions ignored
                bird_v = auto_controller(bird_rect, bird_v, pipe_pairs, pipe_speed, PIPE_GAP)

                # Draw an Exit Auto button (bottom-right)
                if draw_button("Exit Auto Mode", (WIDTH - 120, HEIGHT - 40)):
                    return "home"

        # draw bird (rotate for feel)
        rotated = pygame.transform.rotozoom(bird_surface, -bird_v * 2.5, 1.0)
        bird_draw_rect = rotated.get_rect(center=bird_rect.center)
        win.blit(rotated, bird_draw_rect)

        # move & draw pipes (always move)
        pipe_pairs = move_pipes(pipe_pairs, pipe_speed)
        draw_pipes(pipe_pairs)

        # scoring only increments when pipes are present
        if not waiting_start:
            score += 0.01
            # difficulty scaling
            pipe_speed = BASE_PIPE_SPEED + int(score // 20)

        # collisions only matter in manual mode
        if mode == "manual" and not waiting_start:
            alive = check_collision(pipe_pairs, bird_rect)
        else:
            alive = True  # Auto mode cannot die

        # draw score
        score_surf = FONT.render(str(int(score)), True, TEXT_COLOR)
        win.blit(score_surf, score_surf.get_rect(center=(WIDTH // 2, 40)))

        # floor and flip
        draw_floor(pipe_speed)
        pygame.display.update()
        clock.tick(FPS)

        if not alive:
            high_score = max(high_score, score)
            # show game over screen; if it returns home, go home; if retry, restart
            res = game_over_screen(score, high_score)
            if res == "home":
                return "home"
            else:
                # restart (retry) - re-enter run_game with same mode
                return mode

    return "home"

# --- Main loop ---
while True:
    mode = home_screen()
    # run the game; run_game returns "home" to go back to menu or "manual"/"auto" to restart
    result = run_game(mode)
    if result == "home":
        continue
    else:
        # retry same mode
        mode = result
        continue
