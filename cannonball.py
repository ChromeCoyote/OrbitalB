# Code for projectile

import cosmos
import settings
import pygame
import math

DEFAULT_BALL_COLOR = (255, 255, 255)    # white
# scaling for changes to velocity per key press
DEFAULT_RADIAN_STEP = ((2*math.pi) / 360)
DEFAULT_ARROW_COLOR = (255, 0, 0)       # default arrow color (red)
# divide escape velocity by this to figure velocity change step
DEFAULT_SPEED_DIV = 100        
DEFAULT_POSITION_ANGLE = math.pi / 2     # initial posistion on surface in radians
DEFAULT_FIRING_ANGLE = math.pi / 4       # initial firing angle in radians

class Cannonball(cosmos.Celestial):
    """ Class for projectile (or projectiles), child of Celestial """

    def __init__(self, sts, celestials):
        """ Initialize variables for projectile """
        super().__init__(sts)

        self.name = 'Cannonball'

        self.radius = 1             # 1 meter radius
        
        self.homeworld = False       # not the homeworld ;)
        self.screen_rad = 1         # small yet visible object for testing
        self.color = DEFAULT_BALL_COLOR

        # find and setup stats for homeworld
        self.homeworld = cosmos.Celestial(sts)
        for body in celestials:
            if body.homeworld == True:
                self.homeworld = body
   
        # calculate escape velocity
        self.escape_v = math.sqrt(2 * settings.GRAV_CONST * \
            self.homeworld.mass / self.homeworld.radius)
    
        self.arrow_color = DEFAULT_ARROW_COLOR      # velocity arrow color
        self.radian_step = DEFAULT_RADIAN_STEP
        # step for velocity change with each key press
        self.speed_step = self.escape_v / DEFAULT_SPEED_DIV
        
        self.celestials = celestials
        
        self.alive = False     # starts out not launched (dead)

        self.pos_angle = DEFAULT_POSITION_ANGLE     # initial posistion on surface
        self.launch_angle = self.pos_angle + DEFAULT_FIRING_ANGLE   # default firing angle
        self.set_launch_point()     # initalize x, y posistion
        self.speed = 0.5 * self.escape_v  # set initial speed to half of escape velocity 
        self.vx = self.speed * math.cos(self.launch_angle)
        self.vy = self.speed * math.sin(self.launch_angle)
        
    def reset_velocity(self):
        if self.speed < 0:
            self.speed = 0
        elif self.speed > self.escape_v:
            self.speed = self.escape_v
        
        if self.launch_angle < 0:
            self.launch_angle = 0
        elif self.launch_angle > 2*math.pi:
            self.launch_angle = self.launch_angle % 2*math.pi
        
        self.vx = self.speed * math.cos(self.launch_angle)
        self.vy = self.speed * math.sin(self.launch_angle)
        
    def reset_default_v(self):
        self.speed = 0.5 * self.escape_v            # default speed
        self.launch_angle = self.pos_angle + DEFAULT_FIRING_ANGLE    # default firing angle
        self.reset_velocity()
            
    def update_celestials(self, celestials):
        """ update homewold values """
        self.celestials = celestials
        for body in celestials:
            if body.homeworld == True:
                self.homeworld = body

    def set_launch_point(self):
        """ set launch point based on position angle (pos_angle) """
        self.x = self.homeworld.radius * math.cos(self.pos_angle) \
            + self.homeworld.x + self.radius
        self.y = self.homeworld.radius * math.sin(self.pos_angle) \
            + self.homeworld.y + self.radius
        super().get_screenxy()
        
    def find_speed(self):
        self.speed = math.sqrt(self.vx**2 + self.vy**2)
            
    def check_impact(self, celestials):
        hit = False
        for celestial in celestials:
            if celestial.name != self.name and super().check_hit(celestial):
                hit = True
        return hit
        
    def draw_launch_v(self):
        (tempvx, tempvy) = super().normalize(self.vx, self.vy)
        tempvx *= self.homeworld.radius * (self.speed / self.escape_v)
        tempvx += self.x
        tempvy *= self.homeworld.radius * (self.speed / self.escape_v)
        tempvy += self.y
        (tip_x, tip_y) = super().set_screenxy(tempvx, tempvy)
        # vertex1_x = self.screen_x + self.screen_rad
        # vertex1_y = self.screen_y + self.screen_rad
        # vertex2_x = self.screen_x - self.screen_rad
        # vertex2_y = self.screen_y - self.screen_rad
        # pygame.draw.polygon(self.sts.screen, self.arrow_color, [[tip_x, tip_y], [vertex1_x, vertex1_y], [vertex2_x, vertex2_y]])
        pygame.draw.line(self.sts.screen, self.arrow_color, [self.screen_x, self.screen_y], [tip_x, tip_y])

    def display_ball_values(self):
        """Print properties of cannonball"""
        super().display_values()
        print(f"The cannonball's launch angle is {self.launch_angle} radians.")