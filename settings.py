from pickle import TRUE
from sre_compile import isstring
import pygame
import random
import math
import numpy
import datetime
import os

# real world variables
EARTH_RADIUS = 6_371    # in kilometers
EARTH_MASS = 5.972e24   # in kilograms
EARTH_DENSITY = 5515    # in kilograms per meter cubed

LUNA_RADIUS = 1_737.1   # in kilometers
LUNA_MASS = 7.34767309e22   # in kilograms
LUNA_DENSITY = 3340     # in kilograms per meter cubed
LUNA_ORBIT_RAD = 385_000   # in km

CERES_RADIUS = 470      # in kilometers
CERES_DENSITY = 2612

# C/2014 UN_271 Bernardinelli-Bernstein
COMET_RADIUS = 69      # in kilometers
COMET_MASS = 450e15     # in kg
COMET_DENSITY = 917   # that of ice, just an estimate

GRAV_CONST = 6.674e-20  # universal gravitational constant, cubic km

DEFAULT_STAR_DENSITY = 0.001      #10% of screen filled by default
# DEFAULT_STAR_COLOR = (255,255,255)  # white stars

# screen & game variables
DEFAULT_WIDTH = 0       # should give current screen resolution
DEFAULT_HEIGHT = 0
DEFAULT_FPS = 60        # time resolution, 1/FPS seconds
DEFAULT_TSCALE = 1      # animation time scaling, set to realtime
DEFAULT_BGCOLOR = (0,0,0)   # black background

DEFAULT_TRES = 1 / DEFAULT_FPS  # Default time resoution for simulation

EARTH_RAD_SCALE = 0.1   # A body with Earth's radius will take up this
                        # amount of the screen

# amount of energy lost when there is a collision
DEFAULT_ENERGY_LOSS = 1
DEFAULT_CRIT_MASS = LUNA_MASS / 4      # critical radius under which celestials die
DEFAULT_CRIT_EXPLODE_MASS = LUNA_MASS        # cannonballs blow up the moon!
# mass of collidiing object has to be this many times more to cause shatter
DEFAULT_CRIT_MASS_RATIO = 1        

DEFAULT_TANK_SCREENRAD = 3      # default tank screen radius
DEFAULT_TANK_COLOR = (0,255,0)  # default tank color, lime green?
DEFAULT_ENEMY_TANK_COLOR = (255, 0, 255)    # enemy tank color, magenta
DEFAULT_ESCAPE_FRAC = 0.5       # default cannonball speed as fraction

DEFAULT_RADIAN_STEP = ((2*math.pi) / 360)
DEFAULT_SPEED_DIV = 100        
DEFAULT_POSITION_ANGLE = math.pi / 2     # initial posistion on surface in radians
DEFAULT_FIRING_ANGLE = 0       # initial firing angle in radians

DEFAULT_FUSE_TIME = 1               # fuse lasts for 1 second, after which cannonball becomes armed
DEFAULT_EXPLODE_TIME = 2               # cannonballs explode for this many seconds
DEFAULT_FLASH_CHANCE = 0.8            # cannonballs flash new color every tenth of a secondn when exploding
DEFAULT_CANNONBALL_MASS = 1000      # default cannonball mass

# don't select a color every explode tick 
SKIP_COLOR = 100

DEFAULT_BALL_COLOR = (255, 255, 255)    # white
DEFAULT_ARMED_COLOR = (255, 69, 0)        # orange
DEFAULT_BALL_SCREEN_RAD = 2     # small yet visible
# scaling for changes to velocity per key press
DEFAULT_RADIAN_STEP = ((2*math.pi) / 360)
DEFAULT_HOT_ARROW_COLOR = (255, 0, 0)       # default arrow colors
DEFAULT_WARM_ARROW_COLOR = (255, 255, 0)
DEFAULT_COLD_ARROW_COLOR = (0, 255, 255)
HOT_THRESHOLD = 0.9                         # thresholds for arrows
COLD_THRESHOLD = 0.3

# Energy release by Czar Bomba in kg*km^2*s^(-2)
CZAR_BOMBA_ENERGY = 2e11

# frequency of asteroid creation...
DEFAULT_ASTEROID_CHANCE = 1/120

# AI PARAMETERS
SIMPLE_SPEED_GUESS_LOWER = 0.8
SIMPLE_SPEED_GUESS_HIGHER = 0.95

# Cannonballs have as much energy as 1 million Czar Bombs
# DEFAULT_EXPLODE_ENERGY = CZAR_BOMBA_ENERGY / 2e12
DEFAULT_EXPLODE_ENERGY = 0

DEFAULT_EXPLODE_RADIUS = LUNA_RADIUS / 2 # explosion is 1/4 radius of Moon!

DEFAULT_BODY_COLOR = (0, 94, 184)       # ocean color
DEFAULT_LUNA_COLOR = (254, 252, 215)    # Moon Glow
# DEFAULT LUNA_COLOR = (201, 201, 201)   # gray
DEFAULT_COMET_COLOR = (200, 233, 233)   # ice blue

DEFAULT_FONT_SIZE = 24
DEFAULT_FONT_COLOR = (255, 255, 255)    # white

CHAMBER_BALL = pygame.K_RETURN
FIRE_BALL = pygame.K_SPACE
INCREASE_ANGLE = pygame.K_UP
DECREASE_ANGLE = pygame.K_DOWN
INCREASE_SPEED = pygame.K_KP_PLUS
DECREASE_SPEED = pygame.K_KP_MINUS
MOVE_TANK_CW = pygame.K_RIGHT
MOVE_TANK_CCW = pygame.K_LEFT
DETONATE_BALL = pygame.K_DELETE
EJECT_BALL = pygame.K_BACKSLASH
EXTI_MENU = pygame.K_ESCAPE

DEFAULT_AI_TOLERANCE = 1
# How often enemy tank will choose to fire rather than move
DEFAULT_AI_FIRE_WEIGHT = 0.8
# How long in seconds that AI tank will wait to make an action to slow it down
DEFAULT_AI_WAIT_TIME = 0

# Game will keep track of objects that are this far out of screen,
# i.e. if value is 0.5, objects will be keep in memory as long as they
# are within 50% the total screen height or width outside the actual screen
DEFAULT_VIRTUAL_SCREEN = 0.5

# Chance for one of the 8 zones to have a faraway object
DEFAULT_CHANCE_FOR_FARAWAY_OBJECT = 1/4
NUM_ZONES = 8

# Number of faraway object categories
NUM_FARAWAY_OBJECT_CAT = 9

NUM_HOMEWORLD_CAT = 10
NUM_DESERT = 8
NUM_FOREST = 14
NUM_ICE = 4
NUM_LAVA = 12
NUM_OCEAN = 8
NUM_ROCKY = 12
NUM_TECH = 12
NUM_TERRAN = 16
NUM_TUNDRA = 8

def rand_clr():
    """ Gets color of star based on galactic distribution """
    clr = (255, 255, 255)
    rando = random.random()
    if rando <= 0.1:         # class B star
        clr = (170, 191, 255)
    elif rando <= 0.25:        # class A star
        clr = (202, 215, 255)
    elif rando <= 0.45:         # class F star
        clr = (248, 247, 255)
    elif rando <= 0.65:        # class G star
        clr = (255, 244, 234)
    elif rando <= 0.8:        # class K star
        clr = (255, 210, 161)
    elif rando <= 0.9:        # class M star
        clr = (255, 204, 111)
    else:                       # class O star
        clr = (155, 176, 255)

    return clr

def choose_random_file(path):
    random_file = False
    old_path = path
    path = os.path.normpath(path)
    if os.path.exists(path):
        random_file = random.choice(os.listdir(path))
        random_file = os.path.normpath(old_path + '/' + random_file)

    return random_file

class Settings:
    """Stores settings for game"""

    def __init__(self, width = DEFAULT_WIDTH, height = DEFAULT_HEIGHT):
        """Initialize the game's settings."""
        pygame.init()       # inialize pygame modules

        self.debug = True   # debugging on for now...

         # Stuff for game log
        self.now = datetime.datetime.now()
        self.log_filename = self.now.strftime("%Y-%m-%d-%H%M-%S_OB_game.log") 
        self.log_text = []

        #Screen settings
        self.screen_width = width
        self.screen_height = height
        self.fps = DEFAULT_FPS
        self.rad_scale = EARTH_RAD_SCALE
        self.tres = DEFAULT_TRES    # time resolution
        self.time_scale = DEFAULT_TSCALE
        self.bgcolor = DEFAULT_BGCOLOR
        # self.starcolor = DEFAULT_STAR_COLOR

        self.stardensity = DEFAULT_STAR_DENSITY
        self.energy_loss = DEFAULT_ENERGY_LOSS
        self.crit_mass = DEFAULT_CRIT_MASS
        self.crit_mass_ratio = DEFAULT_CRIT_MASS_RATIO
        self.crit_explode_mass = DEFAULT_CRIT_EXPLODE_MASS*1.01

        self.meteor_shower = False
        self.asteroid_chance = DEFAULT_ASTEROID_CHANCE
        
        # declaration of Surface object
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height) )
        # get actual window size
        (self.act_w, self.act_h) = pygame.display.get_window_size()

        self.starfield_clr = []     # inialize starfield color array
        self.starfield_xy = []      # inialize starfield coordinates
        self.faraway_pixies = []     # list of picture objects for background
        self.pix_xy = []            # list of xy cooridinates for background objects

        self.set_starfield()
       
        self.screen_dist_scale = self.act_h * self.rad_scale / \
            EARTH_RADIUS

    def set_fps(self, fps):
        """ Set FPS """
        self.fps = fps
        
    def set_time_scale(self, time_scale):
        """ Set time scale """
        self.time_scale = time_scale

    def set_scales(self, rad_scale, time_scale, tres):
        """ Set scaling relative to Earth's radius """
        self.rad_scale = rad_scale
        self.time_scale = time_scale
        self.tres = tres
        self.screen_dist_scale = self.act_h * rad_scale / EARTH_RADIUS
    
    def set_screensize(self, width, height):
        """ Set screen size and reset window """
        self.screen_width = width
        self.screen_height = height
        pygame.display.quit()       # close current display
        # reset current screen (Surface)
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height))
        # get actual window size
        (self.act_w, self.act_h) = pygame.display.get_window_size()
        self.set_starfield()
        self.screen_dist_scale = self.act_h * self.rad_scale / EARTH_RADIUS

    def set_bgcolor(self, red, green, blue):
        """ Set background color """
        self.bgcolor = (red, green, blue)

    def set_stardensity(self, density):
        """ Set density of starfield.  0.1 is 10% of sky """
        self.stardensity = density

    def fill_background(self):
        """ fill background with background color """
        self.screen.fill(self.bgcolor)

    def pick_spot_in_zone(self, zone):
        """ Picks a spot in one of the eight background zones """        
        if zone == 1:
            min_x = 0
            min_y = 0
            max_x = int((1/6)*self.act_w)
            max_y = int((1/6)*self.act_h)
            mid_x = int((max_x + min_x) / 2)
            mid_y = int((max_y + min_y) / 2)
            X = int( numpy.random.normal(mid_x, (1/20)*self.act_w) )
            Y = int( numpy.random.normal(mid_y, (1/20)*self.act_h) )
            if X < min_x:
                X = min_x
            elif X > max_x:
                X = max_x
            elif Y < min_y:
                Y = min_y
            elif Y > max_y:
                Y = max_y
        elif zone == 2:
            min_x = int((1/6)*self.act_w)
            min_y = 0
            max_x = int((5/6)*self.act_w)
            max_y = int((1/6)*self.act_h)
            mid_x = int((max_x + min_x) / 2)
            mid_y = int((max_y + min_y) / 2)
            X = int( numpy.random.normal(mid_x, (1/6*self.act_w)) )
            Y = int( numpy.random.normal(mid_y, (1/20)*self.act_h) )
            if X < min_x:
                X = min_x
            elif X > max_x:
                X = max_x
            elif Y < min_y:
                Y = min_y
            elif Y > max_y:
                Y = max_y
        elif zone == 3:
            min_x = int((5/6)*self.act_w)
            min_y = 0
            max_x = int(self.act_w)
            max_y = int((1/6)*self.act_h)
            mid_x = int((max_x + min_x) / 2)
            mid_y = int((max_y + min_y) / 2)
            X = int(numpy.random.normal(mid_x, (1/20)*self.act_h))
            Y = int(numpy.random.normal(mid_y, (1/20)*self.act_h))
            if X < min_x:
                X = min_x
            elif X > max_x:
                X = max_x
            elif Y < min_y:
                Y = min_y
            elif Y > max_y:
                Y = max_y
        elif zone == 4:
            min_x = int((5/6)*self.act_w)
            min_y = int((1/6)*self.act_h)
            max_x = int(self.act_w)
            max_y = int((5/6)*self.act_h)
            mid_x = int((max_x + min_x) / 2)
            mid_y = int((max_y + min_y) / 2)
            X = int(numpy.random.normal(mid_x, (1/20)*self.act_h))
            Y = int(numpy.random.normal(mid_y, (1/6)*self.act_h))
            if X < min_x:
                X = min_x
            elif X > max_x:
                X = max_x
            elif Y < min_y:
                Y = min_y
            elif Y > max_y:
                Y = max_y
        elif zone == 5:
            min_x = int((5/6)*self.act_w)
            min_y = int((5/6)*self.act_h)
            max_x = int(self.act_w)
            max_y = int(self.act_h)
            mid_x = int((max_x + min_x) / 2)
            mid_y = int((max_y + min_y) / 2)
            X = int(numpy.random.normal(mid_x, (1/20)*self.act_h))
            Y = int(numpy.random.normal(mid_y, (1/20)*self.act_h))
            if X < min_x:
                X = min_x
            elif X > max_x:
                X = max_x
            elif Y < min_y:
                Y = min_y
            elif Y > max_y:
                Y = max_y
        elif zone == 6:
            min_x = int((1/6)*self.act_w)
            min_y = int((5/6)*self.act_h)
            max_x = int((5/6)*self.act_w)
            max_y = int(self.act_h)
            mid_x = int((max_x + min_x) / 2)
            mid_y = int((max_y + min_y) / 2)
            X = int( numpy.random.normal(mid_x, (1/6*self.act_w)) )
            Y = int( numpy.random.normal(mid_y, (1/20)*self.act_h) )
            if X < min_x:
                X = min_x
            elif X > max_x:
                X = max_x
            elif Y < min_y:
                Y = min_y
            elif Y > max_y:
                Y = max_y
        elif zone == 7:
            min_x = 0
            min_y = int((5/6)*self.act_h)
            max_x = int((1/6)*self.act_w)
            max_y = int(self.act_h)
            mid_x = int((max_x + min_x) / 2)
            mid_y = int((max_y + min_y) / 2)
            X = int( numpy.random.normal(mid_x, (1/20)*self.act_w) )
            Y = int( numpy.random.normal(mid_y, (1/20)*self.act_h) )
            if X < min_x:
                X = min_x
            elif X > max_x:
                X = max_x
            elif Y < min_y:
                Y = min_y
            elif Y > max_y:
                Y = max_y
        elif zone == 8:
            min_x = 0
            min_y = int((1/6)*self.act_h)
            max_x = int((1/6)*self.act_w)
            max_y = int((5/6)*self.act_h)
            mid_x = int((max_x + min_x) / 2)
            mid_y = int((max_y + min_y) / 2)
            X = int(numpy.random.normal(mid_x, (1/20)*self.act_h))
            Y = int(numpy.random.normal(mid_y, (1/6)*self.act_h))
            if X < min_x:
                X = min_x
            elif X > max_x:
                X = max_x
            elif Y < min_y:
                Y = min_y
            elif Y > max_y:
                Y = max_y
        else:
            X = 0
            Y = 0
            if self.debug:
                self.write_to_log("ERROR:  Invalid zone ID passed to Settings.pick_spot_in_zone()")         

        if self.debug:
            log_text = []
            log_text.append(f"Screen coordinates ({X}, {Y}) choosen in zone #{zone}.")
            log_text.append(f"Screen dimensions are {self.act_w} wide by {self.act_h} high.")
            log_text.append(f"Minimum (x, y) are ({min_x}, {min_y}).")
            log_text.append(f"Maximum (x, y) are ({max_x}, {max_y}).")
            log_text.append(f"Mid (x, y) are ({mid_x}, {mid_y}).")
            self.write_to_log(log_text)

        return (X, Y)

    def pull_faraway_pix(self, pix_name):
        
        pix_path = False
        if isinstance(pix_name, str):
            if pix_name.lower() == "asteroid":
                pix_path = choose_random_file("Pix/Faraway_Objects/Asteroids")
                if not pix_path and self.debug:
                    self.write_to_log(f"ERROR:  Can't choose asteroid pix!")
            elif pix_name.lower() == "black_hole":
                pix_path = choose_random_file("Pix/Faraway_Objects/Black_Holes")
                if not pix_path and self.debug:
                    self.write_to_log(f"ERROR:  Can't choose black hole pix!")
            elif pix_name.lower() == "comet":
                pix_path = choose_random_file("Pix/Faraway_Objects/Comets")
                if not pix_path and self.debug:
                    self.write_to_log(f"ERROR:  Can't choose comet pix!")
            elif pix_name.lower() == "galaxy":
                pix_path = choose_random_file("Pix/Faraway_Objects/Galaxies")
                if not pix_path and self.debug:
                    self.write_to_log(f"ERROR:  Can't choose galaxy pix!")
            elif pix_name.lower() == "gas_giant":
                pix_path = choose_random_file("Pix/Faraway_Objects/Gas_Giants")
                if not pix_path and self.debug:
                    self.write_to_log(f"ERROR:  Can't choose gas giant pix!")
            elif pix_name.lower() == "nebula":
                pix_path = choose_random_file("Pix/Faraway_Objects/Nebulae")
                if not pix_path and self.debug:
                    self.write_to_log(f"ERROR:  Can't choose nebula pix!")
            elif pix_name.lower() == "quasar":
                pix_path = choose_random_file("Pix/Faraway_Objects/Quasars")
                if not pix_path and self.debug:
                    self.write_to_log(f"ERROR:  Can't choose quasar pix!")
            elif pix_name.lower() == "sun":
                pix_path = choose_random_file("Pix/Faraway_Objects/Suns")
                if not pix_path and self.debug:
                    self.write_to_log(f"ERROR:  Can't choose sun pix!")
            elif pix_name.lower() == "moon":
                pix_path = choose_random_file("Pix/Faraway_Objects/Moons")
                if not pix_path and self.debug:
                    self.write_to_log(f"ERROR:  Can't choose moon pix!")
            else:
                if self.debug:
                    self.write_to_log(f"ERROR:  Pix name {pix_name} not a valid choice.")
        else:
            if self.debug:
                self.write_to_log("ERROR:  Pix name has to be a string for Settings.pull_faraway_pix()")
        
        if pix_path:
            self.faraway_pixies.append(pygame.image.load_extended(pix_path))
            self.faraway_pixies[-1].convert_alpha()
            if self.debug:
                self.write_to_log(f"Image at {pix_path} choosen for background...")

        return pix_path

    def pick_faraway_object(self, zone):
        dice_roll = random.randint(1, NUM_FARAWAY_OBJECT_CAT)
        if dice_roll == 1:
            if self.pull_faraway_pix("asteroid"):
                self.pix_xy.append(self.pick_spot_in_zone(zone))
            elif self.debug:
                self.write_to_log("ERROR pulling asteroid at random in Settings.pick_faraway_object()")
        elif dice_roll == 2:
            if self.pull_faraway_pix("black_hole"):
                self.pix_xy.append(self.pick_spot_in_zone(zone))
            elif self.debug:
                self.write_to_log("ERROR pulling black hole at random in Settings.pick_faraway_object()")
        elif dice_roll == 3:
            if self.pull_faraway_pix("comet"):
                self.pix_xy.append(self.pick_spot_in_zone(zone))
            elif self.debug:
                self.write_to_log("ERROR pulling comet at random in Settings.pick_faraway_object()")
        elif dice_roll == 4:
            if self.pull_faraway_pix("galaxy"):
                self.pix_xy.append(self.pick_spot_in_zone(zone))
            elif self.debug:
                self.write_to_log("ERROR pulling galaxy at random in Settings.pick_faraway_object()")
        elif dice_roll == 5:
            if self.pull_faraway_pix("gas_giant"):
                self.pix_xy.append(self.pick_spot_in_zone(zone))
            elif self.debug:
                self.write_to_log("ERROR pulling gas giant at random in Settings.pick_faraway_object()")
        elif dice_roll == 6:
            if self.pull_faraway_pix("nebula"):
                self.pix_xy.append(self.pick_spot_in_zone(zone))
            elif self.debug:
                self.write_to_log("ERROR pulling nebula at random in Settings.pick_faraway_object()")
        elif dice_roll == 7:
            if self.pull_faraway_pix("quasar"):
                self.pix_xy.append(self.pick_spot_in_zone(zone))
            elif self.debug:
                self.write_to_log("ERROR pulling quasar at random in Settings.pick_faraway_object()")
        elif dice_roll == 8:
            if self.pull_faraway_pix("sun"):
                self.pix_xy.append(self.pick_spot_in_zone(zone))
            elif self.debug:
                self.write_to_log("ERROR pulling sun at random in Settings.pick_faraway_object()")
        elif dice_roll == 8:
            if self.pull_faraway_pix("moon"):
                self.pix_xy.append(self.pick_spot_in_zone(zone))
            elif self.debug:
                self.write_to_log("ERROR pulling moon at random in Settings.pick_faraway_object()")
        elif self.debug:
            self.write_to_log("Unspecified ERROR in Settings.pick_faraway_object.()")
    
    def set_starfield(self):
        """ set starfield of random stars with random colors """
        self.starfield_clr = []
        self.starfield_xy = []
        for w in range(self.act_w):
            for h in range(self.act_h):
                if random.random() <= self.stardensity:
                    self.starfield_clr.append(rand_clr())     # assign color
                    self.starfield_xy.append( (w, h) )

        for zone in range(1, (NUM_ZONES+1)):
            if random.uniform(0, 1) < DEFAULT_CHANCE_FOR_FARAWAY_OBJECT:
                self.pick_faraway_object(zone)
        
    def draw_stars(self):
        """ Draw stars on current background """
        for ind in range(len(self.starfield_xy)):
            self.screen.set_at(self.starfield_xy[ind], \
                self.starfield_clr[ind])

        if self.faraway_pixies:
            for pixie in range( 0, len(self.faraway_pixies) ):
                self.screen.blit(self.faraway_pixies[pixie], self.pix_xy[pixie])

    def restore_screen(self):
         # declaration of Surface object
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height) )
        # get actual window size
        (self.act_w, self.act_h) = pygame.display.get_window_size()

    def destroy_screen(self):
        """prevent errors with deepcopy()"""
        del self.screen

    def write_to_log(self, text):
        self.now = datetime.datetime.now()
        if isinstance(text, list):
            self.log_text.append("<<<" + self.now.strftime("%H:%M:%S:%f") + ">>>\n")
            for line in text:
                self.log_text.append("* " + line + "\n")
        else:
                self.log_text.append("<<<" + self.now.strftime("%H:%M:%S:%f") + ">>>  " + text + "\n")

    def output_log_to_file(self):
        if len(self.log_text):
            with open(self.log_filename, 'a') as log_file:
                if isinstance(self.log_text, list):
                    for line in self.log_text:
                        log_file.write(line)
                else:
                    log_file.write(line)