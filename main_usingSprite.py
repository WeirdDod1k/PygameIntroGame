import pygame
from sys import exit
from random import randint, choice


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        player_walk1 = pygame.image.load("graphics/Player/player_walk_1.png").convert_alpha()
        player_walk2 = pygame.image.load("graphics/Player/player_walk_2.png").convert_alpha()
        self.player_walk = [player_walk1, player_walk2]
        self.player_index = 0
        self.player_jump = pygame.image.load("graphics/Player/jump.png").convert_alpha()

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(80, 300))
        self.gravity = 0
        self.velocity = 0

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 300:
            self.gravity = -20
        elif keys[pygame.K_r]:
            self.rect.midbottom = (80, 300)
            self.gravity = 0
        elif keys[pygame.K_a]:  # move left
            self.velocity = -5
        elif keys[pygame.K_d]:  # move right
            self.velocity = 5

    def apply_gravity(self):
        self.gravity += 1.3
        self.rect.y += self.gravity
        if self.rect.bottom >= 300:
            self.rect.bottom = 300

    def apply_velocity(self):  # applying velocity
        self.rect.x += self.velocity
        if self.velocity != 0:  # stops the player after releasing A/D buttons
            self.velocity = (self.velocity**0) * (abs(self.velocity)-1)  # x = (x^0) * (|x|-1)
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > 800:
            self.rect.right = 800

    def animation_state(self):
        if self.rect.bottom < 300:
            self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk):
                self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.apply_velocity()
        self.animation_state()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()

        if type == "fly":
            fly_1 = pygame.image.load("graphics/Fly/Fly1.png").convert_alpha()
            fly_2 = pygame.image.load("graphics/Fly/Fly2.png").convert_alpha()
            self.frames = [fly_1, fly_2]
            y_pos = 110
            self.anim_speed = 0.25
            self.speed = 10
        else:
            snail_1 = pygame.image.load("graphics/snail/snail1.png").convert_alpha()
            snail_2 = pygame.image.load("graphics/snail/snail2.png").convert_alpha()
            self.frames = [snail_1, snail_2]
            y_pos = 300
            self.anim_speed = 0.1
            self.speed = choice([4, 6, 7])

        self.animation_index = 0

        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom=(randint(900, 1100), y_pos))

    def animation_state(self):
        self.animation_index += self.anim_speed
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()
        self.rect.x -= self.speed
        self.destroy()

    def destroy(self):
        keys = pygame.key.get_pressed()
        if self.rect.x <= -100 or keys[pygame.K_r]:  # 2nd condition destroys sprites when you restart
            self.kill()  # destroys the sprite


def display_score():
    current_time = int(pygame.time.get_ticks()/100) - start_time
    score_surf = test_font.render(f'Score: {current_time}', False, (64, 64, 64))
    score_rect = score_surf.get_rect(center=(400, 50))
    screen.blit(score_surf, score_rect)
    print(current_time)
    return current_time


def collision_sprite():
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, False):
        obstacle_group.empty()
        return False
    else:
        return True


pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("Karakatitsa")
clock = pygame.time.Clock()
test_font = pygame.font.Font("font/Pixeltype.ttf", 50)
game_active = False
start_time = 0
score = 0

# Groups
player = pygame.sprite.GroupSingle()
player.add(Player())

obstacle_group = pygame.sprite.Group()

sky_surface = pygame.image.load("graphics/Sky.png").convert_alpha()  # convert_alpha converts pngs to help pygame
ground_surface = pygame.image.load("graphics/ground.png").convert_alpha()

# Intro screen
player_stand_surface = pygame.image.load("graphics/Player/player_stand.png").convert_alpha()
player_stand_surface = pygame.transform.scale2x(player_stand_surface)
player_stand_rectangle = player_stand_surface.get_rect(center=(400, 200))

title_surface = test_font.render("Karakatitsa", False, "#52453e")
title_rectangle = title_surface.get_rect(midbottom=(400, 50))

instruction_surface = test_font.render("Press R to start!", False, "#52453e")
instruction_rectangle = instruction_surface.get_rect(midbottom=(400, 380))

# Timer
obstacle_timer = pygame.USEREVENT + 1  # add 1 to avoid conflict with events reserved for pygame itself
pygame.time.set_timer(obstacle_timer, 1200)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if game_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_active = True
                    start_time = int(pygame.time.get_ticks()/100)
                    obstacle_group.update()  # reset
                    player.update()          # reset

            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(["fly", "snail", "snail"])))

        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_active = True
                    start_time = int(pygame.time.get_ticks()/100)

    # draw elements
    # update everything
    if game_active:
        screen.blit(sky_surface, (0, 0))  # blit - block image transfer. y = screen/2 - image/2
        screen.blit(ground_surface, (0, 300))
        score = display_score()

        player.draw(screen)
        player.update()

        obstacle_group.draw(screen)
        obstacle_group.update()

        # collision
        game_active = collision_sprite()

    else:
        screen.fill((94, 129, 162))
        screen.blit(player_stand_surface, player_stand_rectangle)
        screen.blit(title_surface, title_rectangle)
        screen.blit(instruction_surface, instruction_rectangle)
        if score != 0:
            score_surface = test_font.render(f"Your score is: {score}", False, "#52453e")
            score_rectangle = score_surface.get_rect(midbottom=(400, 330))
            screen.blit(score_surface, score_rectangle)

    pygame.display.update()
    clock.tick(60)
