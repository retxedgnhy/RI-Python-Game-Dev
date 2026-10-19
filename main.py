import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Game Setup
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 40
COLS, ROWS = WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE
FPS = 60

# Sleek Dark Mode Color Palette
BG_COLOR = (18, 18, 20)            # Deep dark background
WALL_COLOR = (30, 41, 59)          # Dark slate blue obstacles
WALL_BORDER = (51, 65, 85)         # Lighter accent border for definition
EXIT_COLOR = (34, 197, 94)         # Vibrant neon green exit
EXIT_GLOW = (20, 83, 45)           # Deep green aura
TEXT_COLOR = (241, 245, 249)       # Crisp off-white text
CAT_COLOR = (249, 115, 22)         # Vibrant orange cat
CAT_STUNNED = (148, 163, 184)      # Gray when stunned
MOUSE_COLOR = (203, 213, 225)      # Light silver mouse
UI_BG = (24, 24, 27)               # Dark top HUD background
HEART_COLOR = (239, 68, 68)        # Bright red hearts
STUN_READY_COLOR = (59, 130, 246)  # Blue for stun ready

# Setup Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cat & Mouse - Diagonal Arena Edition")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Segoe UI", 20, bold=True)
title_font = pygame.font.SysFont("Segoe UI", 26, bold=True)
large_font = pygame.font.SysFont("Segoe UI", 48, bold=True)

# 5 Levels with Exit (E) diagonally opposite to Mouse (M)
LEVELS = [
    # Level 1: Scattered pillars (M top-left, E bottom-right)
    [
        "WWWWWWWWWWWWWWWWWWWW",
        "W M                W",
        "W    WW      WW    W",
        "W    WW      WW    W",
        "W                  W",
        "W      WW    WW    W",
        "W      WW    WW    W",
        "W                  W",
        "W    WW      WW    W",
        "W    WW      WW    W",
        "W                  W",
        "W        C         W",
        "W                  W",
        "W                E W",
        "WWWWWWWWWWWWWWWWWWWW"
    ],
    # Level 2: Diagonal slashes
    [
        "WWWWWWWWWWWWWWWWWWWW",
        "W M                W",
        "W   W    W    W    W",
        "W    W    W    W   W",
        "W     W    W    W  W",
        "W      W    W    W W",
        "W       W    W    WW",
        "W                  W",
        "WW    W    W    W  W",
        "W W    W    W    W W",
        "W  W    W    W    WW",
        "W                  W",
        "W        C         W",
        "W                E W",
        "WWWWWWWWWWWWWWWWWWWW"
    ],
    # Level 3: Central obstacle cluster
    [
        "WWWWWWWWWWWWWWWWWWWW",
        "W M                W",
        "W                  W",
        "W      WWWWWW      W",
        "W      W    W      W",
        "W      W    W      W",
        "W      WWWWWW      W",
        "W                  W",
        "W      WWWWWW      W",
        "W      W    W      W",
        "W      W    W      W",
        "W      WWWWWW      W",
        "W        C         W",
        "W                E W",
        "WWWWWWWWWWWWWWWWWWWW"
    ],
    # Level 4: Diagonal stepping stones
    [
        "WWWWWWWWWWWWWWWWWWWW",
        "W M                W",
        "W    WW        WW  W",
        "W      WW    WW    W",
        "W        WWWW      W",
        "W      WW    WW    W",
        "W    WW        WW  W",
        "W                  W",
        "W    WW        WW  W",
        "W      WW    WW    W",
        "W        WWWW      W",
        "W                  W",
        "W        C         W",
        "W                E W",
        "WWWWWWWWWWWWWWWWWWWW"
    ],
    # Level 5: The Ultimate Open Arena
    [
        "WWWWWWWWWWWWWWWWWWWW",
        "W M                W",
        "W   W W W W W W W  W",
        "W                  W",
        "W   W W W W W W W  W",
        "W                  W",
        "W   W W W W W W W  W",
        "W                  W",
        "W   W W W W W W W  W",
        "W                  W",
        "W   W W W W W W W  W",
        "W                  W",
        "W        C         W",
        "W                E W",
        "WWWWWWWWWWWWWWWWWWWW"
    ]
]

class Game:
    def __init__(self):
        self.lives = 5
        self.level_index = 0
        self.state = "PLAYING" # PLAYING, GAMEOVER, WIN
        
        # Stun variables
        self.stun_duration = 0    
        self.stun_cooldown = 0    
        
        self.load_level()

    def load_level(self):
        self.time_limit = 420 # 7 minutes
        self.start_ticks = pygame.time.get_ticks()
        
        self.walls = []
        map_data = LEVELS[self.level_index]

        for r, row in enumerate(map_data):
            for c, char in enumerate(row):
                x = c * GRID_SIZE
                y = r * GRID_SIZE
                if char == 'W':
                    self.walls.append(pygame.Rect(x, y, GRID_SIZE, GRID_SIZE))
                elif char == 'M':
                    self.mouse_startX, self.mouse_startY = float(x), float(y)
                elif char == 'C':
                    self.cat_startX, self.cat_startY = float(x), float(y)
                elif char == 'E':
                    self.exit_x, self.exit_y = x, y

        self.reset_positions()
        self.mouse_speed = 3.5
        self.cat_speed = 2.1 + (self.level_index * 0.25)

    def reset_positions(self):
        self.mouse_x = self.mouse_startX
        self.mouse_y = self.mouse_startY
        self.cat_x = self.cat_startX
        self.cat_y = self.cat_startY

    def get_remaining_time(self):
        elapsed_seconds = (pygame.time.get_ticks() - self.start_ticks) // 1000
        remaining = self.time_limit - elapsed_seconds
        if remaining <= 0:
            self.start_ticks = pygame.time.get_ticks()
            return self.time_limit
        return remaining

    def trigger_stun(self):
        if self.stun_cooldown == 0 and self.stun_duration == 0:
            self.stun_duration = 120  # 2 seconds
            self.stun_cooldown = 300  # 5 seconds cooldown

    def update_timers(self):
        if self.stun_duration > 0:
            self.stun_duration -= 1
        if self.stun_cooldown > 0:
            self.stun_cooldown -= 1

    def move_mouse(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_a]:
            dx -= self.mouse_speed
        if keys[pygame.K_d]:
            dx += self.mouse_speed
        if keys[pygame.K_w]:
            dy -= self.mouse_speed
        if keys[pygame.K_s]:
            dy += self.mouse_speed

        mouse_rect_x = pygame.Rect(self.mouse_x + dx + 6, self.mouse_y + 6, GRID_SIZE - 12, GRID_SIZE - 12)
        if not any(mouse_rect_x.colliderect(w) for w in self.walls):
            self.mouse_x += dx

        mouse_rect_y = pygame.Rect(self.mouse_x + 6, self.mouse_y + dy + 6, GRID_SIZE - 12, GRID_SIZE - 12)
        if not any(mouse_rect_y.colliderect(w) for w in self.walls):
            self.mouse_y += dy

    def move_cat(self):
        if self.stun_duration > 0:
            return

        target_x = self.mouse_x
        target_y = self.mouse_y

        dir_x = target_x - self.cat_x
        dir_y = target_y - self.cat_y
        dist = math.hypot(dir_x, dir_y)

        if dist > 2:
            nx = (dir_x / dist) * self.cat_speed
            ny = (dir_y / dist) * self.cat_speed

            cat_rect_x = pygame.Rect(self.cat_x + nx + 4, self.cat_y + 4, GRID_SIZE - 8, GRID_SIZE - 8)
            if not any(cat_rect_x.colliderect(w) for w in self.walls):
                self.cat_x += nx
            
            cat_rect_y = pygame.Rect(self.cat_x + 4, self.cat_y + ny + 4, GRID_SIZE - 8, GRID_SIZE - 8)
            if not any(cat_rect_y.colliderect(w) for w in self.walls):
                self.cat_y += ny

    def check_collisions(self):
        mouse_rect = pygame.Rect(self.mouse_x + 6, self.mouse_y + 6, GRID_SIZE - 12, GRID_SIZE - 12)
        cat_rect = pygame.Rect(self.cat_x + 4, self.cat_y + 4, GRID_SIZE - 8, GRID_SIZE - 8)
        exit_rect = pygame.Rect(self.exit_x + 4, self.exit_y + 4, GRID_SIZE - 8, GRID_SIZE - 8)

        if cat_rect.colliderect(mouse_rect) and self.stun_duration == 0:
            self.lives -= 1
            if self.lives <= 0:
                self.state = "GAMEOVER"
            else:
                self.reset_positions()

        elif mouse_rect.colliderect(exit_rect):
            self.level_index += 1
            if self.level_index >= len(LEVELS):
                self.state = "WIN"
            else:
                self.load_level()

    def draw_mouse(self, x, y):
        mx, my = int(x + GRID_SIZE // 2), int(y + GRID_SIZE // 2)
        pygame.draw.circle(screen, MOUSE_COLOR, (mx, my), 12)
        pygame.draw.circle(screen, WALL_BORDER, (mx, my), 12, 2)
        pygame.draw.circle(screen, MOUSE_COLOR, (mx - 8, my - 8), 6)
        pygame.draw.circle(screen, MOUSE_COLOR, (mx + 8, my - 8), 6)
        pygame.draw.circle(screen, BG_COLOR, (mx - 3, my - 2), 1.5)
        pygame.draw.circle(screen, BG_COLOR, (mx + 3, my - 2), 1.5)

    def draw_cat(self, x, y):
        cx, cy = int(x + GRID_SIZE // 2), int(y + GRID_SIZE // 2)
        color = CAT_STUNNED if self.stun_duration > 0 else CAT_COLOR
        
        pygame.draw.circle(screen, color, (cx, cy), 16)
        pygame.draw.polygon(screen, color, [(cx - 14, cy - 8), (cx - 18, cy - 22), (cx - 4, cy - 14)])
        pygame.draw.polygon(screen, color, [(cx + 14, cy - 8), (cx + 18, cy - 22), (cx + 4, cy - 14)])
        pygame.draw.circle(screen, BG_COLOR, (cx - 5, cy - 2), 2)
        pygame.draw.circle(screen, BG_COLOR, (cx + 5, cy - 2), 2)

        if self.stun_duration > 0:
            surf = font.render("ZZZ", True, (255, 255, 255))
            screen.blit(surf, (cx - 14, cy - 35))

    def draw(self):
        screen.fill(BG_COLOR)

        if self.state == "PLAYING":
            exit_rect = pygame.Rect(self.exit_x + 4, self.exit_y + 4, GRID_SIZE - 8, GRID_SIZE - 8)
            pygame.draw.rect(screen, EXIT_GLOW, exit_rect.inflate(8, 8), border_radius=12)
            pygame.draw.rect(screen, EXIT_COLOR, exit_rect, border_radius=8)

            for w in self.walls:
                pygame.draw.rect(screen, WALL_COLOR, w, border_radius=6)
                pygame.draw.rect(screen, WALL_BORDER, w, 2, border_radius=6)

            self.draw_cat(self.cat_x, self.cat_y)
            self.draw_mouse(self.mouse_x, self.mouse_y)

            pygame.draw.rect(screen, UI_BG, (0, 0, WIDTH, 50))
            pygame.draw.line(screen, (51, 65, 85), (0, 50), (WIDTH, 50), 2)

            rem_seconds = self.get_remaining_time()
            mins = rem_seconds // 60
            secs = rem_seconds % 60

            level_text = title_font.render(f"Level {self.level_index + 1}/5", True, TEXT_COLOR)
            timer_text = font.render(f"⏱️ {mins:02d}:{secs:02d}", True, TEXT_COLOR)
            
            screen.blit(level_text, (20, 10))
            screen.blit(timer_text, (WIDTH - 130, 14))

            if self.stun_duration > 0:
                stun_text = font.render("STUNNED!", True, CAT_STUNNED)
            elif self.stun_cooldown == 0:
                stun_text = font.render("Stun [SPACE]: READY", True, STUN_READY_COLOR)
            else:
                cd_secs = math.ceil(self.stun_cooldown / 60)
                stun_text = font.render(f"Stun CD: {cd_secs}s", True, (100, 116, 139))
            
            screen.blit(stun_text, (370, 14))

            for i in range(self.lives):
                hx = 160 + (i * 25)
                hy = 20
                pygame.draw.circle(screen, HEART_COLOR, (hx, hy + 6), 6)
                pygame.draw.circle(screen, HEART_COLOR, (hx + 10, hy + 6), 6)
                pygame.draw.polygon(screen, HEART_COLOR, [(hx - 6, hy + 9), (hx + 16, hy + 9), (hx + 5, hy + 22)])

        elif self.state == "GAMEOVER":
            text = large_font.render("GAME OVER", True, HEART_COLOR)
            sub = font.render("Press 'R' to Restart", True, TEXT_COLOR)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 20))

        elif self.state == "WIN":
            text = large_font.render("YOU WIN!", True, EXIT_COLOR)
            sub = font.render("Press 'R' to Play Again", True, TEXT_COLOR)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 20))

        pygame.display.flip()

    def restart(self):
        self.lives = 5
        self.level_index = 0
        self.state = "PLAYING"
        self.load_level()

def main():
    game = Game()
    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game.state in ["GAMEOVER", "WIN"]:
                    game.restart()
                elif event.key == pygame.K_SPACE and game.state == "PLAYING":
                    game.trigger_stun()

        if game.state == "PLAYING":
            game.update_timers()
            keys = pygame.key.get_pressed()
            game.move_mouse(keys)
            game.move_cat()
            game.check_collisions()

        game.draw()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()