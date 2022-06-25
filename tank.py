# Code for projectile

from asyncio.windows_events import NULL
from tkinter.font import families
import pygame, math, random
import settings, cosmos, cannonball

DEFAULT_TANK_SCREENRAD = 3      # default tank screen radius
DEFAULT_TANK_COLOR = (0,255,0)  # default tank color, lime green?
DEFAULT_ESCAPE_FRAC = 0.5       # default cannonball speed as fraction

DEFAULT_HOT_ARROW_COLOR = (255, 0, 0)       # default arrow colors
DEFAULT_WARM_ARROW_COLOR = (255, 255, 0)
DEFAULT_COLD_ARROW_COLOR = (0, 255, 255)
HOT_THRESHOLD = 0.9                         # thresholds for arrows
COLD_THRESHOLD = 0.3

DEFAULT_RADIAN_STEP = ((2*math.pi) / 360)
DEFAULT_SPEED_DIV = 100        
DEFAULT_POSITION_ANGLE = math.pi / 2     # initial posistion on surface in radians
DEFAULT_FIRING_ANGLE = math.pi / 4       # initial firing angle in radians

FUSE_THRESHOLD = 10000                 # threshold for fuse
EXPLODE_THRESHOLD = 10000              # threshohld for explosion

# don't select a color every explode tick 
SKIP_COLOR = 1000


class Tank (cosmos.Celestial):
    """ Class for surface roaming tanks """

    def __init__(self, sts, celestials):
        """ Initialize variables for tank """
        super().__init__(sts)

        self.name = 'Tank'

        self.radius = 0.1            # 100 m meter radius
        
        self.homeworld = False       # not the homeworld ;)
        self.gravity = False         # ignore gravity of this object
        self.screen_rad = DEFAULT_TANK_SCREENRAD  
        self.color = DEFAULT_TANK_COLOR

        # find and setup stats for homeworld
        self.homeworld = cosmos.Celestial(sts)
        for body in celestials:
            if body.homeworld == True:
                self.homeworld = body
   
        # calculate escape velocity
        self.escape_v = math.sqrt(2 * settings.GRAV_CONST * \
            self.homeworld.mass / self.homeworld.radius)
    
        self.arrow_color = DEFAULT_WARM_ARROW_COLOR      # velocity arrow color
        self.radian_step = DEFAULT_RADIAN_STEP
        # step for velocity change with each key press
        self.speed_step = self.escape_v / DEFAULT_SPEED_DIV
        
        self.celestials = celestials 
        
        self.alive = True     # starts out actually alive!

        self.pos_angle = DEFAULT_POSITION_ANGLE     # initial posistion on surface
        self.launch_angle = self.pos_angle + DEFAULT_FIRING_ANGLE   # default firing angle
        self.launch_speed = DEFAULT_ESCAPE_FRAC * self.escape_v  # set initial speed to half of escape velocity 
        self.set_arrow_color()

        self.balls = []                  # empty active cannonballs
        self.chambered_ball = False              # ball chambered or not
        self.num_balls = 0

        self.set_surface_pos()     # initalize x, y posistion

        # self.ball_force 

    def fix_launch_velocity(self):
        if self.launch_speed < 0:
            self.launch_speed = 0
        elif self.launch_speed > self.escape_v:
            self.launch_speed = self.escape_v
        
        if self.launch_angle < 0:
            self.launch_angle = 0
        elif self.launch_angle > 2*math.pi:
            self.launch_angle = self.launch_angle % 2*math.pi
        
    def reset_default_launch(self):
        self.launch_speed = DEFAULT_ESCAPE_FRAC * self.escape_v            # default speed
        self.launch_angle = self.pos_angle + DEFAULT_FIRING_ANGLE    # default firing angle

    def update_celestials(self, celestials):
        """ update homewold values """
        self.celestials = celestials
        for body in celestials:
            if body.homeworld == True:
                self.homeworld = body

    def check_chamber(self):
        chamber_ready = 0
        for ball in self.balls:
            if ball.chambered:
                chamber_okay += 1
        
        return chamber_okay
    
    def set_surface_pos(self):
        """ set launch point based on position angle (pos_angle) """
        self.x = self.homeworld.radius * math.cos(self.pos_angle) \
            + self.homeworld.x
        self.y = self.homeworld.radius * math.sin(self.pos_angle) \
            + self.homeworld.y
        super().get_screenxy()
        
        return (self.x, self.y)
        
    def set_arrow_color(self):
        ratio = self.launch_speed / self.escape_v
        if ratio > HOT_THRESHOLD:
            self.arrow_color = DEFAULT_HOT_ARROW_COLOR
        elif ratio < COLD_THRESHOLD:
            self.arrow_color = DEFAULT_COLD_ARROW_COLOR
        else:
            self.arrow_color = DEFAULT_WARM_ARROW_COLOR
        
    def get_launch_velocity(self):
        vx = self.launch_speed * math.cos(self.launch_angle)
        vy = self.launch_speed * math.sin(self.launch_angle)
        return (vx, vy)
    
    def chamber_ball(self):
        """ Chamber a cannonball and prepare to fire it"""
        chamber_success = False
        
        if not self.chambered_ball:
            self.balls.append(cannonball.Cannonball(self.sts, self.celestials))
            self.num_balls = len(self.balls)    # set number of balls counted in balls list
            self.chambered_ball = True  # set index of currently chambered ball
            self.balls[-1].set_xy(self.x, self.y)
            self.fix_launch_velocity()
            [self.balls[-1].vx, self.balls[-1].vy] = self.get_launch_velocity()
            self.balls[-1].chambered = True
            chamber_success = True

        return chamber_success

    def fire_ball(self):
        """ Fire chambered cannonball """
        fire = False
        
        if self.chambered_ball:        # if a ball is chambered...
            self.chambered_ball = False         # set chamber to empty
            self.balls[-1].chambered = False   # set chambered ball's status to not so
            self.balls[-1].active = True       # set chambered ball to active
            [self.balls[-1].vx, self.balls[-1].vy] = self.get_launch_velocity()
            [self.balls[-1].x, self.balls[-1].y] = (self.x, self.y)
            self.balls[-1].get_screenxy()
            fire = True
        
        return fire

    def move_balls(self):
        """ Move active balls """
        for ball in self.balls:
            if ball.active == True:
                ball.move(self.celestials)
    
    def check_balls(self):
        """ Check status of active balls """

        for ball in self.balls:
            if ball.active:
                if not ball.armed:
                    ball.fuse_timer += 1
                    if ball.fuse_timer > FUSE_THRESHOLD:
                        ball.armed = True
                        ball.color = cannonball.DEFAULT_ARMED_COLOR
                ball.check_impact(self.celestials)
            
            if ball.exploding:
                if not (ball.explode_timer % SKIP_COLOR):
                    ball.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                ball.explode_timer += 1
                if ball.explode_timer > EXPLODE_THRESHOLD:
                    ball.exploding = False
                   
        for ball in self.balls[:]:
            if not ball.active and not ball.exploding and not ball.chambered:
                self.balls.remove(ball)
        
        self.num_balls = len(self.balls)

    def detonate_ball(self):
        blew_up = False
        for ball in self.balls:
            if ball.active and ball.armed and not blew_up:
                ball.explode()
                blew_up = True
        
        return blew_up

    def draw_launch_v(self):
        self.set_arrow_color()
        (tempvx, tempvy) = self.get_launch_velocity()
        (tempvx, tempvy) = super().normalize(tempvx, tempvy)
        tempvx *= self.homeworld.radius * (self.launch_speed / self.escape_v)
        tempvx += self.x
        tempvy *= self.homeworld.radius * (self.launch_speed / self.escape_v)
        tempvy += self.y
        (tip_x, tip_y) = super().set_screenxy(tempvx, tempvy)
        pygame.draw.line(self.sts.screen, self.arrow_color, [self.screen_x, self.screen_y], [tip_x, tip_y])
        return (tip_x, tip_y)

    def display_tank_values(self):
        """Print properties of tank"""
        printx = 0
        printy = 0
        print(f"\n")
        super().display_values()
        print(f"The tanks's launch angle is {self.launch_angle} radians.")
        print(f"The tank's launch speed is {self.launch_speed}.")
        (printx, printy) = self.get_launch_velocity()
        print(f"The tank's launch velocity is <{printx, printy}>.")
        (printx, printy) = self.draw_launch_v()
        print(f"The tip of the launch vectory on screen should be:  <{printx, printy}>.")

    def display_ball_stats(self):
        print(f"Balls in memory:  {len(self.balls)}.")
        print(f"Counted balls:  {self.num_balls}.")
        ball_number = 0
        for ball in self.balls:
            ball_number += 1
            print(f"\nBall #{ball_number}:")
            ball.display_ball_values()



    
