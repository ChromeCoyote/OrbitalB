import settings, pygame, random, cosmos, sys, math, cannonball, tank

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
    settings.LUNA_RADIUS, (194,197,204) )
celestials[1].set_xy(0, settings.EARTH_RADIUS * 2)
speed = math.sqrt(settings.GRAV_CONST * celestials[0].mass / \
    celestials[1].radius) / 3
celestials[1].set_v(speed, 0)

# celestials.append(cosmos.Celestial(sets))
# celestials[2].set_attr('Moon #2', False, settings.LUNA_DENSITY, \
#    settings.LUNA_RADIUS, (0, 0, 255) )
# celestials[2].set_xy(settings.EARTH_RADIUS * 2, 0)
# speed = math.sqrt(settings.GRAV_CONST * celestials[0].mass / \
#     celestials[2].radius) / 3
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

tank = tank.Tank(sets, celestials)

time = 0
ball.active = False

ball_index = -1

printx = 0
printy = 0

print("\n")
ball.display_ball_values()

while True:
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if sets.debug:
                tank.display_ball_stats()
                print("\nQuit through pygame...")
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if not tank.chamber_ball():
                    if sets.debug:
                        print("\nError chambering ball, already one in chamber...")
            elif event.key == pygame.K_SPACE:
                if not tank.fire_ball():
                    if sets.debug:
                        print("\nError firing ball:  none chambered")
            elif event.key == pygame.K_UP and tank.chambered_ball:
                tank.launch_angle -= tank.radian_step
                tank.fix_launch_velocity()
                # print("\n")
                # ball.display_ball_values()
            elif event.key == pygame.K_DOWN and tank.chambered_ball:
                tank.launch_angle += tank.radian_step
                tank.fix_launch_velocity()
                # print("\n")
                # ball.display_ball_values()
            elif event.key == pygame.K_KP_PLUS and tank.chambered_ball:
                tank.launch_speed += tank.speed_step
                tank.fix_launch_velocity()
            elif event.key == pygame.K_KP_MINUS and tank.chambered_ball:
                tank.launch_speed -= tank.speed_step
                tank.fix_launch_velocity()
            elif event.key == pygame.K_LEFT and not tank.chambered_ball:
                tank.pos_angle += tank.radian_step
                tank.set_surface_pos()
            elif event.key == pygame.K_RIGHT and not tank.chambered_ball:
                tank.pos_angle -= tank.radian_step
                tank.set_surface_pos()
            elif event.key == pygame.K_DELETE:
                tank.detonate_ball()    
                                
    clock.tick(sets.fps)
    sets.fill_background()
    sets.draw_stars()

    time = 0
    while time < (sets.time_scale*sets.tres):
        
        for body in celestials:
            body.move(celestials)
            body.bounce(celestials)
        
        tank.move_balls()
        tank.check_balls()
        time += sets.tres
          
    for body in celestials:
        body.draw_bodycircle()
    
    tank.set_surface_pos()
    tank.draw_bodycircle()
    
    for ball in tank.balls:
        if ball.active or ball.exploding:
            ball.draw_bodycircle()
    
    if tank.chambered_ball:
        tank.draw_launch_v()
            
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
