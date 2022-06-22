import settings, pygame, random, cosmos, sys, math, cannonball

from settings import State

sets = settings.Settings()
# sets.set_bgcolor(40, 60, 120)
sets.fill_background()
# print(f"{sets.starfield}")
sets.draw_stars()

# experimenting with FPS & time
# sets.set_fps(60)
# sets.set_time_scale(1000)
sets.set_scales(sets.rad_scale, 300, 1/20)

celestials = []

celestials.append(cosmos.Celestial(sets))

# celestials.append(cosmos.Celestial(sets))
# celestials[1].set_attr('Moon #1', False, settings.LUNA_DENSITY, \
#   settings.LUNA_RADIUS, (255,255,255) )
# celestials[1].set_xy(0, settings.EARTH_RADIUS * 2)
# speed = math.sqrt(settings.GRAV_CONST * celestials[0].mass / \
#   celestials[1].radius) / 3
# celestials[1].set_v(speed, 0)

# celestials.append(cosmos.Celestial(sets))
# celestials[2].set_attr('Moon #2', False, settings.LUNA_DENSITY, \
#    settings.LUNA_RADIUS, (0, 0, 255) )
# celestials[2].set_xy(settings.EARTH_RADIUS * 2, 0)
# speed = math.sqrt(settings.GRAV_CONST * celestials[0].mass / \
#    celestials[2].radius) / 3
# celestials[2].set_v(0, -speed)

# celestials.append(cosmos.Celestial(sets))
# celestials[3].set_attr('Moon #3', False, settings.LUNA_DENSITY, \
#    settings.LUNA_RADIUS, (0, 200, 0) )
# celestials[3].set_xy(0, -settings.EARTH_RADIUS * 2)
# speed = math.sqrt(settings.GRAV_CONST * celestials[0].mass / \
#    celestials[3].radius)
# celestials[3].set_v(-speed,0)

clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 24)

screen_rect = sets.screen.get_rect()

for body in celestials:
    print("\n")
    body.display_values()

ball = cannonball.Cannonball(sets, celestials)
ball.screen_rad = 2
ball.vx *= 1.9
ball.vy *= 1.9
# ball.x += settings.EARTH_RADIUS

time = 0

key_press = pygame.K_DELETE

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
             key_press = event.key
     
    clock.tick(sets.fps)
    sets.fill_background()
    sets.draw_stars()

    if key_press == pygame.K_SPACE:
        ball.state == State.ALIVE
        text = pygame.font.Font.render(font, f"Space Pressed!", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.midbottom = screen_rect.midtop

    for body in celestials:
        time = 0
        while time < (sets.time_scale*sets.tres):
            body.move(celestials)
            # body.bounce(celestials)
            if ball.state == State.ALIVE:
                ball.move(celestials)
            time += sets.tres
        body.draw_bodycircle()
        if ball.state == State.ALIVE:
            ball.draw_bodycircle()
 
    text = pygame.font.Font.render(
        font, f"FPS:  {int(clock.get_fps())}", True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.midbottom = screen_rect.midbottom

    sets.screen.blit(text, text_rect)

    pygame.display.flip()
