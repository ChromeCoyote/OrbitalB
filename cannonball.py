# Code for projectile

import numpy
import cosmos
import settings
import pygame
import math
import random
import time

class Cannonball(cosmos.Celestial):
    """ Class for projectile (or projectiles), child of Celestial """

    def __init__(self, sts, celestials):
        """ Initialize variables for projectile """
        super().__init__(sts)

        self.name = 'Cannonball'

        self.radius = 0.001             # 1 m meter radius
        self.screen_rad = settings.DEFAULT_BALL_SCREEN_RAD

        self.homeworld = False       # not the homeworld ;)
        self.gravity = False            # ignore gravity of this
        self.explode_radius = settings.DEFAULT_EXPLODE_RADIUS
        self.color = settings.DEFAULT_BALL_COLOR

        # find and setup stats for homeworld
        self.homeworld = False
        for body in celestials:
            if body.homeworld == True:
                self.homeworld = body
   
        self.celestials = celestials
        
        self.active = False     # starts out not launched (dead)
        self.chambered = False
        self.exploding = False
        self.armed = False
        self.given_away = False

        # keep track of fuse, explosion timers
        self.fuse_start = 0
        self.explode_start = 0
        
        self.mass = settings.DEFAULT_CANNONBALL_MASS

        self.speed = 0
        self.vx = 0
        self.vy = 0

        self.stuck_to_celestial = False
        self.pos_angle = 0

        # set by another class/function
        self.explode_energy = settings.DEFAULT_EXPLODE_ENERGY
        # self.explode_energy = 0
        self.explode_force_mag = self.explode_energy / self.explode_radius
                                  
    def update_celestials(self, celestials):
        """ update homewold values """
        self.celestials = celestials
        for body in celestials:
            if body.homeworld == True:
                self.homeworld = body
    
    def find_speed(self):
        self.speed = math.sqrt(self.vx**2 + self.vy**2)
            
    def explode(self):
        # self.active = False
        self.armed = False
        self.exploding = True
        # self.radius = self.explode_radius
        # self.screen_rad = self.explode_radius * self.sts.screen_dist_scale
        # self.set_screen_radius()
        self.explode_start = time.time()
    
    def expand(self):
        if self.exploding:
            self.radius = self.explode_radius*( (time.time() - self.explode_start)/settings.DEFAULT_EXPLODE_TIME )
            self.set_screen_radius()
    
    def set_explode_force_mag(self, time):
        self.explode_force_mag = self.explode_energy / time

    def get_surface_pos(self):
        """ set launch point based on position angle (pos_angle) """
        self.x = self.stuck_to_celestial.radius * math.cos(self.pos_angle) \
            + self.stuck_to_celestial.x
        self.y = self.stuck_to_celestial.radius * math.sin(self.pos_angle) \
            + self.stuck_to_celestial.y
        super().get_screenxy()

    def stick_to_celestial(self, celestial):
        if not self.stuck_to_celestial:
            self.stuck_to_celestial = celestial
            (stuck_x, stuck_y) = numpy.subtract(
                [self.x, self.y], [self.stuck_to_celestial.x, self.stuck_to_celestial.y])
            self.pos_angle = math.atan2(stuck_y, stuck_x)
    
    def check_impact(self, tanks):
        hit = False
       
        for celestial in self.celestials:
            if celestial.name != self.name and super().check_hit(celestial):
                hit = True
                # self.homeworld = celestial      # changes homeworld for explosion
                if self.armed:
                    self.explode()
                elif self.exploding:
                    if not self.stuck_to_celestial:
                        self.stick_to_celestial(celestial)
                        (ax, ay) = super().get_unit(celestial.x, celestial.y)
                        ax *= self.explode_force_mag
                        ay *= self.explode_force_mag
                        celestial.vx += ax * self.sts.tres
                        celestial.vy += ay * self.sts.tres
                        if celestial.mass < self.sts.crit_explode_mass:
                            celestial.break_self(self.celestials, celestial.get_unit(self.x, self.y))
                            self.stuck_to_celestial = False
                            self.exploding = False
                            self.active = False
                else:
                    self.active = False
                
        for tank in tanks:
            if self.exploding and super().check_hit(tank):
                hit = True
                tank.active = False
                if self.sts.debug:
                    self.sts.write_to_log(f"{tank.name} has been hit!")
                    
        return hit

    def write_ball_values(self):
        """Print properties of cannonball"""
        super().write_values()
        extra_cannonball_text = []
        extra_cannonball_text.append(f"ADDITIONAL INFORMATION FOR {self.name}:")        
        if self.active:
            extra_cannonball_text.append("This cannonball is active.")
        if self.chambered:
            extra_cannonball_text.append("This cannonball is chambered.")
        if self.exploding:
            extra_cannonball_text.append("This cannonball is exploding!")
        if self.armed:
            extra_cannonball_text.append("This ball is armed.")
        self.sts.write_to_log(extra_cannonball_text)

    def choose_flash_color(self):
        random_flash = random.randint(1, 6)
        if random_flash == 1:
            # Cinnabar
            self.color = (246, 65, 45)
        elif random_flash == 2:
            # Mystic Red
            self.color = (255, 86, 7)
        elif random_flash == 3:
            # Vivid Gamboge
            self.color == (255, 152, 0)
        elif random_flash == 4:
            # Fluorescent Orange
            self.color == (255, 193, 0)
        elif random_flash == 5:
            # Vivid Yellow
            self.color = (255, 236, 25)
        else:
            # White
            self.color = (255, 255, 255)
            
    def flash(self):
        """ Change cannonball color while exploding """
        if self.exploding:
            if random.uniform(0, 1) < settings.DEFAULT_FLASH_CHANCE:
               self.choose_flash_color()