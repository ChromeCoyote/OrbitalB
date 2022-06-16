# Code for projectile

import cosmos
import settings
import pygame
import math

class Cannonball(cosmos.Celestial):
    """ Class for projectile (or projectiles), child of Celestial """

    def __init__(self, sts, celestials):
        """ Initialize variables for projectile """
        super().__init__(sts)

        self.name = 'Cannonball'

        self.homeworld = False       # not the homeworld ;)
        self.screen_rad = 1         # small yet visible object for testing
        self.color = (255, 255, 255)      # white

        self.celestials = celestials

        for body in celestials:
            if body.homeworld == True:
                self.homeworld = body
            else:
                self.homeworld = cosmos.Celestial(sts)

        self.escape_v = math.sqrt(2 * settings.GRAV_CONST * \
            self.homeworld.mass / self.homeworld.radius)

        self.pos_angle = 90     # initial posistion is 90 degrees on surface
        self.launch_angle = self.pos_angle + 45     # firing angle
        self.set_launch_point()     # initalize x, y posistion
        self.vx = 0.5 * self.escape_v * math.cos(self.launch_angle)
        self.vy = 0.5 * self.escape_v * math.sin(self.launch_angle)

    def update_celestials(self, celestials):
        """ update homewold values """
        self.celestials = celestials
        for body in celestials:
            if body.homeworld == True:
                self.homeworld = body

    def set_launch_point(self):
        """ set launch point based on position angle (pos_angle) """
        self.x = self.homeworld.radius * math.cos(self.pos_angle) \
            + self.homeworld.x
        self.y = self.homeworld.radius * math.sin(self.pos_angle) \
            + self.homeworld.y
        super().set_screenxy()
