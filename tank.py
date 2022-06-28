# Code for projectile

from asyncio.windows_events import NULL
from tkinter.font import families
import pygame, math, random, numpy
import settings, cosmos, cannonball

def check_tanks(tanks):
    destroyed_player_tanks = []
    
    for tank in tanks[:]:
        if not tank.active:
            if tanks[0].sts.debug:
                print(f"\n{tank.name} being destroyed...")    
            if tank.balls:
                if tank != tanks[0]:
                # give destroyed tank's balls to first tank's balls
                    tank.give_balls(tanks[0])
                    if tanks[0].sts.debug:
                        print(f"\nBalls from {tank.name} given to first tank's ball list.")
                else:
                # give destroyed tank's balls to last tank's balls
                    tank.give_balls(tanks[-1])
                    if tanks[0].sts.debug:
                        print(f"\nBalls from {tank.name} given to last tank's ball list.")
            if tank.player_tank:
                destroyed_player_tanks.append(tank)
            tanks.remove(tank)
            if tanks[0].sts.debug:
                print(f"Tank successfully destroyed!")

    if not destroyed_player_tanks:
        destroyed_player_tanks = False

    return destroyed_player_tanks
 
class Tank (cosmos.Celestial):
    """ Class for surface roaming tanks """

    def __init__(self, sts, celestials):
        """ Initialize variables for tank """
        super().__init__(sts)

        self.name = "Player Tank"

        self.radius = 0.1            # 100 m meter radius
        
        self.homeworld = False       # not the homeworld ;)
        self.gravity = False         # ignore gravity of this object
        self.screen_rad = settings.DEFAULT_TANK_SCREENRAD  
        self.color = settings.DEFAULT_TANK_COLOR

        # find and setup stats for homeworld
        self.homeworld = cosmos.Celestial(sts)
        for body in celestials:
            if body.homeworld == True:
                self.homeworld = body
   
        # calculate escape velocity
        self.escape_v = math.sqrt(2 * settings.GRAV_CONST * \
            self.homeworld.mass / self.homeworld.radius)
    
        self.arrow_color = settings.DEFAULT_WARM_ARROW_COLOR      # velocity arrow color
        self.radian_step = settings.DEFAULT_RADIAN_STEP
        # step for velocity change with each key press
        self.speed_step = self.escape_v / settings.DEFAULT_SPEED_DIV
        
        self.celestials = celestials 
        
        self.alive = True     # starts out actually alive!

        self.pos_angle = settings.DEFAULT_POSITION_ANGLE     # initial posistion on surface
        self.launch_angle = self.pos_angle + settings.DEFAULT_FIRING_ANGLE   # default firing angle
        self.launch_speed = settings.DEFAULT_ESCAPE_FRAC * self.escape_v  # set initial speed to half of escape velocity 
        self.set_arrow_color()

        self.balls = []                  # empty active cannonballs
        self.chambered_ball = False              # ball chambered or not
        self.num_balls = 0

        self.player_tank = True     # default player tank
        self.winner = False         # not a winner yet!

        self.get_surface_pos()     # initalize x, y posistion

        self.chamber_ball_key = settings.CHAMBER_BALL
        self.fire_ball_key = settings.FIRE_BALL
        self.increase_angle_key = settings.INCREASE_ANGLE
        self.decrease_angle_key = settings.DECREASE_ANGLE
        self.increase_speed_key = settings.INCREASE_SPEED
        self.decrease_speed_key = settings.DECREASE_SPEED
        self.move_CCW_key = settings.MOVE_TANK_CCW
        self.move_CW_key = settings.MOVE_TANK_CW
        self.detonate_ball_key = settings.DETONATE_BALL

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
        self.launch_speed = settings.DEFAULT_ESCAPE_FRAC * self.escape_v            # default speed
        self.launch_angle = self.pos_angle + settings.DEFAULT_FIRING_ANGLE    # default firing angle

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
    
    def get_surface_pos(self):
        """ set launch point based on position angle (pos_angle) """
        self.x = self.homeworld.radius * math.cos(self.pos_angle) \
            + self.homeworld.x
        self.y = self.homeworld.radius * math.sin(self.pos_angle) \
            + self.homeworld.y
        super().get_screenxy()
        
        return (self.x, self.y)
        
    def set_arrow_color(self):
        ratio = self.launch_speed / self.escape_v
        if ratio > settings.HOT_THRESHOLD:
            self.arrow_color = settings.DEFAULT_HOT_ARROW_COLOR
        elif ratio < settings.COLD_THRESHOLD:
            self.arrow_color = settings.DEFAULT_COLD_ARROW_COLOR
        else:
            self.arrow_color = settings.DEFAULT_WARM_ARROW_COLOR
        
    def get_launch_velocity(self):
        vx = self.launch_speed * math.cos(self.launch_angle) + self.homeworld.vx
        vy = self.launch_speed * math.sin(self.launch_angle) + self.homeworld.vy
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
    
    def check_balls(self, tanks):
        """ Check status of active balls """

        for ball in self.balls:
            if ball.active:
                if not ball.armed and not ball.exploding:
                    ball.fuse_timer += 1
                    if ball.fuse_timer > settings.FUSE_THRESHOLD:
                        ball.armed = True
                        ball.color = settings.DEFAULT_ARMED_COLOR
                if ball.exploding:
                    if ball.stuck_to_celestial:
                        ball.get_surface_pos()
                    if not (ball.explode_timer % settings.SKIP_COLOR):
                        ball.color = (
                            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                    ball.explode_timer += 1
                    if ball.explode_timer > settings.EXPLODE_THRESHOLD:
                        ball.exploding = False
                        ball.active = False
                ball.check_impact(self.celestials, tanks)
                   
        for ball in self.balls[:]:
            if not ball.active and not ball.chambered:
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
        [tip_x, tip_y] = self.get_launch_velocity()
        [tip_x, tip_y] = numpy.subtract(
            [tip_x, tip_y], [self.homeworld.vx, self.homeworld.vy])
        [tip_x, tip_y] = cosmos.normalize([tip_x, tip_y])
        tip_x *= self.homeworld.radius * (self.launch_speed / self.escape_v)
        tip_y *= self.homeworld.radius * (self.launch_speed / self.escape_v)
        [tip_x, tip_y] = numpy.add([tip_x, tip_y], [self.x, self.y])
        [tip_x, tip_y] = super().set_screenxy(tip_x, tip_y)
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
        print(f"Balls in memory for {self.name}:  {len(self.balls)}.")
        print(f"Counted balls for {self.name}:  {self.num_balls}.")
        ball_number = 0
        for ball in self.balls:
            ball_number += 1
            print(f"\nBall #{ball_number} of {self.name}:")
            ball.display_ball_values()

    def set_enemy_tank(self):
        """ Sets tank to an enemy """
        self.player_tank = False
        self.name = "Enemy Tank"
        self.color = settings.DEFAULT_ENEMY_TANK_COLOR
        self.pos_angle = settings.DEFAULT_POSITION_ANGLE + math.pi
        self.get_surface_pos()

    def give_balls(self, tank):
        if self.balls:
            for ball in self.balls:
                tank.balls.append(ball)
    
        