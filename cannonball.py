# Code for projectile

import cosmos
import settings
import pygame
import math
import random

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
        self.homeworld = cosmos.Celestial(sts)
        for body in celestials:
            if body.homeworld == True:
                self.homeworld = body
   
        self.celestials = celestials
        
        self.active = False     # starts out not launched (dead)
        self.chambered = False
        self.exploding = False
        self.armed = False

        self.fuse_timer = 0
        self.explode_timer = 0

        self.speed = 0
        self.vx = 0
        self.vy = 0

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
        self.active = False
        self.armed = False
        self.exploding = True
        self.radius = self.explode_radius
        self.screen_rad = self.explode_radius * self.sts.screen_dist_scale
    
    def set_explode_force_mag(self, time):
        self.explode_force_mag = self.explode_energy / time

    def check_impact(self, celestials):
        hit = False
       
        for celestial in celestials:
            if celestial.name != self.name and super().check_hit(celestial):
                hit = True
                # self.homeworld = celestial      # changes homeworld for explosion
                if self.armed:
                    self.explode()
                else:
                    self.active = False

                if self.exploding:
                    (ax, ay) = super().get_unit(celestial.x, celestial.y)
                    ax *= self.explode_force_mag
                    ay *= self.explode_force_mag
                    celestial.vx += ax * self.sts.tres
                    celestial.vy += ay * self.sts.tres
                    if celestial.radius < self.sts.crit_explode_radius:
                        celestial.break_self(celestials)

        return hit

    def display_ball_values(self):
        """Print properties of cannonball"""
        print("\n")
        super().display_values()
        if self.active:
            print("\nThis ball is active.")
        if self.chambered:
            print("\nThis ball is chambered.")
        if self.exploding:
            print("\nThis ball is exploding!")
        if self.armed:
            print("\nThis ball is armed.")