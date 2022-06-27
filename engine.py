# Main Game "Engine"

import math, pygame, random, sys
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
    
    def ticktock(self):
        self.clock.tick(self.sts.fps)

    def create_universe(self):
        self.sts.fill_background()
        self.sts.draw_stars()

    def create_homeworld(self):
        home_created = False
        
        if not len(self.celestials):
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
                    if len(self.tanks) > 0:
                        self.tanks[0].display_ball_stats()
                
                    print("\nQuit through pygame...")
                
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == settings.CHAMBER_BALL:
                    if not self.tanks[0].chamber_ball():
                        if self.sts.debug:
                            print("\nError chambering ball, already one in chamber...")
                elif event.key == settings.FIRE_BALL:
                    if not self.tanks[0].fire_ball():
                        if self.sts.debug:
                            print("\nError firing ball:  none chambered")
                elif event.key == settings.INCREASE_ANGLE and self.tanks[0].chambered_ball:
                    self.tanks[0].launch_angle += self.tanks[0].radian_step
                    self.tanks[0].fix_launch_velocity()
                    # print("\n")
                    # ball.display_ball_values()
                elif event.key == settings.DECREASE_ANGLE and self.tanks[0].chambered_ball:
                    self.tanks[0].launch_angle -= self.tanks[0].radian_step
                    self.tanks[0].fix_launch_velocity()
                    # print("\n")
                    # ball.display_ball_values()
                elif event.key == settings.INCREASE_SPEED and self.tanks[0].chambered_ball:
                    self.tanks[0].launch_speed += self.tanks[0].speed_step
                    self.tanks[0].fix_launch_velocity()
                elif event.key == settings.DECREASE_SPEED and self.tanks[0].chambered_ball:
                    self.tanks[0].launch_speed -= self.tanks[0].speed_step
                    self.tanks[0].fix_launch_velocity()
                elif event.key == settings.MOVE_TANK_CCW and not self.tanks[0].chambered_ball:
                    self.tanks[0].pos_angle += self.tanks[0].radian_step
                    self.tanks[0].set_surface_pos()
                elif event.key == settings.MOVE_TANK_CW and not self.tanks[0].chambered_ball:
                    self.tanks[0].pos_angle -= self.tanks[0].radian_step
                    self.tanks[0].set_surface_pos()
                elif event.key == settings.DETONATE_BALL:
                    self.tanks[0].detonate_ball()