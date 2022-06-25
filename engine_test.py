import settings, pygame, random, cosmos, sys, math, cannonball, tank, engine

MainSettings = settings.Settings()
# experimenting with FPS & time
MainSettings.set_scales(MainSettings.rad_scale, 20, 1)

MainEngine = engine.Engine(MainSettings)

MainEngine.create_homeworld()
MainEngine.create_moon()
MainEngine.create_moon()
MainEngine.create_tank()

while True:

    MainEngine.manage_events(pygame.event.get())

    MainEngine.ticktock()
    MainEngine.create_universe()

    MainEngine.time = 0
    while MainEngine.time < (MainSettings.time_scale * MainSettings.tres):
        
        for body in MainEngine.celestials:
            body.move(MainEngine.celestials)
            # body.bounce(MainEngine.celestials)
        
        MainEngine.tanks[0].move_balls()
        MainEngine.tanks[0].check_balls()
        MainEngine.time += MainSettings.tres
          
    for body in MainEngine.celestials:
        body.draw_bodycircle()
    
    MainEngine.tanks[0].set_surface_pos()
    MainEngine.tanks[0].draw_bodycircle()
    
    for ball in MainEngine.tanks[0].balls:
        if ball.active or ball.exploding:
            ball.draw_bodycircle()
    
    if MainEngine.tanks[0].chambered_ball:
        MainEngine.tanks[0].draw_launch_v()
            
    text_FPS = pygame.font.Font.render(
        MainEngine.font, f"FPS:  {int(MainEngine.clock.get_fps())}", True, (255, 255, 255))
    text_rect_FPS = text_FPS.get_rect()
    text_rect_FPS.midbottom = MainEngine.screen_rect.midbottom
    
    # text_ball = pygame.font.Font.render(
    #     font, f"Angle:  {ball.launch_angle}, vel.:  <{ball.", True, (255, 255, 255))
    # text_rect_FPS = text_FPS.get_rect()
    # text_rect_FPS.midbottom = screen_rect.midbottom
        
    MainSettings.screen.blit(text_FPS, text_rect_FPS)

    pygame.display.flip()
