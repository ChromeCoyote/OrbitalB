# Main Game "Engine"


import math, pygame, random, sys
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

    def create_comet(self):
        comet_created = False
        cnt = len(self.celestials)
        if cnt > 0:
            self.celestials.append(cosmos.Celestial(self.sts))
            self.celestials[-1].set_attr(f'Comet #{cnt + 1}', False, settings.COMET_DENSITY, \
                settings.COMET_RADIUS, settings.DEFAULT_COMET_COLOR)
            speed = math.sqrt(settings.GRAV_CONST * self.celestials[0].mass / \
                self.celestials[-1].radius) / 3
            x_on_screen = int(
                self.celestials[-1].width + self.celestials[-1].screen_rad)
            y_on_screen = random.randint(0, self.celestials[-1].height)
            self.celestials[-1].place_on_screen(x_on_screen, y_on_screen)
            self.celestials[-1].set_v(-speed, 0)
            asteroid_created = True
            if self.celestials[-1].sts.debug:
                self.sts.write_to_log(f"{self.celestials[-1].name} created!")
                self.celestials[-1].write_values()

        return comet_created
    
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
                self.tanks[-1].name = f"Tank #{num_tanks} {self.tanks[-1].snail_color} Player Tank"
            else:
                self.tanks[-1].player_tank = False
                self.tanks[-1].name = f"Tank #{num_tanks} {self.tanks[-1].snail_color} AI Tank"

            for tank_ind in range(0, num_tanks):
                self.tanks[tank_ind].pos_angle = tank_ind*(2*math.pi / num_tanks) + settings.DEFAULT_POSITION_ANGLE

            self.tanks[-1].get_surface_pos()
            self.tanks[-1].reset_default_launch()

            self.tanks[-1].screen_rad = settings.DEFAULT_SNAIL_SCREEN_RADIUS
            self.tanks[-1].load_snail_frames()
            self.tanks[-1].set_frames(self.tanks[-1].walking_frames)
            self.tanks[-1].load_frame(0)
            self.tanks[-1].fix_snail_frame()

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
                    if tank.player_tank and not tank.dying:
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
        for tank in self.tanks:
            if not tank.player_tank and not tank.dying:
                tank.make_choices(self.tanks)

    def draw_objects(self):
        for body in self.celestials:
            if not body.homeworld:
                body.draw_bodycircle()

        if self.tanks:
            for tank in self.tanks:
                if tank.balls:
                    for ball in tank.balls:
                        if ball.active or ball.exploding:
                            ball.draw_bodycircle()
                if tank.chambered_ball:
                    tank.draw_launch_v()
                tank.draw_bodycircle()

        self.celestials[0].draw_bodycircle()
        
    def display_game_message(self, message, location, font_color):
        text_to_show = pygame.font.Font.render(
            self.font, message, True, font_color)
        text_rect = text_to_show.get_rect()
        
        if location == self.screen_rect.top:
            text_rect.top = location
        elif location == self.screen_rect.left:
            text_rect.left = location
        elif location == self.screen_rect.bottom:
            text_rect.bottom = location
        elif location == self.screen_rect.right:
            text_rect.right = location
        elif location == self.screen_rect.topleft:
            text_rect.topleft = location
        elif location == self.screen_rect.bottomleft:
            text_rect.bottomleft = location
        elif location == self.screen_rect.topright:
            text_rect.topright = location
        elif location == self.screen_rect.bottomright:
            text_rect.bottomright = location
        elif location == self.screen_rect.midtop:
            text_rect.midtop = location
        elif location == self.screen_rect.midleft:
            text_rect.midleft = location
        elif location == self.screen_rect.midbottom:
            text_rect.midbottom = location
        elif location == self.screen_rect.midright:
            text_rect.midrighgt = location
        elif location == self.screen_rect.center:
            text_rect.center = location
        else:
            text_rect.center = self.screen_rect.center
            self.sts.write_to_log("ERROR:  Invalid text location sent to Engine.dispay_game_message()")
        
        self.sts.screen.blit(text_to_show, text_rect)

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

        while wait4me:
            self.ticktock()

            self.create_universe()

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

            self.set_font_size(48)
            if self.tanks and self.tanks[0].winner:
                    for ball in self.tanks[0].balls:
                        if ball.exploding:
                            ball.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))

                    self.draw_objects()
                
                    self.display_game_message(
                            f"{self.tanks[0].name} wins!", self.screen_rect.center, self.tanks[0].color)
            elif not self.tanks:
                self.draw_objects()
                self.display_game_message(
                        "All tanks destroyed!", self.screen_rect.center, settings.DEFAULT_FONT_COLOR)

            self.set_font_size(64)
            self.display_game_message(
                    f"GAME OVER", self.screen_rect.midbottom, (random.randint(0,255), random.randint(0,255), random.randint(0,255)))
            pygame.display.flip()
                    
        if self.sts.debug:
            self.sts.write_to_log("Game over, exiting...")

    def meteor_shower(self):
        if self.sts.meteor_shower:
            chance = random.uniform(0,1)
            if chance < self.sts.asteroid_chance:
                self.create_asteroid()