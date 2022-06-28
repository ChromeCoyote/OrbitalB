# Main Game "Engine"

import math, pygame, random, sys

import numpy

from numpy import multiply
import settings, cosmos, tank, cannonball

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
            home_created = True

        return home_created

    def create_moon(self):
        moon_created = False

        cnt = len(self.celestials)
        if cnt > 0:
            self.celestials.append(cosmos.Celestial(self.sts))
            self.celestials[-1].set_attr(f'Moon #{cnt + 1}', False, settings.LUNA_DENSITY, \
                settings.LUNA_RADIUS, (
                    random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)) )
            speed = math.sqrt(settings.GRAV_CONST * self.celestials[0].mass / \
                self.celestials[-1].radius) / 3
            orbit_dist = self.celestials[0].radius * 2
            orbit_ang = random.uniform(0, round(2*math.pi, 2))
            self.celestials[-1].set_xy(orbit_dist*math.cos(orbit_ang), orbit_dist*math.sin(orbit_ang))
            self.celestials[-1].set_v(-speed*math.sin(orbit_ang), speed*math.cos(orbit_ang))
            moon_created = True
        
        return moon_created

    def create_tank(self):
        tank_created = False
        
        if len(self.celestials) > 0:
            self.tanks.append(tank.Tank(self.sts, self.celestials))
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
                    print("\nQuit through pygame...")
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                for tank in self.tanks:
                    if tank.player_tank:
                        if event.key == tank.chamber_ball_key:
                            if not tank.chamber_ball():
                                if self.sts.debug:
                                    print("\nError chambering ball, already one in chamber...")
                        elif event.key == tank.fire_ball_key:
                            if not tank.fire_ball():
                                if self.sts.debug:
                                    print("\nError firing ball:  none chambered")
                        elif event.key == tank.increase_angle_key and tank.chambered_ball:
                            tank.launch_angle += tank.radian_step
                            tank.fix_launch_velocity()
                            # print("\n")
                            # ball.display_ball_values()
                        elif event.key == tank.decrease_angle_key and tank.chambered_ball:
                            tank.launch_angle -= tank.radian_step
                            tank.fix_launch_velocity()
                            # print("\n")
                            # ball.display_ball_values()
                        elif event.key == tank.increase_speed_key and tank.chambered_ball:
                            tank.launch_speed += tank.speed_step
                            tank.fix_launch_velocity()
                        elif event.key == tank.decrease_speed_key and tank.chambered_ball:
                            tank.launch_speed -= tank.speed_step
                            tank.fix_launch_velocity()
                        elif event.key == tank.move_CCW_key and not tank.chambered_ball:
                            tank.pos_angle += tank.radian_step
                            tank.get_surface_pos()
                        elif event.key == tank.move_CW_key and not tank.chambered_ball:
                            tank.pos_angle -= tank.radian_step
                            tank.get_surface_pos()
                        elif event.key == tank.detonate_ball_key:
                            tank.detonate_ball()

    def draw_objects(self):
        for body in self.celestials:
            body.draw_bodycircle()
        
        for tank in self.tanks:
            tank.draw_bodycircle()
            if tank.chambered_ball:
                tank.draw_launch_v()
            for ball in tank.balls:
                if ball.active or ball.exploding:
                    ball.draw_bodycircle()

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
            print("ERROR:  Invalid text location sent to dispay_game_message")
        
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