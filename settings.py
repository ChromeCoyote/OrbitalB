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
DEFAULT_CRIT_MASS = LUNA_MASS / 16      # critical radius under which celestials die
DEFAULT_CRIT_EXPLODE_MASS = LUNA_MASS        # cannonballs blow up the moon!
# mass of collidiing object has to be this many times more to cause shatter
DEFAULT_CRIT_MASS_RATIO = 1        

DEFAULT_TANK_SCREENRAD = 3      # default tank screen radius
DEFAULT_TANK_COLOR = (0,255,0)  # default tank color, lime green?
DEFAULT_ENEMY_TANK_COLOR = (255, 0, 255)    # enemy tank color, magenta
DEFAULT_THIRD_TANK_COLOR = (255, 255, 0)    # third tank color, yellow
DEFAULT_ESCAPE_FRAC = 0.5       # default cannonball speed as fraction

DEFAULT_RADIAN_STEP = ((2*math.pi) / 360)
DEFAULT_SPEED_DIV = 100        
DEFAULT_POSITION_ANGLE = math.pi / 2     # initial posistion on surface in radians
DEFAULT_FIRING_ANGLE = 0       # initial firing angle in radians

DEFAULT_FUSE_TIME = 1               # fuse lasts for 1 second, after which cannonball becomes armed
DEFAULT_EXPLODE_TIME = 2               # cannonballs explode for this many seconds
DEFAULT_GIVEN_AWAY_TIME = 10           # how long cannonballs last when shooting tank dies
DEFAULT_FLASH_CHANCE = 0.8            # cannonballs flash new color when exploding
DEFAULT_CANNONBALL_MASS = 1000      # default cannonball mass

DEFAULT_MESSAGE_TIME = 3

# don't select a color every explode tick 
SKIP_COLOR = 100

DEFAULT_BALL_COLOR = (255, 255, 255)    # white
DEFAULT_ARMED_COLOR = (255, 69, 0)        # orange
DEFAULT_FLASH_COLORS = [ 
    (240, 248, 255),    # alice blue
    (176, 244, 230),    # powder blue
    (135, 206, 250),    # light sky blue
    (135, 206, 235),    # sky blue
    (0, 191, 255),      # deep sky blue
    (30, 144, 255),     # dodger blue
    (0, 0, 255),        # blue
    (100, 149, 237),    # corn flower blue
    (255, 255, 255),    # white
    (65, 105, 255) ]    # royal blue

DEFAULT_GREEN_SNAIL_FLASH_COLORS = [
    (124, 252, 0),      # lawn green
    (127, 252, 0),      # chartreuse
    (0, 255, 0),        # lime green
    (255, 255, 255),     # white
    (0, 255, 127),       # spring green
    (152, 251, 152),     # pale green
    (0, 250, 154)       # medium spring green
]

DEFAULT_RED_SNAIL_FLASH_COLORS = [
    (220, 20, 60),       # crimson
    (255, 255, 255),    # white
    (255, 0, 0),        # red
    (255, 0, 255),      # magenta
    (238, 130, 238),     # violet
    (216, 191, 216),     # thisle
    (221, 160, 221)     # plum
]

DEFAULT_YELLOW_SNAIL_FLASH_COLORS = [
    (255, 255, 255),    # white
    (255, 215, 0),       # gold
    (255, 165, 0),      # orange
    (255, 255, 0),      # yellow
    (255, 255, 224),    # light yellow
    (255, 255, 153),    # light yellow #2
    (255, 255, 102)    # light yellow #3
]

DEFAULT_BALL_SCREEN_RAD = 2     # small yet visible
# scaling for changes to velocity per key press
DEFAULT_RADIAN_STEP = ((2*math.pi) / 360)

# Default targeting arrow colors
DEFAULT_HOT_ARROW_COLOR = (255, 0, 0)       # red
DEFAULT_WARM_ARROW_COLOR = (128, 0, 128)    # purple
DEFAULT_COLD_ARROW_COLOR = (0, 255, 255)    # cyan
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
DEFAULT_EXPLODE_ENERGY = CZAR_BOMBA_ENERGY / 2e10
# DEFAULT_EXPLODE_ENERGY = 0

DEFAULT_EXPLODE_RADIUS = LUNA_RADIUS / 2 # explosion is 1/4 radius of Moon!

DEFAULT_BODY_COLOR = (0, 94, 184)       # ocean color
DEFAULT_LUNA_COLOR = (254, 252, 215)    # Moon Glow
# DEFAULT LUNA_COLOR = (201, 201, 201)   # gray
DEFAULT_COMET_COLOR = (200, 233, 233)   # ice blue

DEFAULT_FONT_SIZE = 24
DEFAULT_FONT_COLOR = (255, 255, 255)    # white

DEFAULT_SPELL_COOLDOWN_TIME = 10
DEFAULT_SPELL_TIME = 3

DEFAULT_GRAVITY_INCREASE = 10

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
SPELL_SHIELD = pygame.K_s
SPELL_GRAVITY = pygame.K_g
SPELL_ICE = pygame.K_i

DEFAULT_AI_TOLERANCE = 1
# How often enemy tank will choose to fire rather than move
DEFAULT_AI_FIRE_WEIGHT = 0.8
DEFAULT_AI_SPELL_WEIGHT = 0.8
# How long in seconds that AI tank will wait to make an action to slow it down
DEFAULT_AI_WAIT_TIME = 1/8
# AI Tanks will avoid armed or exploding balls 
# this fraction of the homeworld's radius away
DEFAULT_DANGER_RATIO = 0.2

# Game will keep track of objects that are this far out of screen,
# i.e. if value is 0.5, objects will be keep in memory as long as they
# are within 50% the total screen height or width outside the actual screen
DEFAULT_VIRTUAL_SCREEN = 0.5

# Chance for one of the 8 zones to have a faraway object
DEFAULT_CHANCE_FOR_FARAWAY_OBJECT = 1/4
NUM_ZONES = 8

# Number of faraway object categories

FARAWAY_OBJECT_DIR = "Pix/Faraway_Objects"
HOMEWORLDS_DIR = "Pix/Homeworlds"

DWARVES_PATH = "Pix/Dwarves"
MOONS_PATH = "Pix/Moons"

SNAILS_PATH = "Pix/Snails"

EXPLOSIONS_PATH = "Pix/Explosions"

SPELLBOOK_PATH = "Pix/Magic/Spellbook"
ICE_PATH = "Pix/Magic/Ice"

DEFAULT_BALL_PIX_SCREEN_RAD = 10

DEFAULT_SNAIL_SCREEN_RADIUS = 25
DEFAULT_SNAIL_DISPLACEMENT_FACTOR = 0.25

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
        files_in_dir = os.listdir(path)
        if files_in_dir:
            random_file = random.choice(files_in_dir)
            random_file = os.path.join(old_path, random_file)
            random_file = os.path.normpath(random_file)
            if not os.path.isfile(random_file):
                random_file = False
        
    return random_file

def choose_random_directory(path):
    random_dir = False
    # print(f"\nOriginal path is:  {path}")
    path = os.path.normpath(path)
    # print(f"\nNew path is:  {path}")
    if os.path.exists(path):
        dirs = os.listdir(path)
        if dirs:
            random_dir = random.choice(dirs)
            random_dir = os.path.join(path, random_dir)
            random_dir = os.path.normpath(random_dir)
            if not os.path.isdir(random_dir):
                random_dir = False
                # print(f"\nERROR in settings.choose_random_directory:  {random_dir} is not a directory...")

    # print(f"Random directory chose is {random_dir}...")    
    return random_dir

def random_pix_transform(pix):
    flip_x = random.getrandbits(1)
    flip_y = random.getrandbits(1)
    spin = random.randint(0, 3)
    pygame.transform.rotate(pix, spin*90)
    pygame.transform.flip(pix, flip_x, flip_y)
    
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

    def pick_faraway_pix(self, zone):
        """ Randomly select a sprite for background from defined directories.  """
        pix_path = choose_random_directory(FARAWAY_OBJECT_DIR)
        pix_path = choose_random_file(pix_path)
        if pix_path:
            self.faraway_pixies.append(
                (pygame.image.load_extended(pix_path), self.pick_spot_in_zone(zone)) )
            self.faraway_pixies[-1][0].convert_alpha()
            if self.debug:
                self.write_to_log(f"Image at {pix_path} choosen for background...")
        elif self.debug:
            self.write_to_log(f"Can't find faraway image ax {pix_path}!")
        
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
                self.pick_faraway_pix(zone)
        
    def draw_stars(self):
        """ Draw stars on current background """
        for ind in range(len(self.starfield_xy)):
            self.screen.set_at(self.starfield_xy[ind], \
                self.starfield_clr[ind])

        if self.faraway_pixies:
            for pixie in self.faraway_pixies:
                self.screen.blit(
                    pixie[0], pixie[0].get_rect(center = pixie[1]) )
    
    def write_to_log(self, text):
        """ Add list or string of text to memory to be written later to file. """
        self.now = datetime.datetime.now()
        if isinstance(text, list):
            self.log_text.append("<<<" + self.now.strftime("%H:%M:%S:%f") + ">>>\n")
            for line in text:
                self.log_text.append("* " + line + "\n")
        else:
                self.log_text.append("<<<" + self.now.strftime("%H:%M:%S:%f") + ">>>  " + text + "\n")

    def output_log_to_file(self):
        """ Write text in memory to file. """
        if len(self.log_text):
            with open(self.log_filename, 'a') as log_file:
                if isinstance(self.log_text, list):
                    for line in self.log_text:
                        log_file.write(line)
                else:
                    log_file.write(line)