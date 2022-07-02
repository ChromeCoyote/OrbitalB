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

def add_celestial_explosion(_celestial, _tanks):
    _tanks[0].balls.append(Cannonball(_tanks[0].sts, _tanks[0].celestials))
    _tanks[0].balls[-1].celestial_explosion = True
    _tanks[0].balls[-1].name = f"{_celestial.name}'s Explosion-{random.randint(1,10000)}"
    _tanks[0].balls[-1].vx = _celestial.vx
    _tanks[0].balls[-1].vy = _celestial.vy
    _tanks[0].balls[-1].ax = _celestial.ax
    _tanks[0].balls[-1].ay = _celestial.ay
    _tanks[0].balls[-1].x = _celestial.x
    _tanks[0].balls[-1].y = _celestial.y
    _tanks[0].balls[-1].get_screenxy()
    _tanks[0].balls[-1].active = True
    _tanks[0].balls[-1].exploding = True
    _tanks[0].balls[-1].given_away = True
    _tanks[0].balls[-1].radius = _celestial.radius
    _tanks[0].balls[-1].set_screen_radius()
    _tanks[0].balls[-1].explode_radius = _celestial.radius
    _tanks[0].balls[-1].pix_dir = settings.choose_random_directory(settings.EXPLOSIONS_PATH)
    _tanks[0].balls[-1].pix_path = os.listdir(_tanks[0].balls[-1].pix_dir)

    if _tanks[0].balls[-1].pix_path:
        if _tanks[0].sts.debug:
            _tanks[0].sts.write_to_log(f"Files found for frames for {_tanks[0].balls[-1].name}...")
        _tanks[0].balls[-1].load_frames()
    else:
        _tanks[0].balls[-1].pix_frames = False
        if _tanks[0].sts.debug:
            _tanks[0].sts.write_to_log(
                    f"ERROR:  Explosion pix files not found in {_tanks[0].balls[-1].pix_dir} for {_tanks[0].balls[-1].name}!")

    _tanks[0].balls[-1].explode_start = time.time()
    _tanks[0].balls[-1].frame_timer = time.time()

    if _tanks[0].sts.debug:
        _tanks[0].balls[-1].write_ball_values()

def break_celestial(broke_body, celestials, _tanks, break_plane):
    if broke_body.mass >= broke_body.sts.crit_mass:
        # add_celestial_explosion(broke_body, _tanks)
        broke_body.radius /= 2
        broke_body.get_mass()
        broke_body.set_screen_radius()
        if broke_body.pix:
            # settings.random_pix_transform(broke_body.pix)
            broke_body.scale_pix_to_body_circle()
        if broke_body.sts.debug:
            broke_body.sts.write_to_log(f"{broke_body.name} has been shrunk by another...")
            broke_body.write_values()

        celestials.append(Celestial(broke_body.sts))
        celestials[-1].set_attr(
            (broke_body.name + f'-{random.randint(0, 10000)}'), False, 
                broke_body.density, broke_body.radius, broke_body.color)
        celestials[-1].vx = broke_body.vx
        celestials[-1].vy = broke_body.vy
        celestials[-1].x = broke_body.x
        celestials[-1].y = broke_body.y
        if broke_body.pix:
            celestials[-1].load_pix(broke_body.pix_path)
            # settings.random_pix_transform(broke_body.pix)
            celestials[-1].scale_pix_to_body_circle()
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
    for celestial in celestials[:]:
        if not celestial.active and not celestial.homeworld:
            if celestials[0].sts.debug:
                celestials[0].sts.write_to_log(f"\n{celestial.name} being destroyed...")    
            celestials.remove(celestial)
            if celestials[0].sts.debug:
                celestials[0].sts.write_to_log(f"Successfully destroyed celestial!")    

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
        self.pix = False
        self.pix_path = False
        self.pix_dir = False
        self.pix_frames = False
        self.pix_frame = 0      # current frame in animation in pix_frames
        self.frame_wait = 1 / self.sts.fps  # default time to wait to change frames
        self.frame_timer = 0
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

    def get_screenxy(self):
        """Get x and y coordinates on screen"""
        (self.screen_x, self.screen_y) = self.set_screenxy(self.x, self.y)
        return (self.screen_x, self.screen_y)

    def place_on_screen(self, X, Y):
        """ Set object's game (x,y) coordinates to coordinates on screen """    
        
        self.x = int((X - self.width/2)*(1/self.sts.screen_dist_scale))
        self.y = int((self.height/2 - Y)*(1/self.sts.screen_dist_scale))

    def draw_bodycircle(self):
        """ Draws a simple circle to represent world """
        if self.pix:
            self.sts.screen.blit(
                self.pix, self.pix.get_rect(center = (self.screen_x, self.screen_y)) )
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
        """Print properties of world"""
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

    def break_self(self, celestials, _tanks, break_plane):
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
                celestials[-1].scale_pix_to_body_circle()
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
        """ Check for collision, break apart and bounce if so """
        for celestial in celestials[:]:
            if celestial.name != self.name and self.check_hit(celestial):
                    if self.mass > (celestial.mass * self.sts.crit_mass_ratio) and not celestial.homeworld:
                        add_celestial_explosion(celestial, _tanks)
                        self.bounce(celestial)
                        break_celestial(celestial, celestials, _tanks, celestial.get_unit(self.x, self.y))
                    elif (self.mass * self.sts.crit_mass_ratio) < celestial.mass and not self.homeworld:
                        add_celestial_explosion(self, _tanks)
                        self.bounce(celestial)
                        self.break_self(celestials, _tanks, self.get_unit(celestial.x,  celestial.y))
                    # fix overlap if any
                    self.fix_overlap(celestial)
                                                               
    def check_off_screen(self):
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

    def load_pix(self, path_to_pix):
        if isinstance(path_to_pix, str):
            self.pix_path = os.path.normpath(path_to_pix)
            load_success = os.path.exists(self.pix_path)
        else:
            load_success = False
            if self.sts.debug:
                self.sts.write_to_log(f"ERROR using load_pix() for {self.name}  Invalid path format (is it a string?)")
        if load_success:
            self.pix = pygame.image.load_extended(self.pix_path)
            self.pix.convert_alpha()
            self.scale_pix_to_body_circle()
            if self.sts.debug:
                self.sts.write_to_log(f"{self.pix_path} loaded as pixie for {self.name} and scaled to body circle...")
        else:
            self.pix_path = False
            if self.sts.debug:
                self.sts.write_to_log(f"ERROR loading {self.pix_path} for {self.name}:  file doesn't exist!")
   
        return load_success

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
        if self.pix:
            self.pix = pygame.transform.scale(self.pix, (2*self.screen_rad, 2*self.screen_rad))
            # self.pix = pygame.transform.smoothscale(self.pix, (2*self.screen_rad, 2*self.screen_rad))
    
    # def scale_pix_rings(self):
    #     if self.pix_rings:
    #        self.pix_rings = pygame.transform.scale(self.pix_rings, (2.6*self.screen_rad, 2.6*self.screen_rad))

    def pick_homeworld_pix(self):
        self.pix_path = settings.choose_random_directory(settings.HOMEWORLDS_DIR)
        self.pix_path = settings.choose_random_file(self.pix_path)
        if self.pix_path:
            self.load_pix(self.pix_path)
            if self.sts.debug:
                self.sts.write_to_log(f"Image at {self.pix_path} chosen as homeworld pix for {self.name}'s...")
        elif self.sts.debug:
            self.sts.write_to_log(f"Can't find homeworld image ax {self.pix_path}!")
        
    def pick_moon_pix(self):
        if not self.homeworld:
            self.pix_path = settings.choose_random_file(settings.MOONS_PATH)
            if self.pix_path:
                self.load_pix(self.pix_path)
            elif self.sts.debug:
                self.sts.write_to_log(f"ERROR loading moon pix from {self.pix_path} for {self.name}...")

    def pick_dwarf_pix(self):
        if not self.homeworld:
            self.pix_path = settings.choose_random_file(settings.DWARVES_PATH)
            if self.pix_path:
                self.load_pix(self.pix_path)
            elif self.sts.debug:
                self.sts.write_to_log(f"ERROR loading dwarf pix from {self.pix_path} for {self.name}...")

    def fix_frames_path(self):
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
        if isinstance(self.pix_frames, list):
            self.pix = self.pix_frames[self.pix_frame]
            self.scale_pix_to_body_circle()
            if self.pix_frame < ( len(self.pix_frames) - 1 ):
                self.pix_frame += 1
            else:
                self.pix_frame = 0
        elif self.sts.debug:
            self.sts.write_to_log(
                f"ERROR in Cosmos.next_frame:  No list of pix frames defined for {self.name}.")
    
    def load_frame(self, frame):
        if isinstance(self.pix_frames, list) and isinstance(frame, int):
            self.pix_frame = frame
            self.scale_pix_to_body_circle()
            if self.pix_frame > ( len(self.pix_frames) - 1):
                self.pix_frame = 0
            self.pix = self.pix_frames[self.pix_frame]
        elif self.sts.debug:
            self.sts.write_to_log(
                f"ERROR in Cosmos.load_frame:  No list of pix frames defined for {self.name}, or invalid frame.")
    
    def load_frames(self):
        self.pix_frames = []
        # self.fix_frames_path()
        if isinstance(self.pix_path, list):
            for frame in self.pix_path:
                frame_file = os.path.join(self.pix_dir, frame)
                frame_file = os.path.normpath(frame_file)
                if os.path.exists(frame_file):
                    self.pix_frames.append(pygame.image.load_extended(frame_file))
                    if self.sts.debug:
                        self.sts.write_to_log(f"Pix at {frame_file} loaded as frame for {self.name}...")
                elif self.sts.debug:
                    self.sts.write_to_log(f"ERROR for {self.name}:  {frame_file} not found!")
            self.load_frame(0)
        elif self.sts.debug:
            self.sts.write_to_log(f"ERROR:  No list of pix frames defined for {self.name}.")

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
        self.explode_start = 0
        self.given_away_start = 0
        
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
    
    def check_impact(self, _tanks):
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
                        if not self.celestial_explosion:
                            (ax, ay) = super().get_unit(celestial.x, celestial.y)
                            ax *= self.explode_force_mag
                            ay *= self.explode_force_mag
                            celestial.vx += ax * self.sts.tres
                            celestial.vy += ay * self.sts.tres
                            if celestial.mass < self.sts.crit_explode_mass:
                                add_celestial_explosion(celestial, _tanks)
                                celestial.break_self(self.celestials, _tanks, celestial.get_unit(self.x, self.y))
                                self.stuck_to_celestial = False
                                # self.exploding = False
                                # self.active = False
                        elif not celestial.homeworld:
                            self.stuck_to_celestial = False
                else:
                    self.active = False
                
        for tank in _tanks:
            if self.exploding and super().check_hit(tank):
                hit = True
                tank.active = False
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