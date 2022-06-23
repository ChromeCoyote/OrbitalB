import settings, pygame, random, cosmos, sys, math, cannonball

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

celestials.append(cosmos.Celestial(sets))
celestials[1].set_attr('Moon #1', False, settings.LUNA_DENSITY, \
    settings.LUNA_RADIUS, (255,255,255) )
celestials[1].set_xy(0, settings.EARTH_RADIUS * 2)
speed = math.sqrt(settings.GRAV_CONST * celestials[0].mass / \
    celestials[1].radius) / 3
celestials[1].set_v(speed, 0)

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
ball.vx *= 0.5
ball.vy *= 0.5
# ball.x += settings.EARTH_RADIUS

time = 0
ball.alive = False
save_angle = 0
save_speed = 0

print("\n")
ball.display_ball_values()

while True:
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and ball.alive == False:
                ball.alive = True
            elif event.key == pygame.K_UP and ball.alive == False:
                ball.launch_angle -= ball.radian_step
                ball.reset_velocity()
                # print("\n")
                # ball.display_ball_values()
            elif event.key == pygame.K_DOWN and ball.alive == False:
                ball.launch_angle += ball.radian_step
                ball.reset_velocity()
                # print("\n")
                # ball.display_ball_values()
            elif event.key == pygame.K_KP_PLUS and ball.alive == False:
                ball.speed += ball.speed_step
                ball.reset_velocity()
            elif event.key == pygame.K_KP_MINUS and ball.alive == False:
                ball.speed -= ball.speed_step
                ball.reset_velocity()
            elif event.key == pygame.K_LEFT:
                ball.pos_angle += ball.radian_step
                ball.set_launch_point()
            elif event.key == pygame.K_RIGHT:
                ball.pos_angle -= ball.radian_step
                ball.set_launch_point()    
                                
    clock.tick(sets.fps)
    sets.fill_background()
    sets.draw_stars()

    save_angle = ball.launch_angle
    save_speed = ball.speed

    for body in celestials:
        time = 0
        while time < (sets.time_scale*sets.tres):
            body.move(celestials)
            # body.bounce(celestials)
            if ball.alive == True:
                ball.move(celestials)
                if ball.check_impact(celestials) == True:
                    ball.alive = False
                    ball.set_launch_point()
                    ball.launch_angle = save_angle
                    ball.speed = save_speed
                    ball.reset_velocity()
            time += sets.tres
        
        body.draw_bodycircle()
    
    if ball.alive == False:
        ball.draw_launch_v()
        ball.set_launch_point()
    ball.draw_bodycircle()    
            
    text_FPS = pygame.font.Font.render(
        font, f"FPS:  {int(clock.get_fps())}", True, (255, 255, 255))
    text_rect_FPS = text_FPS.get_rect()
    text_rect_FPS.midbottom = screen_rect.midbottom
    
    # text_ball = pygame.font.Font.render(
    #     font, f"Angle:  {ball.launch_angle}, vel.:  <{ball.", True, (255, 255, 255))
    # text_rect_FPS = text_FPS.get_rect()
    # text_rect_FPS.midbottom = screen_rect.midbottom
    
    
    sets.screen.blit(text_FPS, text_rect_FPS)

    pygame.display.flip()
