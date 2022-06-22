# Data and functions for the world and moon (mass, radius, etc.)

import math
import settings
import pygame
import numpy

DEFAULT_BODY_COLOR = (102, 51, 0)       # brown color

def bounce_v(m1, m2, x1, x2, v1, v2):
    """ Calculate new velocity for body 1 """
    # set up scalar factor
    factor1 = ( (2 * m1) / (m1 + m2) )
    factor1 /= ( (x1[0] - x2[0])**2 + (x1[1] - x2[1])**2 )
    factor1 *= numpy.dot( numpy.subtract(v1, v2), \
        numpy.subtract(x1, x2) )
    print(f"{factor1}")

    # calculate new velocities after reflection
    vel1 = numpy.subtract(v1, numpy.array(
        numpy.subtract(x1, x2))*factor1)

    return vel1

class Celestial:
    """ Class to hold data & functions for worlds & moons """

    def __init__(self, sts):
        """Initialize variables for world.  Default is for the Earth."""
        # attributes of the body for calculations
        self.name = 'Earth'             # name of the body
        self.homeworld = True           # homeworld or not?
        self.radius = settings.EARTH_RADIUS      # radius of body in km
        self.density = settings.EARTH_DENSITY
        self.mass = self.get_mass()

        self.x = 0                      # math x coordinate in km
        self.y = 0                      # math y coordinate in km
        self.vx = 0                     # x component of velocity in km/s
        self.vy = 0                     # y component of velocity in km/s
        self.speed = 0                  # speed of body
        self.ax = 0                     # x component of acceleration in m/s
        self.ay = 0                     # y component of acceleration in m/s

        self.sts = sts              # imported settings object

        self.width = 0              # screen width
        self.height = 0             # screen height

        # attributes of the body for display on the screen
        self.screen_x = 0
        self.screen_y = 0
        self.color = DEFAULT_BODY_COLOR

        # gets current resolution values for current windows.
        # If no windows is inialized, sets resolution to 0, which causes
        # errors
        if self.sts.screen != None:
            (self.width, self.height) = pygame.display.get_window_size()
        else:
            print("Warning!  No screen inialized!")

        self.set_screenxy()     # set screen x and y coordinates

        # set screen radius
        self.screen_rad = self.radius * sts.screen_dist_scale

    def get_mass(self):
        """ Sets mass of body based on radius and density """
        vol = (4/3)*math.pi*(self.radius*1000)**3      # in cubic meters
        return (self.density * vol)

    def set_xy(self, x, y):
        """Set x and y coordinates for the body"""
        self.x = x
        self.y = y
        self.set_screenxy()

    def set_v(self, vx, vy):
        """Set velocity of body"""
        self.vx = vx
        self.vy = vy

    def get_speed(self):
        """set and return speed |v|"""
        self.speed = math.sqrt(self.vx**2 + self.vy**2)
        return self.speed

    def get_xy(self):
        """Get x and y coordinates"""
        return (self.x,self.y)

    def get_v(self):
        """Get coordinates of velocity"""
        return (self.vx, self.vy)

    def get_dist(self, x, y):
        """Get magnitude of the distance from point"""
        return math.sqrt((x - self.x)**2 + (y - self.y)**2)

    def get_vect(self, x, y):
        """Get vector pointing from x and y to body"""
        return (x - self.x, y - self.y)

    def get_unit(self, x, y):
        """Get unit vector pointing from x and y to body"""
        [unit_x, unit_y] = self.get_vect(x, y)
        dist = self.get_dist(x, y)
        unit_x /= dist
        unit_y /= dist
        return (unit_x, unit_y)

    def set_attr(self, name, home, density, radius, color):
        """Set name, mass and radius for the body"""
        self.name = name
        self.homeworld = home
        self.density = density
        self.radius = radius
        self.mass = self.get_mass()
        self.screen_rad = self.radius * self.sts.screen_dist_scale
        self.color = color

    def set_screenxy(self):
        """ Set current x and y coordinates to screen's coordinates """
        self.screen_x = int((self.x * self.sts.screen_dist_scale) + \
            (self.width / 2) )
        self.screen_y = int((-self.y * self.sts.screen_dist_scale) + \
            (self.height / 2) )

    def get_screenxy(self):
        """Get x and y coordinates on screen"""
        self.set_screenxy()
        return (self.screen_x, self.screen_y)

    def draw_bodycircle(self):
        """ Draws a simple circle to represent world """
        pygame.draw.circle(self.sts.screen, self.color, (self.screen_x, \
            self.screen_y), self.screen_rad)

    def update_settings(sts):
        """ Updates settings class object """
        self.sts = sts

    def display_values(self):
        """Print properties of world"""
        print(f"The celestial body's name is {self.name}.")
        if self.homeworld == True:
            print("This is the homeworld.")
        else:
            print("This is not the homeworld.")
        print(f"The celestial boyd's density is {self.density} kg/m^3.")
        print(f"The celestial body's mass is {self.mass} kg.")
        print(f"The Earth's mass is {settings.EARTH_MASS} kg.")
        print(f"The celestial body's radius is {self.radius} km.")
        print(f"The celestial body's coordinates are ({self.x}, {self.y}).")
        print(f"The celestial body's velocity is ({self.vx}, {self.vy}).")
        print(f"The celestial body's speed is {self.get_speed()} km/s.")
        print(f"The celestial body's acceleration is ({self.ax}, {self.ay}).")         
        print(f"The celestial body's screen x and y coordinates are ",end='')
        print(f"({self.screen_x}, {self.screen_y}).")
        print(f"The celestial body's screen radius is {self.screen_rad}.")

    def get_accel(self, celestial):
        """ Calculate acceleration from other celestial body"""
        a_mag = settings.GRAV_CONST * celestial.mass / \
            ((self.get_dist(celestial.x, celestial.y))**2)
        (x, y) = self.get_unit(celestial.x, celestial.y)
        x *= a_mag
        y *= a_mag
        return (x,y)

    def set_accel(self, celestials):
        """ get acceleration from all celestial bodies """
        self.ax = 0     # reset current acceleration
        self.ay = 0
        for celestial in celestials:
            if celestial.name != self.name:
                (addx, addy) = self.get_accel(celestial)
                self.ax += addx
                self.ay += addy

    def accelerate(self, celestials):
        """ Change celestial body's velocity """
        self.set_accel(celestials)
        self.vx += self.ax * self.sts.tres
        self.vy += self.ay * self.sts.tres

    def bounce(self, celestials):
        """ Check for collision & reflect if so """
        rel_dist = 0            # relative distance between bodies
        combo_rad = 0

        addx = 0                # for adjusting position vectors
        addy = 0

        for celestial in celestials:
            if celestial.name != self.name:
                rel_dist = self.get_dist(celestial.x, celestial.y)
                combo_rad = self.radius + celestial.radius
                if rel_dist < combo_rad:    # if spheres overlap...

                    # first, reset coordinates to eliminate overlap
                    (addx, addy) = self.get_unit(celestial.x, celestial.y)
                    addx = -addx
                    addy = -addy
                    self.x += addx * abs(rel_dist - combo_rad)
                    self.y += addy * abs(rel_dist - combo_rad)
                    self.set_screenxy()

                    oldvx = self.vx     # placeholders for old self velocity
                    oldvy = self.vy

                    # assign new velocities and convert to km, km/s
                    # if self.homeworld == False:
                    (self.vx, self.vy) = bounce_v( \
                        self.mass, celestial.mass, \
                        (self.x, self.y), \
                        (celestial.x, celestial.y), \
                        (self.vx, self.vy), \
                        (celestial.vx, celestial.vy) )
                    self.vx *= math.sqrt(self.sts.energy_loss)
                    self.vy *= math.sqrt(self.sts.energy_loss)
                    # if celestial.homeworld == False:
                    (celestial.vx, celestial.vy) = bounce_v(
                        celestial.mass, self.mass, \
                        (celestial.x, celestial.y), \
                        (self.x, self.y), \
                        (celestial.vx, celestial.vy), \
                        (oldvx, oldvy) )
                    celestial.vx *= math.sqrt(self.sts.energy_loss)
                    celestial.vy *= math.sqrt(self.sts.energy_loss)

    def move(self, celestials):
        """ Move object based on current velocity """
        self.accelerate(celestials)
        self.x += self.vx * self.sts.tres
        self.y += self.vy * self.sts.tres
        self.set_screenxy()
