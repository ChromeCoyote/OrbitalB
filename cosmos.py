# Data and functions for the world and moon (mass, radius, etc.)

# from locale import normalize
import math
import settings
import pygame
import numpy
import random
import os
import time

def rotate_vector(r, ang):
    """ Rotate given vector r by arg in radians """
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

def angle_between(ang1, ang2):
        ang_between = ang1 - ang2
        ang_between = (ang_between + math.pi) % (2*math.pi) - math.pi
        return ang_between

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

def add_celestial_explosion(_celestial, _tanks):
    """ Adds a celestial animation to first tank's ball list """

    # Celsetial explosion can destroy tanks and acts as a large exploding cannonball
    
    # add celestial explosion to first tank's ball list
    _tanks[0].balls.append(Cannonball(_tanks[0].sts, _tanks[0].celestials))
    # explosion is exploding...
    _tanks[0].balls[-1].celestial_explosion = True
    # give name with a random tag
    _tanks[0].balls[-1].name = f"{_celestial.name}'s Explosion-{random.randint(1,10000)}"
    
    # set explosion's position, speed, etc. to exploded celestial
    _tanks[0].balls[-1].vx = _celestial.vx
    _tanks[0].balls[-1].vy = _celestial.vy
    _tanks[0].balls[-1].ax = _celestial.ax
    _tanks[0].balls[-1].ay = _celestial.ay
    _tanks[0].balls[-1].x = _celestial.x
    _tanks[0].balls[-1].y = _celestial.y
    
    # set up parameters
    _tanks[0].balls[-1].get_screenxy()
    _tanks[0].balls[-1].active = True
    _tanks[0].balls[-1].exploding = True
    # given away so can't be detonated
    _tanks[0].balls[-1].given_away = True
    # explosion radius is size of celestial
    _tanks[0].balls[-1].radius = _celestial.radius
    _tanks[0].balls[-1].set_screen_radius()
    _tanks[0].balls[-1].explode_radius = _celestial.radius
    
    # find random frames from default explosion sprite's directory
    _tanks[0].balls[-1].pix_dir = settings.choose_random_directory(settings.EXPLOSIONS_PATH)
    _tanks[0].balls[-1].frame_wait = 1/30
    _tanks[0].balls[-1].load_frames()
    _tanks[0].balls[-1].animate = True
    _tanks[0].balls[-1].animate_repeat = True
   
    # set timers
    _tanks[0].balls[-1].explode_start = time.time()
    _tanks[0].balls[-1].frame_timer = time.time()

    if _tanks[0].sts.debug:
        _tanks[0].balls[-1].write_ball_values()

def break_celestial(broke_body, celestials, break_plane):
    """ Break given celestials in half """

    # This shrinks and clones given celestial.
    # Break plane defines the plane that cuts original celestial in half
            
    if broke_body.mass >= broke_body.sts.crit_mass:
        # cut radius in half
        broke_body.radius /= 2
        # reset parameters
        broke_body.get_mass()
        broke_body.set_screen_radius()
        
        # if Celestial has a sprite...
        if broke_body.pix:
            # reset site of sprite
            broke_body.scale_pix_to_body_circle()
        if broke_body.sts.debug:
            broke_body.sts.write_to_log(f"{broke_body.name} has been shrunk by another...")
            broke_body.write_values()

        # copy shrunk celestial and add it to the celetials list
        celestials.append(Celestial(broke_body.sts))
        # assign new name
        celestials[-1].set_attr(
            (broke_body.name + f'-{random.randint(0, 10000)}'), False, 
                broke_body.density, broke_body.radius, broke_body.color)
        # clone values from original celestial
        celestials[-1].vx = broke_body.vx
        celestials[-1].vy = broke_body.vy
        celestials[-1].x = broke_body.x
        celestials[-1].y = broke_body.y
        
        # If original celestial had a sprite, copy it and rescale it.
        if broke_body.pix:
            celestials[-1].load_pix(broke_body.pix_path)
        if broke_body.sts.debug:
            broke_body.sts.write_to_log(f"{celestials[-1].name} has been created by another...")
            celestials[-1].write_values()

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

        # Bounce the two new elestials away from each other
        broke_body.bounce(celestials[-1])
     
        if broke_body.sts.debug:
            broke_body.sts.write_to_log(f"New values for {broke_body.name}:")
            broke_body.write_values()
        if broke_body.sts.debug:
            broke_body.sts.write_to_log(f"New values for {celestials[-1].name}:")
            celestials[-1].write_values()
    elif not broke_body.homeworld:
        broke_body.active = False
        if broke_body.sts.debug:
            broke_body.sts.write_to_log(f"{broke_body.name} has been marked for destruction by another...")

def check_celestials(celestials):
    """ Check celestials list and remove those marked for removal """
    for celestial in celestials[:]:
        if not celestial.active and not celestial.homeworld:
            if celestials[0].sts.debug:
                celestials[0].sts.write_to_log(f"\n{celestial.name} being destroyed...")    
            celestials.remove(celestial)
            if celestials[0].sts.debug:
                celestials[0].sts.write_to_log(f"Successfully destroyed celestial!")    

# ********************************************************************************************************** 
# *************************** CELESTIALS !!! ****************************************************************
# **********************************************************************************************************

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

        # Storage for sprite/graphic if there is one
        self.pix = False            # active and currently used sprite
        self.pix_path = False       # path to sprite or frames
        self.pix_dir = False        # directory of sprite frames (if any)
        self.pix_frames = False     # list of images that make frames 
        self.pix_frame = 0      # current frame in animation in pix_frames
        self.frame_wait = 1 / self.sts.fps  # default time to wait to change frames
        self.frame_timer = 0        # how long to display each frame, usually 1/FPS
        # offset rendering of sprite by (pix_offset_x, pix_offset_y)
        self.animate = False
        self.animate_repeat = False
        self.animation_finished = False
        self.pix_rotate = False
        self.pix_flip = [False, False]
        self.pix_offset_x = 0       
        self.pix_offset_y = 0
    
        # self.pix_rings = False

        # gets current resolution values for current windows.
        # If no windows is inialized, sets resolution to 0, which causes
        # errors
        if self.sts.screen != None:
            (self.width, self.height) = pygame.display.get_window_size()
        else:
            self.sts.write_to_log("Warning!  No screen inialized!")

        # reset screen x and y coordinates
        self.get_screenxy()

        # set screen radius
        self.set_screen_radius()

    def set_screen_radius(self):
        """ Sets radius in screen pixels given physics radius """
        self.screen_rad = int(self.radius * self.sts.screen_dist_scale)
        if self.screen_rad < 1:
            self.screen_rad = 1
    
    def get_mass(self):
        """ Sets mass of body based on radius and density """
        vol = (4/3)*math.pi*(self.radius*1000)**3      # in cubic meters
        self.mass = self.density * vol
        return self.mass

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

    def convert_from_screen_xy(self, X, Y):
        return_x = int((X - self.width/2)*(1/self.sts.screen_dist_scale))
        return_y = int((self.height/2 - Y)*(1/self.sts.screen_dist_scale))
        return (return_x, return_y)
    
    def get_screenxy(self):
        """Get x and y coordinates on screen"""
        (self.screen_x, self.screen_y) = self.set_screenxy(self.x, self.y)
        return (self.screen_x, self.screen_y)

    def place_on_screen(self, X, Y):
        """ Set object's game (x,y) coordinates to coordinates on screen """    
        (self.x, self.y) = self.convert_from_screen_xy(X, Y)
        
    def draw_bodycircle(self):
        """ Draws a simple circle to represent world """
        if self.pix:
            self.sts.screen.blit(
                self.pix, self.pix.get_rect(
                    center = (self.screen_x + self.pix_offset_x, self.screen_y + self.pix_offset_y)) )
            #if self.pix_rings:
            #    self.sts.screen.blit(
            #        self.pix_rings, self.pix_rings.get_rect(center = (self.screen_x, self.screen_y)) )
        else:
            pygame.draw.circle(self.sts.screen, self.color, (self.screen_x, \
                self.screen_y), self.screen_rad)
    
    def update_settings(self, new_settings):
        """ Updates settings class object """
        self.sts = new_settings

    def write_values(self):
        """ Print properties of celestial to debug log """
        text2write = []
        text2write.append(f"CURRENT VALUES FOR CELESTIAL BODY:  {self.name}")
        if self.homeworld == True:
            text2write.append("This is the homeworld.")
        else:
            text2write.append("This is not the homeworld.")
        text2write.append(f"The celestial boyd's density is {self.density} kg/m^3.")
        text2write.append(f"The celestial body's mass is {self.mass} kg.")
        text2write.append(f"The Earth's mass is {settings.EARTH_MASS} kg.")
        text2write.append(f"The celestial body's radius is {self.radius} km.")
        text2write.append(f"The celestial body's coordinates are ({self.x}, {self.y}).")
        text2write.append(f"The celestial body's velocity is ({self.vx}, {self.vy}).")
        text2write.append(f"The celestial body's speed is {self.get_speed()} km/s.")
        text2write.append(f"The celestial body's acceleration is ({self.ax}, {self.ay}).")         
        text2write.append(
            f"The celestial body's screen x and y coordinates are ({self.screen_x}, {self.screen_y}).")
        text2write.append(f"The celestial body's screen radius is {self.screen_rad}.")
        if self.pix and not isinstance(self.pix_path, list):
            text2write.append(f"The celestial is using a pix found at {self.pix_path}.")
        elif self.pix and isinstance(self.pix_path, list):
            text2write.append(f"The celestial is using frames found at {self.pix_dir}.")
            for path in self.pix_path:
                text2write.append(f"The celestial has a frame at {path}.")
            text2write.append(f"The celestial is currently using a frame at {self.pix_path[self.pix_frame]}.")
        else:
            text2write.append("The celestial is using a body circle.")
       
        self.sts.write_to_log(text2write)

    def get_accel(self, celestial):
        """ Calculate acceleration from other celestial body"""
        dist = ( self.get_dist(celestial.x, celestial.y) )**2 
        if dist:
            a_mag = settings.GRAV_CONST * celestial.mass / dist
            (x, y) = self.get_unit(celestial.x, celestial.y)
            x *= a_mag
            y *= a_mag
        else:
            (x, y) = (0, 0)
            if self.sts.debug:
                self.sts.write_to_log(
                    f"ERROR:  Distance from {self.name} to {celestial.name} calculated to be zero.")
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

    def accelerate(self, celestials, time_res):
        """ Change celestial body's velocity """
        self.set_accel(celestials)
        self.vx += self.ax * time_res
        self.vy += self.ay * time_res

    def check_hit(self, celestial):
        """  Checks to see if self object has hit given object """
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
        if self.mass >= self.sts.crit_mass:                       
            # add_celestial_explosion(self, _tanks)
            self.radius /= 2
            self.get_mass()
            self.set_screen_radius()
            if self.pix:
                # settings.random_pix_transform(self.pix)
                self.scale_pix_to_body_circle()
            if self.sts.debug:
                self.sts.write_to_log(f"{self.name} has shrunk itself...")
                self.write_values()
        
            celestials.append(Celestial(self.sts))
            celestials[-1].set_attr(
                (self.name + f'-{random.randint(0, 10000)}'), False, 
                    self.density, self.radius, self.color)
            celestials[-1].vx = self.vx
            celestials[-1].vy = self.vy
            celestials[-1].x = self.x
            celestials[-1].y = self.y
            if self.pix:
                celestials[-1].load_pix(self.pix_path)
                # settings.random_pix_transform(celestials[-1].pix)
            if self.sts.debug:
                self.sts.write_to_log(f"{celestials[-1].name} has been created by {self.name}...")
                celestials[-1].write_values()
           
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
                self.sts.write_to_log(f"New values for {self.name}:")
                self.write_values()
            
            if self.sts.debug:
                self.sts.write_to_log(f"nNew values for {celestials[-1].name}")
                celestials[-1].write_values()
        elif not self.homeworld:
            self.active = False
            if self.sts.debug:
                self.sts.write_to_log(f"{self.name} has marked itself for destruction...")

    def shatter(self, celestials, _tanks):
        """ Check for collisions between all celestials, break apart and bounce if so """
        for celestial in celestials[:]:
            # If the celestial isn't itself and if there is a hit...
            if celestial.name != self.name and self.check_hit(celestial):
                    # If the mass is larger than defined critical mass, it breaks in half instead of 
                    # being destoryed...
                    if self.mass > (celestial.mass * self.sts.crit_mass_ratio) and not celestial.homeworld:
                        # Add celestial explosion to tanks list                        
                        add_celestial_explosion(celestial, _tanks)
                        # bounce the two away from each other
                        self.bounce(celestial)
                        # break the celestial in half
                        break_celestial(celestial, celestials, celestial.get_unit(self.x, self.y))
                    # Else, if the other's mass is too small but isn't the homeworld... ....
                    elif (self.mass * self.sts.crit_mass_ratio) < celestial.mass and not self.homeworld:
                        # add explosion where self used to be
                        add_celestial_explosion(self, _tanks)
                        self.bounce(celestial)
                        self.break_self(celestials, self.get_unit(celestial.x,  celestial.y))
                    # fix overlap if any
                    self.fix_overlap(celestial)
                                                               
    def check_off_screen(self):
        """ Check to see if the object is too far off screen, and remove it if so. """
        
        # There is a buffer outside of the drawn screen that gives an object a chance to return
        if (self.screen_x + self.screen_rad) < (self.width - (self.width*(1 + settings.DEFAULT_VIRTUAL_SCREEN))):
            self.active = False
            if self.sts.debug:
                self.sts.write_to_log(f"{self.name} is being removed for being too far left off-screen...")
        elif (self.screen_x - self.screen_rad) > self.width*(1 + settings.DEFAULT_VIRTUAL_SCREEN):
            self.active = False
            if self.sts.debug:
                self.sts.write_to_log(f"{self.name} is being removed for being too far right off-screen...")
        elif (self.screen_y + self.screen_rad) < (self.height - (self.height*(1 + settings.DEFAULT_VIRTUAL_SCREEN))):
            self.active = False
            if self.sts.debug:
                self.sts.write_to_log(f"{self.name} is being removed for being too far up off-screen...")
        elif (self.screen_y + self.screen_rad) > self.height*(1 + settings.DEFAULT_VIRTUAL_SCREEN):
            self.active = False
            if self.sts.debug:
                self.sts.write_to_log(f"{self.name} is being removed for being too far down off-screen...")
   
    def move(self, celestials, time_res):
        """ Move object based on current velocity """
        self.accelerate(celestials, time_res)
        self.x += self.vx * self.sts.tres
        self.y += self.vy * self.sts.tres
        self.get_screenxy()
        self.check_off_screen()

    def get_collision_point(self, celestial):
        """  Get the point of collision between two circles.  """
        collide_x = ( (self.x * celestial.radius) + (celestial.x * self.radius) ) / (self.radius + celestial.radius)
        collide_y = ( (self.y * celestial.radius) + (celestial.y * self.radius) ) / (self.radius + celestial.radius)
        return (collide_x, collide_y)

    def displace(self, displacement):
        """ Displace self's (x, y) coordinates by given vector.  """
        [self.x, self.y] = numpy.add([self.x, self.y], displacement)
        self.get_screenxy()

    def load_pix(self, path_to_pix):
        """  Load a single sprite from given path.  """
        
        # error checking
        if isinstance(path_to_pix, str):
            self.pix_path = os.path.normpath(path_to_pix)
            load_success = os.path.exists(self.pix_path)
        else:
            load_success = False
            if self.sts.debug:
                self.sts.write_to_log(f"ERROR using load_pix() for {self.name}  Invalid path format (is it a string?)")
        if load_success:
            # load imaged at path to self's sprite variable.
            self.pix = pygame.image.load_extended(self.pix_path)
            # Get PNG ready
            self.pix.convert_alpha()
            self.transform_pix()
            # scale the picture to set screen radius
            if self.sts.debug:
                self.sts.write_to_log(f"{self.pix_path} loaded as pixie for {self.name}...")
        else:
            self.pix_path = False
            if self.sts.debug:
                self.sts.write_to_log(f"ERROR loading {self.pix_path} for {self.name}:  file doesn't exist!")
   
        return load_success

    def load_pix_to(self, path_to_pix):
        """  Load a single sprite from given path to a particular variable.  """
    
        # error checking
        if isinstance(path_to_pix, str):
            pix_path = os.path.normpath(path_to_pix)
            load_success = os.path.exists(pix_path)
        else:
            load_success = False
            return_pix = False
            if self.sts.debug:
                self.sts.write_to_log(f"ERROR using load_pix_to() for {self.name}  Invalid path format (is it a string?)")
        if load_success:
            # load imaged at path to self's sprite variable.
            return_pix = pygame.image.load_extended(pix_path)
            # Get PNG ready
            return_pix.convert_alpha()
            # scale the picture to set screen radius
            if self.sts.debug:
                self.sts.write_to_log(f"{pix_path} returned as pixie for {self.name}...")
        else:
            return_pix = False
            if self.sts.debug:
                self.sts.write_to_log(f"ERROR loading {pix_path} for {self.name} to destination:  file doesn't exist!")

        return return_pix

    # def load_rings(self, rings_path):
    #    rings_path = os.path.normpath(rings_path)
    #    load_success = os.path.exists(rings_path)
    #     if load_success:
    #        self.pix_rings = pygame.image.load_extended(rings_path)
    #        self.pix_rings.convert_alpha()
    #        if self.sts.debug:
    #            self.sts.write_to_log(f"{rings_path} loaded as rings pix for {self.name}...")
    #    elif self.sts.debug:
    #        self.sts.write_to_log(f"ERROR loading {rings_path} for {self.name}:  file doesn't exist!")
    #
    #    return load_success

    def scale_pix_to_body_circle(self):
        """  Scales loaded sprite image to set screen's radius """
        if self.pix:
            self.pix = pygame.transform.scale(
                self.pix, (int(2*self.screen_rad), int(2*self.screen_rad)) )
            # self.pix = pygame.transform.smoothscale(self.pix, (2*self.screen_rad, 2*self.screen_rad))
    
    # def scale_pix_rings(self):
    #     if self.pix_rings:
    #        self.pix_rings = pygame.transform.scale(self.pix_rings, (2.6*self.screen_rad, 2.6*self.screen_rad))

    def pick_homeworld_pix(self):
        """  Choose at random a sprite from homeworld sprite's directory for homeworld. """
        # choose a random directory in Homeworld's directory (i.e. forest, lava, etc.)
        self.pix_path = settings.choose_random_directory(settings.HOMEWORLDS_DIR)
        # choose a random image from that directory
        self.pix_path = settings.choose_random_file(self.pix_path)
        if self.pix_path:
            # load found sprite if any
            self.load_pix(self.pix_path)
            if self.sts.debug:
                self.sts.write_to_log(f"Image at {self.pix_path} chosen as homeworld pix for {self.name}'s...")
        elif self.sts.debug:
            self.sts.write_to_log(f"Can't find homeworld image ax {self.pix_path}!")
        
    def pick_moon_pix(self):
        """  Choose at random a sprite from the moon sprite's directory for a moon. """
        if not self.homeworld:
            self.pix_path = settings.choose_random_file(settings.MOONS_PATH)
            if self.pix_path:
                self.load_pix(self.pix_path)
            elif self.sts.debug:
                self.sts.write_to_log(f"ERROR loading moon pix from {self.pix_path} for {self.name}...")

    def pick_dwarf_pix(self):
        """  Choose at random a sprite from the dwarf planet's directory for an asteroid, etc. """
        if not self.homeworld:
            self.pix_path = settings.choose_random_file(settings.DWARVES_PATH)
            if self.pix_path:
                self.load_pix(self.pix_path)
            elif self.sts.debug:
                self.sts.write_to_log(f"ERROR loading dwarf pix from {self.pix_path} for {self.name}...")

    def fix_frames_path(self):
        """ Join and set directory path for OS for paths to frame sprites. """
        if isinstance(self.pix_path, list) and self.pix_dir:
            for frame_path in self.pix_path:
                frame_path = os.path.join(self.pix_dir, frame_path)
                frame_path = os.path.normpath(frame_path)
                if self.sts.debug:
                    print(f"\nAdding {frame_path} to {self.name}'s frame paths...")
                    self.sts.write_to_log(f"Adding {frame_path} to {self.name}'s frame paths...")
        elif self.sts.debug:
            self.sts.write_to_log(
                f"ERROR in Cosmos.fix_frames_path:  No list of pix frames defined for {self.name}.")

    def next_frame(self):
        """  Select active image from next sprite in list of frame sprites. """
        
        if isinstance(self.pix_frames, list) and not self.animation_finished:
            if self.pix_frame < ( len(self.pix_frames) - 1):
                self.pix_frame += 1
                self.load_frame()
                if self.pix_frame == ( len(self.pix_frames) - 1 ) and not self.animate_repeat:
                    self.animation_finished = True
            else:
                self.pix_frame = 0
                self.load_frame()
                
        # elif self.sts.debug:
        #     self.sts.write_to_log(
        #        f"ERROR in Cosmos.next_frame:  No list of pix frames defined for {self.name}.")
    
    def load_frame(self):
        """ Load indicated frame from frame sprite list and scale it. """
        if isinstance(self.pix_frames, list) and isinstance(self.pix_frame, int):
            if self.pix_frame > ( len(self.pix_frames) - 1):
                self.pix_frame = 0
            self.pix = self.pix_frames[self.pix_frame]
            self.transform_pix()
            self.animation_finished = False
        elif self.sts.debug:
            self.sts.write_to_log(
                f"ERROR in Cosmos.load_frame:  No list of pix frames defined for {self.name}, or invalid frame.")
    
    def load_frames(self):
        """ Load list of sprites from set directory into memory. """
        self.pix_frames = []
        self.pix_dir = os.path.normpath(self.pix_dir)
        if self.pix_dir and os.path.exists(self.pix_dir):
            self.pix_path = os.listdir(self.pix_dir)
        # self.fix_frames_path()
        else:
            if self.sts.debug:
                self.sts.write_to_log(f"ERROR:  Can't load frames from {self.pix_dir}, directory doesn't exist!")
            self.pix_frames = False
            self.pix_dir = False
        if isinstance(self.pix_path, list):
            for frame in self.pix_path:
                frame_file = os.path.join(self.pix_dir, frame)
                frame_file = os.path.normpath(frame_file)
                if os.path.exists(frame_file):
                    self.pix_frames.append(pygame.image.load_extended(frame_file))
                    self.pix_frames[-1].convert_alpha()
                    if self.sts.debug:
                        self.sts.write_to_log(f"Pix at {frame_file} loaded as frame for {self.name}...")
                elif self.sts.debug:
                    self.sts.write_to_log(f"ERROR for {self.name}:  {frame_file} not found!")
            self.animate = True
            self.pix_frame = 0
            self.load_frame()
        else:
            self.pix_frames = False
            if self.sts.debug:
                self.sts.write_to_log(f"ERROR:  No list of pix frames defined for {self.name}.")

    def load_frames_to(self, dir):
        """ Load list of sprites from given directory to a specific list """
        frames = []
        dir = os.path.normpath(dir)
        paths = False
        if os.path.exists(dir):
            paths = os.listdir(dir)
        elif self.sts.debug:
            self.sts.write_to_log(
                f"ERROR:  Invalid directory {dir} sent to cosomos.load_frames_to() for {self.name}")
        if isinstance(paths, list):
            for frame in paths:
                frame_file = os.path.join(dir, frame)
                frame_file = os.path.normpath(frame_file)
                if os.path.exists(frame_file):
                    frames.append(pygame.image.load_extended(frame_file))
                    frames[-1].convert_alpha()
                elif self.sts.debug:
                    self.sts.write_to_log(
                        f"ERROR:  File {frame_file} not found using cosmos.load_frames_to() for {self.name}.")
        else:
            frames = False
            if self.sts.debug:
                self.sts.write_to_log(
                    f"No files found in {dir} for {self.name} while using cosmos.load_frames_to().")
        return frames

    def set_frames(self, frames):
        """ Switch current set of frames to another given set. """
        if isinstance(frames, list):
            self.pix_frames = frames
            self.pix_frame = 0
            self.load_frame()

    def transform_pix(self):
        if self.pix_flip[0] or self.pix_flip[1]:
                self.flip_pix()
        self.scale_pix_to_body_circle()
        if self.pix_rotate:
            self.rotate_pix()

    def rotate_pix(self):
        """ Rotate active sprite by given radians. """
        # Convert radians to degrees
        deg_rot = self.pix_rotate * 180 / math.pi
        self.pix = pygame.transform.rotate(self.pix, deg_rot)

    def flip_pix(self):
        """ Flip active sprite over x- and/or y-axis. """
        self.pix = pygame.transform.flip(self.pix, self.pix_flip[0], self.pix_flip[1])

    def displace_pix(self, displace_mag, screen_xy):
        """ Displace pix or frames in a vector """

        # Displaces along a vector pointing from point screen_xy to self a 
        # magnitude of displace_mag pixels

        displace_vector = numpy.subtract(
            (self.screen_x, self.screen_y), (screen_xy[0], screen_xy[1]) )
        displace_vector = numpy.multiply(displace_mag, normalize(displace_vector) )
        self.pix_offset_x = int( displace_vector[0] )
        self.pix_offset_y = int( displace_vector[1] )
    
    def animation(self):
        if self.animate and isinstance(self.pix_frames, list) and not self.animation_finished:
            if ( time.time() - self.frame_timer) > self.frame_wait:
                self.next_frame()
                self.frame_timer = time.time()

# ********************************************************************************************************** 
# *************************** CANNONBALL!!! ****************************************************************
# **********************************************************************************************************

class Cannonball(Celestial):
    """ Class for projectile (or projectiles), child of Celestial """

    def __init__(self, sts, celestials):
        """ Initialize variables for projectile """
        super().__init__(sts)

        self.name = 'Cannonball'

        self.radius = 0.001             # 1 m meter radius
        self.screen_rad = settings.DEFAULT_BALL_SCREEN_RAD

        self.homeworld = False       # not the homeworld ;)
        self.explode_radius = settings.DEFAULT_EXPLODE_RADIUS
        self.color = settings.DEFAULT_BALL_COLOR
        self.flash_colors = settings.DEFAULT_FLASH_COLORS

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
        # Use to keep track of Cannonball objects of animated celestial explosions
        self.celestial_explosion = False

        # keep track of fuse, explosion timers
        self.fuse_start = 0
        self.fuse_length = settings.DEFAULT_FUSE_TIME
        self.explode_start = 0
        # To keep track of when to exploded cannonballs of destroyed tanks
        self.given_away_start = 0
        
        self.mass = settings.DEFAULT_CANNONBALL_MASS

        self.speed = 0
        self.vx = 0
        self.vy = 0

        # Keep track if explosion is stuck to a celestial to it travels with it
        self.stuck_to_celestial = False
        # Location of stuck explosion on celestial.
        self.pos_angle = 0

        # set by another class/function
        self.explode_energy = settings.DEFAULT_EXPLODE_ENERGY
        # self.explode_energy = 0
        self.explode_force_mag = self.explode_energy / self.explode_radius

        # holds fireball frames
        self.fireball_frames = False
                                  
    def update_celestials(self, celestials):
        """ update homewold values """
        self.celestials = celestials
        for body in celestials:
            if body.homeworld == True:
                self.homeworld = body
    
    def find_speed(self):
        """ Get speed of cannnonball """
        self.speed = math.sqrt(self.vx**2 + self.vy**2)
            
    def explode(self):
        """ Trigger explosion, reset flags and parameters accordingly. """
        # self.active = False
        self.armed = False
        self.exploding = True
        if "-fireball" in self.name.lower():
            self.animate_repeat = False
            self.frame_wait = 1/10
            self.radius = self.explode_radius
            self.set_screen_radius()
            if self.stuck_to_celestial:
                self.get_surface_pos()
                self.displace_pix(
                    0.9*self.screen_rad, (self.stuck_to_celestial.screen_x, \
                        self.stuck_to_celestial.screen_y) )
                self.pix_rotate = self.pos_angle - math.pi/2
                self.set_frames(self.fireball_frames["surface explode"])
            else:
                self.set_frames(self.fireball_frames["space explode"])
        else:       
            self.animate = False
            self.pix = False
            # keep track of explosion time.
            self.explode_start = time.time()
                
        # keep track of explosion color switching time or animation time
        self.frame_timer = time.time()

        if self.sts.sound_on:
            self.sts.sounds["cannonball-explode"].play()
    
    def expand(self):
        """ Keep track of exploding cannonball's explosion radius. """
        if self.exploding:
            # As explosion timer progresses, 
            # actual radius approaches that of desired explosion radius
            self.radius = self.explode_radius*( 
                (time.time() - self.explode_start)/settings.DEFAULT_EXPLODE_TIME )
            # Reset display radius on screen
            self.set_screen_radius()
    
    # This function is not currently being used
    # def set_explode_force_mag(self, time):
    #    """ Explosion Force changes with time """
    #    self.explode_force_mag = self.explode_energy / time

    def get_surface_pos(self):
        """ set launch point of cannonball on homeworld based on position angle (pos_angle) """
        if self.stuck_to_celestial:
            self.x = self.stuck_to_celestial.radius * math.cos(self.pos_angle) \
                + self.stuck_to_celestial.x
            self.y = self.stuck_to_celestial.radius * math.sin(self.pos_angle) \
                + self.stuck_to_celestial.y
            super().get_screenxy()

    def stick_to_celestial(self, celestial):
        """ Set parameters for cannonball stuck to a celestial """
        if not self.stuck_to_celestial:
            self.stuck_to_celestial = celestial
            (stuck_x, stuck_y) = numpy.subtract(
                [self.x, self.y], [self.stuck_to_celestial.x, self.stuck_to_celestial.y])
            self.pos_angle = math.atan2(stuck_y, stuck_x)
    
    def check_impact(self, _tanks):
        """ Check to see if cannonball is blowing something up. """
        hit = False
       
        # Check what happens to each celestial
        for celestial in self.celestials:
            if self.check_hit(celestial):
                hit = True
                if self.armed:
                    
                    if celestial.homeworld \
                    or ("-fireball" in self.name.lower() and celestial.radius >= settings.LUNA_RADIUS):
                        self.stick_to_celestial(celestial)
                    
                    self.explode()
                elif self.exploding:
                    if celestial.homeworld \
                    or ("-fireball" in self.name.lower() and celestial.mass >= settings.LUNA_MASS) \
                    or self.celestial_explosion:
                        self.stick_to_celestial(celestial)
                    
                    elif not self.celestial_explosion and "-fireball" not in self.name.lower():
                        # Nudge hit celestial based on magnitude of explosion force
                        # (ax, ay) = super().get_unit(celestial.x, celestial.y)
                        # ax *= self.explode_force_mag
                        # ay *= self.explode_force_mag
                        # celestial.vx += ax * self.sts.tres
                        # celestial.vy += ay * self.sts.tres
                        # If the celestial is too small...
                        if celestial.mass < self.sts.crit_explode_mass:
                            # Blow it up!
                            add_celestial_explosion(celestial, _tanks)
                            celestial.break_self(
                                self.celestials, celestial.get_unit(self.x, self.y))
                            # Free stuck explosion from destroyed celestial
                            # self.stuck_to_celestial = False
                            # self.exploding = False
                            # self.active = False
                    # elif not celestial.homeworld:
                        # Mark destroyed celestial for removal
                        # (If not homeworld, of course...)
                        # self.stuck_to_celestial = False
                else:
                    self.active = False
                
        # Check to see if tanks are hit and destroy it if so
        for tank in _tanks:
            for pixie in tank.effect_pixies:
                if "wolf" in pixie.name.lower() \
                and self.exploding \
                and super().check_hit(pixie):
                    pixie.name = "spirit-banish"
                    pixie.screen_displacement = tank.screen_displacement
                    pixie.set_frames(tank.Spell_wolf_frames["summon"])
                    pixie.fix_snail_pix()
                    pixie.animate = True
                    pixie.animate_repeat = False
                    pixie.frame_wait = 1/10
                    tank.spell_active = False
                    tank.remove_effect_pixie("scroll")
                    tank.spell_cooldown_timer = time.time()
            if self.exploding and super().check_hit(tank) and not tank.invulnerable:
                hit = True
                tank.dying = True
                if self.sts.debug:
                    self.sts.write_to_log(f"{tank.name} has been hit by {self.name}!")
                    
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
        if self.celestial_explosion:
            extra_cannonball_text.append("This cannonball is a celestial explosion.")
        self.sts.write_to_log(extra_cannonball_text)

    def flash(self):
        """ Change cannonball color while exploding """
        if ( time.time() - self.frame_timer ) > self.frame_wait:
            self.color = random.choice(self.flash_colors)
            self.frame_timer = time.time()