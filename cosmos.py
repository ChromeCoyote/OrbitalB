# Data and functions for the world and moon (mass, radius, etc.)

# from locale import normalize
import math
from turtle import width
import settings
import pygame
import numpy
import random

def rotate_vector(r, ang):
    cosang = math.cos(ang)
    sinang = math.sin(ang)

    x2 = cosang*r[0] - sinang*r[1]
    y2 = sinang*r[0] + cosang*r[1]

    return(x2, y2)

def normalize(r):
        """ normalize given vector """
        mag = math.sqrt(r[0]**2 + r[1]**2)
        if mag == 0:
            [returnx, returny] = [0, 0]
        else:
            [returnx, returny] = numpy.multiply(1/mag, r)
        return (returnx, returny)

def bounce_v(m1, m2, x1, x2, v1, v2):
    """ Calculate new velocity for body 1 """
    # set up scalar factor
    j1 = normalize(numpy.subtract(x2,x1))
    j2 = normalize(numpy.subtract(x1,x2))
    
    factor1 = numpy.dot(j1, numpy.subtract(v2, v1))
    factor1 *= ( 2 / (m1*(1/m1 + 1/m2)) )

    factor2 = numpy.dot(j2, numpy.subtract(v1, v2))
    factor2 *= ( 2 / (m2*(1/m1 + 1/m2)) )

    # calculate new velocities after reflection
    vel1 = numpy.add(v1, numpy.multiply(factor1, j1))
    vel2 = numpy.add(v2, numpy.multiply(factor2, j2))

    return (vel1, vel2)

def break_celestial(broke_body, celestials, break_plane):
    if broke_body.radius >= broke_body.sts.crit_radius:
        broke_body.radius /= 2
        broke_body.get_mass()
        broke_body.set_screen_radius()
        if broke_body.sts.debug:
            print(f"\n{broke_body.name} has been shrunk by another...")
            broke_body.display_values()

        celestials.append(Celestial(broke_body.sts))
        celestials[-1].set_attr(
            (broke_body.name + f'-{random.randint(0, 10000)}'), False, 
                broke_body.density, broke_body.radius, broke_body.color)
        celestials[-1].vx = broke_body.vx
        celestials[-1].vy = broke_body.vy
        celestials[-1].x = broke_body.x
        celestials[-1].y = broke_body.y
        if broke_body.sts.debug:
            print(f"\n{celestials[-1].name} has been created by another...")
            celestials[-1].display_values()

        # old_displacement is a vector that defines displacement of old body's position vector
        # rotate this vector 90-degrees clockwise...
        old_displacement = rotate_vector(break_plane, -math.pi/2)
        # make the vector length equal to new radius...
        old_displacement = numpy.multiply(broke_body.radius, old_displacement)
        # then displace position vector by that much.  This makes room for new body
        # Old body by is pushed west if heading east, or east if heading west
        [broke_body.x, broke_body.y] = numpy.subtract([broke_body.x, broke_body.y], old_displacement)
        broke_body.get_screenxy()
        # new body is pushed the other direction           
        [celestials[-1].x, celestials[-1].y] = numpy.add(
            [celestials[-1].x, celestials[-1].y], old_displacement)
        celestials[-1].get_screenxy()

        broke_body.bounce(celestials[-1])
     
        if broke_body.sts.debug:
            print(f"\nNew values for {broke_body.name}:")
            broke_body.display_values()
        if broke_body.sts.debug:
            print(f"\nNew values for {celestials[-1].name}:")
            celestials[-1].display_values()
    elif not broke_body.homeworld:
        broke_body.active = False
        if broke_body.sts.debug:
            print(f"{broke_body.name} has been marked for destruction by another...")

def check_celestials(celestials):
    for celestial in celestials[:]:
        if not celestial.active and not celestial.homeworld:
            if celestials[0].sts.debug:
                print(f"\n{celestial.name} being destroyed...")    
            celestials.remove(celestial)
            if celestials[0].sts.debug:
                print(f"Success!")    
                    
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

        # state of the body
        self.active = True               # starts out alive
        self.gravity = True             # by default, exerts gravity

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
        self.color = settings.DEFAULT_BODY_COLOR

        # gets current resolution values for current windows.
        # If no windows is inialized, sets resolution to 0, which causes
        # errors
        if self.sts.screen != None:
            (self.width, self.height) = pygame.display.get_window_size()
        else:
            print("Warning!  No screen inialized!")

        # reset screen x and y coordinates
        self.get_screenxy()

        # set screen radius
        self.set_screen_radius()

    def set_screen_radius(self):
        self.screen_rad = self.radius * self.sts.screen_dist_scale
    
    def get_mass(self):
        """ Sets mass of body based on radius and density """
        vol = (4/3)*math.pi*(self.radius*1000)**3      # in cubic meters
        return (self.density * vol)

    def set_xy(self, x, y):
        """Set x and y coordinates for the body"""
        self.x = x
        self.y = y
        self.get_screenxy()

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
        return normalize([unit_x, unit_y])

    def set_attr(self, name, home, density, radius, color):
        """Set name, mass and radius for the body"""
        self.name = name
        self.homeworld = home
        self.density = density
        self.radius = radius
        self.mass = self.get_mass()
        self.set_screen_radius()
        self.color = color

    def set_screenxy(self, X, Y):
        """ Set current x and y coordinates to screen's coordinates """
        returnx = int((X * self.sts.screen_dist_scale) + \
            (self.width / 2) )
        returny = int((-Y * self.sts.screen_dist_scale) + \
            (self.height / 2) )
        return (returnx, returny)

    def get_screenxy(self):
        """Get x and y coordinates on screen"""
        (self.screen_x, self.screen_y) = self.set_screenxy(self.x, self.y)
        return (self.screen_x, self.screen_y)

    def draw_bodycircle(self):
        """ Draws a simple circle to represent world """
        pygame.draw.circle(self.sts.screen, self.color, (self.screen_x, \
            self.screen_y), self.screen_rad)

    def update_settings(new_settings):
        """ Updates settings class object """
        self.sts = new_settings

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

    def check_hit(self, celestial):
        hit = False
        
        rel_dist = self.get_dist(celestial.x, celestial.y)
        combo_rad = self.radius + celestial.radius
        if rel_dist < combo_rad:    # if spheres overlap...
            hit = True
        
        return hit

    def fix_overlap(self, celestial):
        """ Fix overlapping celestials """
        # calculated relative distance
        rel_dist = self.get_dist(celestial.x, celestial.y)
        # add together radii
        combo_rad = self.radius + celestial.radius
        if rel_dist < combo_rad:
            (addx, addy) = self.get_unit(celestial.x, celestial.y)
            addx *= -1
            addy *= -1
            self.x += addx * abs(rel_dist - combo_rad)
            self.y += addy * abs(rel_dist - combo_rad)
            self.get_screenxy()
    
    def bounce_all(self, celestials):
        """ Check for collision & reflect if so """
        
        for celestial in celestials:
            if celestial.name != self.name and self.check_hit(celestial):
                    # first, reset coordinates to eliminate overlap
                    self.fix_overlap(celestial)
                    # assign new velocities and convert to km, km/s
                    self.bounce(celestial)
                    
    def bounce(self, celestial):
        """ bounce self off of celestial """
        
        self.fix_overlap(celestial)
        # assign new velocities and convert to km, km/s
        ([self.vx, self.vy], [celestial.vx, celestial.vy]) = bounce_v( \
            self.mass, celestial.mass, \
            [self.x, self.y], \
            [celestial.x, celestial.y], \
            [self.vx, self.vy], \
            [celestial.vx, celestial.vy] )
        self.vx *= math.sqrt(self.sts.energy_loss)
        self.vy *= math.sqrt(self.sts.energy_loss)
        celestial.vx *= math.sqrt(self.sts.energy_loss)
        celestial.vy *= math.sqrt(self.sts.energy_loss)

    def break_self(self, celestials, break_plane):
        if self.radius >= self.sts.crit_radius:                       
            self.radius /= 2
            self.get_mass()
            self.set_screen_radius()
            if self.sts.debug:
                print(f"\n{self.name} has shrunk itself...")
                self.display_values()
        
            celestials.append(Celestial(self.sts))
            celestials[-1].set_attr(
                (self.name + f'-{random.randint(0, 10000)}'), False, 
                    self.density, self.radius, self.color)
            celestials[-1].vx = self.vx
            celestials[-1].vy = self.vy
            celestials[-1].x = self.x
            celestials[-1].y = self.y
            if self.sts.debug:
                print(f"\n{celestials[-1].name} has been created by {self.name}...")
                celestials[-1].display_values()
           
            # old_displacement is a vector that defines displacement of old body's position vector
            # rotate this vector 90-degrees clockwise...
            old_displacement = rotate_vector(break_plane, -math.pi/2)
            # make the vector length equal to new radius...
            old_displacement = numpy.multiply(self.radius, old_displacement)
            # then displace position vector by that much.  This makes room for new body
            # Old body by is pushed west if heading east, or east if heading west
            [self.x, self.y] = numpy.subtract([self.x, self.y], old_displacement)
            self.get_screenxy()
            # new body is pushed the other direction           
            [celestials[-1].x, celestials[-1].y] = numpy.add(
                [celestials[-1].x, celestials[-1].y], old_displacement)
            celestials[-1].get_screenxy()

            self.bounce(celestials[-1])

            if self.sts.debug:
                print(f"\nNew vlues for {self.name}:")
                self.display_values()
            
            if self.sts.debug:
                print(f"\nNew valuse for {celestials[-1].name}")
                celestials[-1].display_values()
        elif not self.homeworld:
            self.active = False
            if self.sts.debug:
                print(f"\n{self.name} has marked itself for destruction...")

    def shatter(self, celestials):
        """ Check for collision, break apart and bounce if so """
        for celestial in celestials[:]:
            if celestial.name != self.name and self.check_hit(celestial):
                    if self.mass > (celestial.mass * self.sts.crit_mass) and not celestial.homeworld:
                        self.bounce(celestial)
                        break_celestial(celestial, celestials, celestial.get_unit(self.x, self.y))
                    elif (self.mass * self.sts.crit_mass) < celestial.mass and not self.homeworld:
                        self.bounce(celestial)
                        self.break_self(celestials, self.get_unit(celestial.x,  celestial.y))
                    # fix overlap if any
                    self.fix_overlap(celestial)
                                                               
    def check_off_screen(self):
        if (self.screen_x + self.screen_rad) < 0:
            self.active = False
            if self.sts.debug:
                print(f"\n{self.name} is being removed for being too far left off-screen...")
        elif (self.screen_x - self.screen_rad) > self.width:
            self.active = False
            if self.sts.debug:
                print(f"\n{self.name} is being removed for being too far right off-screen...")
        elif (self.screen_y + self.screen_rad) < 0:
            self.active = False
            if self.sts.debug:
                print(f"\n{self.name} is being removed for being too far up off-screen...")
        elif (self.screen_y + self.screen_rad) > self.height:
            self.active = False
            if self.sts.debug:
                print(f"\n{self.name} is being removed for being too far down off-screen...")
   
    def move(self, celestials):
        """ Move object based on current velocity """
        self.accelerate(celestials)
        self.x += self.vx * self.sts.tres
        self.y += self.vy * self.sts.tres
        self.get_screenxy()
        self.check_off_screen()

    def get_collision_point(self, celestial):
        collide_x = ( (self.x * celestial.radius) + (celestial.x * self.radius) ) / (self.radius + celestial.radius)
        collide_y = ( (self.y * celestial.radius) + (celestial.y * self.radius) ) / (self.radius + celestial.radius)
        return (collide_x, collide_y)

    def displace(self, displacement):
        [self.x, self.y] = numpy.add([self.x, self.y], displacement)
        self.get_screenxy()