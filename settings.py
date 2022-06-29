from pickle import TRUE
import pygame
import random
import math
import numpy

# real world variables
EARTH_RADIUS = 6_371    # in kilometers
EARTH_MASS = 5.972e24   # in kilograms
EARTH_DENSITY = 5515    # in kilograms per meter cubed

LUNA_RADIUS = 1_737.1   # in kilometers
LUNA_MASS = 7.34767309e22   # in kilograms
LUNA_DENSITY = 3340     # in kilograms per meter cubed
LUNA_ORBIT_RAD = 385_000   # in km

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
DEFAULT_CRIT_RADIUS = LUNA_RADIUS / 4      # critical radius under which celestials die
DEFAULT_CRIT_EXPLODE_MASS = LUNA_MASS        # cannonballs blow up the moon!
# mass of collidiing object has to be this many times more to cause shatter
DEFAULT_CRIT_MASS = 1        

DEFAULT_TANK_SCREENRAD = 3      # default tank screen radius
DEFAULT_TANK_COLOR = (0,255,0)  # default tank color, lime green?
DEFAULT_ENEMY_TANK_COLOR = (255, 0, 255)    # enemy tank color, magenta
DEFAULT_ESCAPE_FRAC = 0.5       # default cannonball speed as fraction

DEFAULT_HOT_ARROW_COLOR = (255, 0, 0)       # default arrow colors
DEFAULT_WARM_ARROW_COLOR = (255, 255, 0)
DEFAULT_COLD_ARROW_COLOR = (0, 255, 255)
HOT_THRESHOLD = 0.9                         # thresholds for arrows
COLD_THRESHOLD = 0.3

DEFAULT_RADIAN_STEP = ((2*math.pi) / 360)
DEFAULT_SPEED_DIV = 100        
DEFAULT_POSITION_ANGLE = math.pi / 2     # initial posistion on surface in radians
DEFAULT_FIRING_ANGLE = 0       # initial firing angle in radians

FUSE_THRESHOLD = 100                 # threshold for fuse
EXPLODE_THRESHOLD = 1000              # threshohld for explosion
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

# AI PARAMETERS
SIMPLE_SPEED_GUESS_LOWER = 0.9
SIMPLE_SPEED_GUESS_HIGHER = 1

# Cannonballs have as much energy as 1 million Czar Bombs
DEFAULT_EXPLODE_ENERGY = CZAR_BOMBA_ENERGY / 2e12

DEFAULT_EXPLODE_RADIUS = LUNA_RADIUS / 2 # explosion is 1/4 radius of Moon!

DEFAULT_BODY_COLOR = (0, 94, 184)       # ocean color

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

class Settings:
    """Stores settings for game"""

    def __init__(self, width = DEFAULT_WIDTH, height = DEFAULT_HEIGHT):
        """Initialize the game's settings."""
        pygame.init()       # inialize pygame modules

        self.debug = True   # debugging on for now...

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
        self.crit_radius = DEFAULT_CRIT_RADIUS
        self.crit_explode_mass = DEFAULT_CRIT_EXPLODE_MASS*1.01

        # declaration of Surface object
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height) )
        # get actual window size
        (self.act_w, self.act_h) = pygame.display.get_window_size()

        self.starfield_clr = []     # inialize starfield color array
        self.starfield_xy = []      # inialize starfield coordinates
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

    def set_starfield(self):
        """ set starfield of random stars with random colors """
        self.starfield_clr = []
        self.starfield_xy = []
        for w in range(self.act_w):
            for h in range(self.act_h):
                if random.random() <= self.stardensity:
                    self.starfield_clr.append(rand_clr())     # assign color
                    self.starfield_xy.append( (w, h) )

    def draw_stars(self):
        """ Draw stars on current background """
        for ind in range(len(self.starfield_xy)):
            self.screen.set_at(self.starfield_xy[ind], \
                self.starfield_clr[ind])

    def restore_screen(self):
         # declaration of Surface object
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height) )
        # get actual window size
        (self.act_w, self.act_h) = pygame.display.get_window_size()

    def destroy_screen(self):
        """prevent errors with deepcopy()"""
        del self.screen