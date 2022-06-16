import settings, pygame, random, cosmos, sys, math, cannonball

sets = settings.Settings()
# sets.set_bgcolor(40, 60, 120)
sets.fill_background()
# print(f"{sets.starfield}")
sets.draw_stars()

# experimenting with FPS
sets.set_fps(60000)

celestials = []

celestials.append(cosmos.Celestial(sets))

celestials.append(cosmos.Celestial(sets))
celestials[1].set_attr('Moon #1', False, settings.LUNA_DENSITY, \
    settings.LUNA_RADIUS, (255,255,255) )
celestials[1].set_xy(0, settings.EARTH_RADIUS * 2)
speed = math.sqrt(settings.GRAV_CONST * celestials[0].mass / \
    celestials[1].radius)
celestials[1].set_v(speed, 0)

celestials.append(cosmos.Celestial(sets))
celestials[2].set_attr('Moon #2', False, settings.LUNA_DENSITY, \
    settings.LUNA_RADIUS, (0, 0, 255) )
celestials[2].set_xy(settings.EARTH_RADIUS * 2, 0)
speed = math.sqrt(settings.GRAV_CONST * celestials[0].mass / \
    celestials[2].radius)
celestials[2].set_v(0, -speed)

celestials.append(cosmos.Celestial(sets))
celestials[3].set_attr('Moon #3', False, settings.LUNA_DENSITY, \
    settings.LUNA_RADIUS, (0, 200, 0) )
celestials[3].set_xy(0, -settings.EARTH_RADIUS * 2)
speed = math.sqrt(settings.GRAV_CONST * celestials[0].mass / \
    celestials[3].radius)
celestials[3].set_v(-speed,0)

clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 24)

screen_rect = sets.screen.get_rect()

for body in celestials:
    print("\n")
    body.display_values()

ball = cannonball.Cannonball(sets, celestials)
ball.screen_rad = 2
ball.vx *= 0.8
# ball.vy *= 10
# ball.x += settings.EARTH_RADIUS

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    clock.tick(sets.fps)
    sets.fill_background()
    sets.draw_stars()

    for body in celestials:
        # print("\n")
        # body.display_values()
        body.draw_bodycircle()
        body.move(celestials)
        body.bounce(celestials)

    # ball.display_values()
    ball.draw_bodycircle()
    ball.move(celestials)

    text = pygame.font.Font.render(
        font, f"FPS:  {int(clock.get_fps())}", True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.midbottom = screen_rect.midbottom

    sets.screen.blit(text, text_rect)

    pygame.display.flip()
