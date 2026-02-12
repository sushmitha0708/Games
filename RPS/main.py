import pygame
import random
import sys
import math, asyncio

pygame.init()

WIDTH, HEIGHT = 1000, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rock Paper Scissors - Competitive Edition")
clock = pygame.time.Clock()

# ---------------- COLORS ---------------- #
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
BLUE = (70, 130, 180)
RED = (220, 20, 60)
GREEN = (40, 200, 100)
LIGHT_GRAY = (240, 240, 240)
GOLD = (255, 215, 0)

font_big = pygame.font.SysFont("arial", 60, bold=True)
font_med = pygame.font.SysFont("arial", 40)
font_small = pygame.font.SysFont("arial", 30)

choices = ["Rock", "Paper", "Scissors"]

# ---------------- GAME VARIABLES ---------------- #
score = 0
player_choice = None
computer_choice = None
result_text = ""
animating = False
animation_timer = 0
round_active = False

ROUND_TIME = 30
start_time = pygame.time.get_ticks()
game_over = False

# ---------------- DRAW ICONS ---------------- #

def draw_rock(surface, center, scale=1):
    radius = int(50 * scale)
    pygame.draw.circle(surface, (120, 120, 120), center, radius)
    pygame.draw.circle(surface, (90, 90, 90), center, radius-10)

def draw_paper(surface, center, scale=1):
    w = int(100 * scale)
    h = int(120 * scale)
    rect = pygame.Rect(center[0]-w//2, center[1]-h//2, w, h)
    pygame.draw.rect(surface, WHITE, rect, border_radius=10)
    pygame.draw.rect(surface, BLACK, rect, 3, border_radius=10)

def draw_scissors(surface, center, scale=1):
    length = int(45 * scale)
    pygame.draw.line(surface, BLACK,
                     (center[0]-length, center[1]-length),
                     (center[0]+length, center[1]+length), 6)
    pygame.draw.line(surface, BLACK,
                     (center[0]-length, center[1]+length),
                     (center[0]+length, center[1]-length), 6)
    pygame.draw.circle(surface, RED,
                       (center[0]-length, center[1]-length), 12)
    pygame.draw.circle(surface, RED,
                       (center[0]-length, center[1]+length), 12)

def draw_icon(choice, surface, center, scale=1):
    if choice == "Rock":
        draw_rock(surface, center, scale)
    elif choice == "Paper":
        draw_paper(surface, center, scale)
    elif choice == "Scissors":
        draw_scissors(surface, center, scale)

# ---------------- HUD ICONS ---------------- #

def draw_coin(surface, center, radius=18):
    pygame.draw.circle(surface, GOLD, center, radius)
    pygame.draw.circle(surface, (255, 235, 120), center, radius-5)
    pygame.draw.circle(surface, BLACK, center, radius, 2)

def draw_sandglass(surface, center):
    x, y = center
    size = 18

    pygame.draw.polygon(surface, BLACK,
                        [(x-size, y-size),
                         (x+size, y-size),
                         (x, y)], 2)

    pygame.draw.polygon(surface, BLACK,
                        [(x-size, y+size),
                         (x+size, y+size),
                         (x, y)], 2)

# ---------------- BUTTON CLASS ---------------- #

class IconButton:
    def __init__(self, choice, x, y):
        self.choice = choice
        self.center = (x, y)
        self.radius = 85
        self.hover = False

    def draw(self):
        color = BLUE if self.hover else LIGHT_GRAY
        pygame.draw.circle(screen, color, self.center, self.radius)
        pygame.draw.circle(screen, BLACK, self.center, self.radius, 3)
        draw_icon(self.choice, screen, self.center, 1)

    def update(self, mouse_pos):
        dist = math.hypot(mouse_pos[0]-self.center[0],
                          mouse_pos[1]-self.center[1])
        self.hover = dist < self.radius

    def clicked(self, mouse_pos):
        dist = math.hypot(mouse_pos[0]-self.center[0],
                          mouse_pos[1]-self.center[1])
        return dist < self.radius

buttons = [
    IconButton("Rock", 250, 650),
    IconButton("Paper", 500, 650),
    IconButton("Scissors", 750, 650)
]

# ---------------- WIN LOGIC ---------------- #

def determine_score(player, computer):
    global score

    if player == computer:
        return "Draw! 0", 0
    elif (
        (player == "Rock" and computer == "Scissors") or
        (player == "Paper" and computer == "Rock") or
        (player == "Scissors" and computer == "Paper")
    ):
        score += 1
        return "You Win! +1", 1
    else:
        score -= 1
        return "You Lose! -1", -1

# ---------------- BACKGROUND ---------------- #

def draw_background():
    for y in range(HEIGHT):
        color = (200 - y//6, 220 - y//7, 255)
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

# ---------------- RESET ---------------- #

def reset_game():
    global score, start_time, game_over
    global player_choice, computer_choice, result_text
    score = 0
    start_time = pygame.time.get_ticks()
    game_over = False
    player_choice = None
    computer_choice = None
    result_text = ""

# ---------------- MAIN LOOP ---------------- #

running = True

async def main():
    while running:
        clock.tick(60)
        draw_background()

        mouse_pos = pygame.mouse.get_pos()
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) // 1000
        remaining_time = max(0, ROUND_TIME - elapsed_time)

        if remaining_time == 0:
            game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and not animating and not game_over:
                for btn in buttons:
                    if btn.clicked(mouse_pos) and not round_active:
                        player_choice = btn.choice
                        computer_choice = random.choice(choices)
                        animating = True
                        round_active = True
                        animation_timer = pygame.time.get_ticks()

            if event.type == pygame.MOUSEBUTTONDOWN and game_over:
                reset_game()

        # Animation delay
        if animating:
            if pygame.time.get_ticks() - animation_timer > 600:
                animating = False
                result_text, _ = determine_score(player_choice, computer_choice)
                round_active = False

        # ---------------- TOP HUD ---------------- #

        hud_bar = pygame.Surface((WIDTH, 90))
        hud_bar.set_alpha(200)
        hud_bar.fill(WHITE)
        screen.blit(hud_bar, (0, 0))

        # Score
        draw_coin(screen, (60, 45))
        score_surface = font_med.render(f"Score: {score}", True, BLACK)
        screen.blit(score_surface, (100, 25))

        # Timer
        timer_color = RED if remaining_time <= 5 else BLACK
        draw_sandglass(screen, (WIDTH - 180, 45))
        timer_surface = font_med.render(f"Time: {remaining_time}s", True, timer_color)
        screen.blit(timer_surface, (WIDTH - 150, 25))

        # ---------------- TITLE ---------------- #

        title = font_big.render("Rock Paper Scissors", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 110))

        # ---------------- GAME DISPLAY ---------------- #

        if player_choice:
            draw_icon(player_choice, screen, (300, 350), 1.5)

        if computer_choice and not animating:
            draw_icon(computer_choice, screen, (700, 350), 1.5)

        vs = font_big.render("VS", True, GOLD)
        screen.blit(vs, (WIDTH//2 - vs.get_width()//2, 330))

        result_surface = font_med.render(result_text, True, RED)
        screen.blit(result_surface,
                    (WIDTH//2 - result_surface.get_width()//2, 500))

        # Buttons
        for btn in buttons:
            btn.update(mouse_pos)
            btn.draw()

        # ---------------- GAME OVER ---------------- #

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

            final_text = font_big.render(
                f"FINAL SCORE: {score}",
                True, WHITE)
            screen.blit(final_text,
                        (WIDTH//2 - final_text.get_width()//2, 300))

            restart_text = font_small.render(
                "Click Anywhere to Restart",
                True, WHITE)
            screen.blit(restart_text,
                        (WIDTH//2 - restart_text.get_width()//2, 400))

        pygame.display.flip()
        await asyncio.sleep(0)


asyncio.run(main())

