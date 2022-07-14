import settings, pygame
import tank as _tank
import cosmos, engine, gc, traceback

counts = {}
loops = 0

for role in settings.AI_NATURES:
    counts[role] = 0

counts["errors"] = 0

lowest_FPS = 100
FPS = 0

while True:

    loops += 1

    print(f"\n*** LOOP #{loops} ***")

    try:
        MainSettings = settings.Settings()

        # experimenting with FPS & time
        MainSettings.set_scales(MainSettings.rad_scale, 1, 10)

        MainEngine = engine.Engine(MainSettings)

        #create homeworld
        MainEngine.create_homeworld()

        # create moons
        MainEngine.create_moon()
        MainEngine.create_moon()

        MainEngine.create_tank(False)
        MainEngine.create_tank(False)
        MainEngine.create_tank(False)

        destroyed_tanks = False

        while not MainEngine.game_over:

            MainEngine.meteor_shower()

            MainEngine.create_universe()      
            MainEngine.draw_objects()

            # MainEngine.meteor_shower()

            MainEngine.ticktock()

            # main time time for physics calculations...
            MainEngine.time = 0
            while MainEngine.time < (MainEngine.sts.time_scale * MainEngine.sts.tres):
                
                for body in MainEngine.celestials:
                    body.move(MainEngine.celestials, MainEngine.sts.tres)
                    for tank in MainEngine.tanks:
                        tank.check_smush(body)    
                    body.shatter(MainEngine.celestials, MainEngine.tanks)
                    body.bounce_all(MainEngine.celestials)
                            
                cosmos.check_celestials(MainEngine.celestials)

                MainEngine.center_homeworld()
                
                for tank in MainEngine.tanks:
                    tank.check_dying()
                    tank.move_balls()
                    tank.check_balls(MainEngine.tanks)
                    tank.check_spells(MainEngine.tanks)
            
                destroyed_tanks = _tank.check_tanks(MainEngine.tanks, MainEngine.sts)
                if destroyed_tanks:
                    for tank in destroyed_tanks:
                        # put image of dead snail in background images
                        MainSettings.faraway_pixies.append( 
                        (tank.pix, (tank.screen_x + tank.pix_offset_x, tank.screen_y + tank.pix_offset_y )) )
                        MainEngine.add_message(
                            f"{tank.name} has been destroyed!", MainEngine.screen_rect.midbottom, tank.color)
                        
                MainEngine.time += MainEngine.sts.tres

            MainEngine.manage_events(pygame.event.get())    
            # draw FPS to measure performance
            FPS = MainEngine.clock.get_fps()
            if FPS < lowest_FPS and FPS > 0:
                lowest_FPS = FPS
            MainEngine.display_temp_text(
                (f"FPS:  {int(FPS)}", MainEngine.screen_rect.midtop, settings.DEFAULT_FONT_COLOR) )   
                
            if len(MainEngine.tanks) == 1 and not MainEngine.tanks[0].balls:
                if not MainEngine.tanks[0].dying:
                    MainEngine.tanks[0].winner = True
                MainEngine.tanks[0].remove_effect_pixie("spellready icon")
                MainEngine.game_over = True
                for role in settings.AI_NATURES:
                    if role.lower() in MainEngine.tanks[0].name.lower():
                        counts[role] += 1

            elif not MainEngine.tanks:
                MainEngine.game_over = True

            # gc.collect()

            pygame.display.flip()

        # ENDGAME SCREEN *******************************************
        MainEngine.endgame_screen()
        if MainEngine.sts.debug:
            MainEngine.sts.write_to_log("Exiting game outside of main loop and writing log file...")
            MainEngine.sts.output_log_to_file()
    except Exception as err:
        print(err)
        print("\n")
        print(traceback.format_exc())
        counts["errors"] += 1
    finally:
        print(counts)        
        print(f"\nLowest FPS:  {lowest_FPS}")
        del MainEngine
        del MainSettings
        gc.collect()