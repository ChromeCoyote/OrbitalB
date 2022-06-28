import settings, pygame, random, cosmos, sys, math, cannonball, engine
import tank as _tank

MainSettings = settings.Settings()

# experimenting with FPS & time
MainSettings.set_scales(MainSettings.rad_scale, 20, 1)

MainEngine = engine.Engine(MainSettings)

#create homeworld
MainEngine.create_homeworld()

# create moons
MainEngine.create_moon()
# MainEngine.create_moon()
# MainEngine.create_moon()
# MainEngine.create_moon()

# Create player tank, index 0
MainEngine.create_tank()

# enemy tanks
MainEngine.create_tank()
MainEngine.tanks[-1].set_enemy_tank()

destroyed_tanks = []

while not MainEngine.game_over:

    MainEngine.manage_events(pygame.event.get())

    MainEngine.ticktock()
    MainEngine.create_universe()

    # main time time for physics calculations...
    MainEngine.time = 0
    while MainEngine.time < (MainSettings.time_scale * MainSettings.tres):
        
        for body in MainEngine.celestials:
            body.move(MainEngine.celestials)
            body.shatter(MainEngine.celestials)
            body.bounce(MainEngine.celestials)
                    
        cosmos.check_celestials(MainEngine.celestials)

        MainEngine.center_homeworld()
        
        for tank in MainEngine.tanks:
            tank.move_balls()
            tank.check_balls(MainEngine.tanks)

        destroyed_player_tanks = _tank.check_tanks(MainEngine.tanks)
        if destroyed_player_tanks:
            for tank in destroyed_player_tanks:
                MainEngine.draw_objects()
                MainEngine.display_game_message(
                    f"{tank.name} has been destroyed!", MainEngine.screen_rect.center, tank.color)
                pygame.display.flip()
                pygame.event.wait()
              
        MainEngine.time += MainSettings.tres
          
    MainEngine.draw_objects()
        
    # draw FPS to measure performance
    if MainSettings.debug:
        MainEngine.display_game_message(
            f"FPS:  {int(MainEngine.clock.get_fps())}", MainEngine.screen_rect.midbottom, settings.DEFAULT_FONT_COLOR)     
          
    if len(MainEngine.tanks) == 1:
        MainEngine.tanks[0].winner = True
        MainEngine.game_over = True
    elif not MainEngine.tanks:
        MainEngine.game_over = True

    pygame.display.flip()

# ENDGAME SCREEN *******************************************
wait4me = True

while wait4me:
    MainEngine.ticktock()

    MainEngine.create_universe()

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.KEYDOWN:
            wait4me = False

    MainEngine.set_font_size(48)
    if MainEngine.tanks and MainEngine.tanks[0].winner:
            for ball in MainEngine.tanks[0].balls:
                if ball.exploding:
                    ball.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))

            MainEngine.draw_objects()
           
            MainEngine.display_game_message(
                    f"{MainEngine.tanks[0].name} wins!", MainEngine.screen_rect.center, MainEngine.tanks[0].color)
    elif not MainEngine.tanks:
        MainEngine.draw_objects()
        MainEngine.display_game_message(
                "All tanks destroyed!", MainEngine.screen_rect.center, settings.DEFAULT_FONT_COLOR)

    MainEngine.set_font_size(64)
    MainEngine.display_game_message(
            f"GAME OVER", MainEngine.screen_rect.midbottom, (random.randint(0,255), random.randint(0,255), random.randint(0,255)))
    pygame.display.flip()
            
if MainSettings.debug:
    print("Game over, exiting...")

sys.exit()