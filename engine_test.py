import settings, pygame, random, cosmos, sys, math, cannonball, engine
import tank as _tank

MainSettings = settings.Settings()

# experimenting with FPS & time
MainSettings.set_scales(MainSettings.rad_scale, 1, 10)

MainEngine = engine.Engine(MainSettings)

#create homeworld
MainEngine.create_homeworld()

# create moons
# MainEngine.create_moon()
# MainEngine.celestials[-1].vx = 0
# MainEngine.celestials[-1].vy = 0
# MainEngine.celestials[-1].y = 2*MainEngine.celestials[0].radius
# MainEngine.celestials[-1].x = 0
# MainEngine.create_moon()
# MainEngine.create_moon()
# MainEngine.create_moon()

# Create player tank, index 0
MainEngine.create_tank()

# enemy tanks
MainEngine.create_tank()
MainEngine.tanks[-1].set_enemy_tank()

# AI testing...
# MainEngine.tanks[-1].pick_position()

destroyed_player_tanks = False

while not MainEngine.game_over:

    MainEngine.manage_events(pygame.event.get())

    for tank in MainEngine.tanks:
        if not tank.player_tank:
            tank.make_choices(MainEngine.tanks)

    MainEngine.ticktock()
    MainEngine.create_universe()

    # main time time for physics calculations...
    MainEngine.time = 0
    while MainEngine.time < (MainSettings.time_scale * MainSettings.tres):
        
        for body in MainEngine.celestials:
            body.move(MainEngine.celestials)
            for tank in MainEngine.tanks:
                tank.check_smush(body)    
            body.shatter(MainEngine.celestials)
            body.bounce_all(MainEngine.celestials)
                    
        cosmos.check_celestials(MainEngine.celestials)

        MainEngine.center_homeworld()
        
        for tank in MainEngine.tanks:
            tank.move_balls()
            tank.check_balls(MainEngine.tanks)
     
        destroyed_player_tanks = _tank.check_tanks(MainEngine.tanks, MainSettings)
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
          
    if len(MainEngine.tanks) == 1 and not MainEngine.tanks[0].balls:
        MainEngine.tanks[0].winner = True
        MainEngine.game_over = True
    elif not MainEngine.tanks:
        MainEngine.game_over = True

    pygame.display.flip()

# ENDGAME SCREEN *******************************************
MainEngine.endgame_screen()

sys.exit()