# Main Game "Engine"


import math, pygame, random, sys, time
import numpy
import settings, cosmos, tank

class Engine:
    """ Main game engine """
    def __init__(self, sts):
        self.sts = sts

        self.celestials = []         # empty list with all celestials
        self.tanks = []              # empty list with all tanks

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, settings.DEFAULT_FONT_SIZE)
        self.screen_rect = self.sts.screen.get_rect()
        self.time = 0

        self.displacement = (0,0)

        self.snail_colors = ["Green", "Red", "Yellow"]
        self.tank_colors = [
            settings.DEFAULT_TANK_COLOR, 
            settings.DEFAULT_ENEMY_TANK_COLOR,
            settings.DEFAULT_THIRD_TANK_COLOR ]
        self.color_index = 0

        # flags for game over, win
        self.game_over = False

        self.messages = []
        self.screen_message = False
        self.message_rect = False

        if self.sts.sound_on:
            self.sts.load_sounds()

    def set_font_size(self, new_font_size):
        self.font = pygame.font.SysFont(None, new_font_size)
    
    def ticktock(self):
        self.clock.tick(self.sts.fps)

    def create_universe(self):
        self.sts.fill_background()
        self.sts.draw_stars()

    def create_homeworld(self):
        home_created = False
        
        if not self.celestials:
            self.celestials.append(cosmos.Celestial(self.sts))
            self.celestials[0].pick_homeworld_pix()
            home_created = True
            
        return home_created

    def create_moon(self):
        moon_created = False

        cnt = len(self.celestials)
        if cnt > 0:
            if cnt == 1:
                new_moon_color = settings.DEFAULT_LUNA_COLOR
            else:
                new_moon_color = (
                    random.randint(0, 255),random.randint(0, 255),random.randint(0, 255))
            self.celestials.append(cosmos.Celestial(self.sts))
            self.celestials[-1].set_attr(f'Moon #{cnt + 1}', False, settings.LUNA_DENSITY, \
                settings.LUNA_RADIUS, new_moon_color)
            speed = math.sqrt(settings.GRAV_CONST * self.celestials[0].mass / \
                self.celestials[-1].radius) / 3
            orbit_dist = self.celestials[0].radius * 2
            orbit_ang = random.uniform(0, round(2*math.pi, 2))
            self.celestials[-1].set_xy(orbit_dist*math.cos(orbit_ang), orbit_dist*math.sin(orbit_ang))
            self.celestials[-1].set_v(-speed*math.sin(orbit_ang), speed*math.cos(orbit_ang))
            self.celestials[-1].pick_moon_pix()
            
            moon_created = True
        
        return moon_created

    def create_asteroid(self):
        asteroid_created = False
        cnt = len(self.celestials)
        if cnt > 0:
            self.celestials.append(cosmos.Celestial(self.sts))
            self.celestials[-1].set_attr(f'Asteroid #{cnt + 1}', False, settings.CERES_DENSITY, \
                settings.CERES_RADIUS, (
                    random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)) )
            speed = math.sqrt(settings.GRAV_CONST * self.celestials[0].mass / \
                self.celestials[-1].radius) / 3
            x_on_screen = int(
                self.celestials[-1].width + self.celestials[-1].screen_rad)
            y_on_screen = random.randint(0, self.celestials[-1].height)
            self.celestials[-1].place_on_screen(x_on_screen, y_on_screen)
            self.celestials[-1].set_v(-speed, 0)
            self.celestials[-1].pick_dwarf_pix()
            asteroid_created = True
            if self.celestials[-1].sts.debug:
                self.sts.write_to_log(f"{self.celestials[-1].name} created!")
                self.celestials[-1].write_values()

        return asteroid_created

    def create_tank(self, player_tank):
        tank_created = False
        if isinstance(self.celestials, list) and len(self.celestials) > 0:
            num_tanks = len(self.tanks)
        else:
            num_tanks = -1  

        if num_tanks >= 0 and self.color_index < len(self.snail_colors):
            self.tanks.append(tank.Tank(self.sts, self.celestials))
            num_tanks += 1
            
            self.tanks[-1].snail_color = self.snail_colors[self.color_index]
            self.tanks[-1].color = self.tank_colors[self.color_index]
            self.color_index += 1

            if player_tank:
                self.tanks[-1].player_tank = True
                self.tanks[-1].name = f"Snail #{num_tanks} {self.tanks[-1].snail_color} Player"
            else:
                self.tanks[-1].player_tank = False
                self.tanks[-1].name = f"Snail #{num_tanks} {self.tanks[-1].snail_color} " \
                    + random.choice(settings.AI_NATURES)
                if "archer" in self.tanks[-1].name.lower():
                    self.tanks[-1].fire_weight = 0.6
                    self.tanks[-1].spell_weight = 0.1
                elif "mage" in self.tanks[-1].name.lower():
                    self.tanks[-1].spell_weight = 0.6
                    self.tanks[-1].fire_weight = 0.1
                elif "berserker" in self.tanks[-1].name.lower():
                    self.tanks[-1].fire_weight = 0.3
                    self.tanks[-1].spell_weight = 0.1

            self.tanks[-1].screen_rad = settings.DEFAULT_SNAIL_SCREEN_RADIUS
            self.tanks[-1].load_snail_frames()
            self.tanks[-1].set_frames(self.tanks[-1].walking_frames)
            
            for tank_ind in range(0, num_tanks):
                self.tanks[tank_ind].pos_angle = tank_ind*(2*math.pi / num_tanks) + settings.DEFAULT_POSITION_ANGLE
                self.tanks[tank_ind].get_surface_pos()
                self.tanks[tank_ind].reset_default_launch()
                self.tanks[tank_ind].fix_snail_pix()
                self.tanks[tank_ind].load_frame()

            # self.tanks[-1].spell_cooldown = time.time()
            
            if self.sts.debug:
                self.sts.write_to_log(f"{self.tanks[-1].name} successfully created!")        
            
            tank_created = True

        return tank_created

    def manage_events(self, events):
        """ manage events, mostly keystrokes """

        for event in events:
            if event.type == pygame.QUIT:
                if self.sts.debug:
                    if self.tanks:
                        for tank in self.tanks:
                            tank.display_ball_stats()
                    self.sts.write_to_log("Quit through pygame and writing log file...")
                    self.sts.output_log_to_file()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                for tank in self.tanks:
                    if tank.player_tank and not tank.frozen:
                        if event.key == tank.chamber_ball_key:
                            if not tank.chamber_ball():
                                if self.sts.debug:
                                    self.sts.write_to_log(
                                        f"ERROR: {tank.name} can't chamber cannonball, already one in chamber...")
                            elif self.sts.debug:
                                self.sts.write_to_log(f"{tank.name} chambered cannonball...")
                                tank.balls[-1].write_ball_values()
                        elif event.key == tank.fire_ball_key:
                            if not tank.fire_ball():
                                if self.sts.debug:
                                    self.sts.write_to_log(
                                        f"ERROR: {tank.name} can't fire cannonball, nothing chambered...")
                        elif event.key == tank.increase_angle_key and tank.chambered_ball:
                            tank.launch_angle += tank.radian_step
                            tank.fix_launch_velocity()
                        elif event.key == tank.decrease_angle_key and tank.chambered_ball:
                            tank.launch_angle -= tank.radian_step
                            tank.fix_launch_velocity()
                        elif event.key == tank.increase_speed_key and tank.chambered_ball:
                            tank.launch_speed += tank.speed_step
                            tank.fix_launch_velocity()
                        elif event.key == tank.decrease_speed_key and tank.chambered_ball:
                            tank.launch_speed -= tank.speed_step
                            tank.fix_launch_velocity()
                        elif event.key == tank.move_CCW_key and not tank.chambered_ball:
                            tank.move_CCW()
                        elif event.key == tank.move_CW_key and not tank.chambered_ball:
                            tank.move_CW()
                        elif event.key == tank.detonate_ball_key:
                            tank.detonate_ball()
                        elif event.key == tank.eject_ball_key:
                            tank.eject_ball()
                        elif event.key == tank.Spell_shield:
                            tank.Spell_raise_shields()
                        elif event.key == tank.Spell_gravity:
                            tank.Spell_raise_gravity(self.tanks)
                        elif event.key == tank.Spell_ice:
                            tank.Spell_ice_counterspell(self.tanks)
                        elif event.key == tank.Spell_teleport:
                            tank.Spell_teleport_snail(self.tanks)
                        elif event.key == tank.Spell_meteor:
                            tank.Spell_meteor_portal(self.tanks)
                        elif event.key == tank.Spell_clone:
                            tank.Spell_clone_cannonball()
                        elif event.key == tank.Spell_big_ball:
                            tank.Spell_big_cannonball()
                        elif event.key == tank.Spell_wolf:
                            tank.Spell_summon_wolf()
                        elif event.key == tank.Spell_fireball:
                            tank.Spell_homing_fireball(self.tanks)
                        elif event.key == tank.Spell_shock:
                            tank.Spell_shock_strike()

        for tank in self.tanks:
            if not tank.player_tank and not tank.frozen:
                tank.make_choices(self.tanks)

    def draw_objects(self):
        # draw cannonballs and explosions first...
        if len(self.tanks) > 0:
            for tank in self.tanks:
                if tank.balls:
                    for ball in tank.balls:
                        if ball.active or ball.exploding:
                            ball.draw_bodycircle()
        
        # then all celestials but the homeworld....
        for body in self.celestials:
            if not body.homeworld:
                body.draw_bodycircle()

        # then launch arrows, then tanks....
        if len(self.tanks) > 0:
            for tank in self.tanks:
                if tank.chambered_ball:
                    tank.draw_launch_v()
                tank.draw_bodycircle()

        # then the homworld...
        self.celestials[0].draw_bodycircle()

        # then effects...
        if len(self.tanks) > 0:
            for tank in self.tanks:
                if len(tank.effect_pixies) > 0:
                    for pixie in tank.effect_pixies:
                        pixie.draw_bodycircle()

        # then messages...
        self.display_game_message()
        
    def add_message(self, mess_text, mess_location, mess_color):
        """ Add message to message queue"""
        
        # Index 0:  message text
        # Index 1:  message location
        # Index 2:  message color
        # Index 3:  message add time
        self.messages.append( 
            [mess_text, mess_location, mess_color, False ] )
    
    def set_game_message(self):
        """ Display ingame message """

        # Index 0:  message text
        # Index 1:  message location
        # Index 2:  message color
        # Index 3:  time start
        
        self.screen_message = pygame.font.Font.render(
            self.font, self.messages[0][0], True, self.messages[0][2])
        self.message_rect = self.screen_message.get_rect()

        if self.messages[0][1] == self.screen_rect.top:
            self.message_rect.top = self.messages[0][1]
        elif self.messages[0][1] == self.screen_rect.left:
            self.message_rect.left = self.messages[0][1]
        elif self.messages[0][1] == self.screen_rect.bottom:
            self.message_rect.bottom = self.messages[0][1]
        elif self.messages[0][1] == self.screen_rect.right:
            self.message_rect.right = self.messages[0][1]
        elif self.messages[0][1] == self.screen_rect.topleft:
            self.message_rect.topleft = self.messages[0][1]
        elif self.messages[0][1] == self.screen_rect.bottomleft:
            self.message_rect.bottomleft = self.messages[0][1]
        elif self.messages[0][1] == self.screen_rect.topright:
            self.message_rect.topright = self.messages[0][1]
        elif self.messages[0][1] == self.screen_rect.bottomright:
            self.message_rect.bottomright = self.messages[0][1]
        elif self.messages[0][1] == self.screen_rect.midtop:
            self.message_rect.midtop = self.messages[0][1]
        elif self.messages[0][1] == self.screen_rect.midleft:
            self.message_rect.midleft = self.messages[0][1]
        elif self.messages[0][1] == self.screen_rect.midbottom:
            self.message_rect.midbottom = self.messages[0][1]
        elif self.messages[0][1] == self.screen_rect.midright:
            self.message_rect.midright = self.messages[0][1]
        elif self.messages[0][1] == self.screen_rect.center:
            self.message_rect.center = self.messages[0][1]
        else:
            self.message_rect.center = self.screen_rect.center
            if self.sts.debug:
                self.sts.write_to_log(
                    "ERROR:  Invalid text location in self.messages[0] for Engine.set_game_message()")
        
    def display_game_message(self):
        if isinstance(self.messages, list):
            if len(self.messages) > 0:
                if not self.messages[0][3]:
                    self.messages[0][3] = time.time()
                    self.set_game_message()
                    self.sts.screen.blit(self.screen_message, self.message_rect) 
                elif ( time.time() - self.messages[0][3] ) > settings.DEFAULT_MESSAGE_TIME:
                    self.messages.remove(self.messages[0])
                else:
                    self.sts.screen.blit(self.screen_message, self.message_rect)   

    def display_temp_text(self, message):
        temp_text = pygame.font.Font.render(
            self.font, message[0], True, message[2])
        temp_rect = temp_text.get_rect()

        if message[1] == self.screen_rect.top:
            temp_rect.top = message[1]
        elif message[1] == self.screen_rect.left:
            temp_rect.left = message[1]
        elif message[1] == self.screen_rect.bottom:
            temp_rect.bottom = message[1]
        elif message[1] == self.screen_rect.right:
            temp_rect.right = message[1]
        elif message[1] == self.screen_rect.topleft:
            temp_rect.topleft = message[1]
        elif message[1] == self.screen_rect.bottomleft:
            temp_rect.bottomleft = message[1]
        elif message[1] == self.screen_rect.topright:
            temp_rect.topright = message[1]
        elif message[1] == self.screen_rect.bottomright:
            temp_rect.bottomright = message[1]
        elif message[1] == self.screen_rect.midtop:
            temp_rect.midtop = message[1]
        elif message[1] == self.screen_rect.midleft:
            temp_rect.midleft = message[1]
        elif message[1] == self.screen_rect.midbottom:
            temp_rect.midbottom = message[1]
        elif message[1] == self.screen_rect.midright:
            temp_rect.midright = message[1]
        elif message[1] == self.screen_rect.center:
            temp_rect.center = message[1]
        else:
            temp_rect.center = self.screen_rect.center
            if self.sts.debug:
                self.sts.write_to_log(
                "ERROR:  Invalid text location sent to Engine.display_temp_text()")
        
        self.sts.screen.blit(temp_text, temp_rect)

    
    def center_homeworld(self):
        if self.celestials[0].x or self.celestials[0].y:
            self.displacement = numpy.multiply(
                -1, [self.celestials[0].x, self.celestials[0].y])
            for body in self.celestials:
                body.displace(self.displacement)
            for tank in self.tanks:
                tank.get_surface_pos()
                for ball in tank.balls:
                    ball.displace(self.displacement)

    def endgame_screen(self):
        wait4me = True

        # self.set_font_size(48)
        if self.tanks and self.tanks[0].winner:
            self.add_message(
                f"{self.tanks[0].name} wins!", self.screen_rect.midbottom, self.tanks[0].color)
            game_over_color = self.tanks[0].color
        elif not self.tanks:
            self.add_message(
                "All tanks destroyed!", self.screen_rect.midbottom, settings.DEFAULT_FONT_COLOR)
            game_over_color = settings.DEFAULT_FONT_COLOR
        # self.set_font_size(64)
        self.add_message("GAME OVER", self.screen_rect.midbottom, game_over_color)

        while wait4me:
            self.ticktock()

            self.create_universe()
            self.draw_objects()

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    if self.sts.debug:
                        if self.tanks:
                            for tank in self.tanks:
                                tank.display_ball_stats()
                        self.sts.write_to_log("Quit through pygame and writing log file...")
                        self.sts.output_log_to_file()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    wait4me = False
            
            if len(self.messages) == 0:
                wait4me = False
            
            pygame.display.flip()
                    
        if self.sts.debug:
            self.sts.write_to_log("Game over, exiting...")

    def meteor_shower(self):
        if self.sts.meteor_shower:
            chance = random.uniform(0,1)
            if chance < self.sts.asteroid_chance:
                self.create_asteroid()