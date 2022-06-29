# Code for projectile

from asyncio.windows_events import NULL
from tkinter.font import families
import pygame, math, random, numpy
import settings, cosmos, cannonball

def check_tanks(tanks, _settings):
    destroyed_player_tanks = []
    
    if tanks:
        for tank in tanks[:]:
            if not tank.active:
                if _settings.debug:
                    print(f"\n{tank.name} being destroyed...")    
                if tank.balls:
                    if tank != tanks[0]:
                    # give destroyed tank's balls to first tank's balls
                        tank.give_balls(tanks[0])
                        if _settings.debug:
                            print(f"\nBalls from {tank.name} given to first tank's ball list.")
                    elif tank != tanks[-1]:
                    # give destroyed tank's balls to last tank's balls
                        tank.give_balls(tanks[-1])
                        if _settings.debug:
                            print(f"\nBalls from {tank.name} given to last tank's ball list.")
                    else:
                        if _settings.debug:
                            print(f"\nOnly one tank left, can't give balls away!")
                if tank.player_tank:
                    destroyed_player_tanks.append(tank)
                tanks.remove(tank)
                if _settings.debug:
                    print(f"Tank successfully destroyed!")
        if not destroyed_player_tanks:
            destroyed_player_tanks = False
    else:
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
        self.homeworld = False
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

        # AI variables
        self.angle_guess = self.launch_angle
        self.speed_guess = self.launch_speed
        self.pos_target = self.pos_angle
        self.moving = False
        self.targeting = False

        self.mu = 0         # orbital constant

        if self.homeworld:
            self.mu = -settings.GRAV_CONST*self.homeworld.mass

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
        body.homeworld = False
        for body in celestials:
            if body.homeworld == True:
                self.homeworld = body
        if self.homeworld:
            self.mu = -settings.GRAV_CONST*self.homeworld.mass
        else:
            self.mu = 0

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
                ball.check_impact(tanks)
                   
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
        self.reset_default_launch()

    def give_balls(self, tank):
        if self.balls:
            for ball in self.balls:
                if not ball.chambered:
                    tank.balls.append(ball)
    
    def guess_launch_angle(self, targeted_tank):
        if targeted_tank.active:
            radical_factor = (self.mu * targeted_tank.pos_angle) / (self.pos_angle**2 * self.launch_speed**2)
            if radical_factor < 0:
                self.pick_launch_angle()
            else:
                self.angle_guess = math.asin(math.sqrt(radical_factor))
        else:
            self.pick_launch_angle()
    
    def guess_launch_speed(self, targeted_tank):
        if targeted_tank.active:
            self.speed_guess = math.sqrt(
                (self.mu * targeted_tank.pos_angle) / (self.pos_angle**2 * (math.sin(self.launch_angle)) ** 2)
            )
        else:
            self.pick_launch_speed()

    def pick_launch_angle(self):
        if random.randint(0, 1):
            self.angle_guess = random.uniform(
                (self.pos_angle + 3*math.pi/8), (self.pos_angle + math.pi/8) )
        else:
            self.angle_guess = random.uniform(
                (self.pos_angle - 3*math.pi/8), (self.pos_angle - math.pi/8) )
    
    def pick_launch_speed(self):
        self.speed_guess = random.uniform(
            settings.SIMPLE_SPEED_GUESS_LOWER*self.escape_v, settings.SIMPLE_SPEED_GUESS_HIGHER*self.escape_v)
    
    def simple_target(self):
        self.pick_launch_angle()
        self.pick_launch_speed()

    def quick_target(self, targeted_tank):
        self.pick_launch_speed()
        self.guess_launch_angle(targeted_tank)

    def check_moving(self):
        if abs(self.pos_angle - self.pos_target) < 2*self.radian_step:
            self.moving = False
            if self.sts.debug:
                print(f"\n{self.name} at target position, not moving...")
        else:
            self.moving = True
            if self.sts.debug:
                print(f"\n{self.name} not at target position, moving...")

    def check_targeting(self):
        angle_ready = False
        speed_ready = False
        
        if abs(self.launch_angle - self.angle_guess) < 10*self.radian_step:
            angle_ready = True
        if abs(self.launch_speed - self.speed_guess) < 2*self.speed_step:
            speed_ready = True

        if angle_ready and speed_ready and self.targeting:
            if self.sts.debug:
                print(f"\n{self.name} firing solution within tolerances, not adjusting firing solution...")
                print(f"\n{self.name} attempting to fire cannonball...")
    
            if self.chambered_ball:
                self.fire_ball()
                self.targeting = False
            elif self.sts.debug:
                print("\nError firing cannonball, no ball chambered!")
        elif self.targeting:
            if self.sts.debug:
                print(f"\n{self.name} firing solution not within tolerances, adjusting firing solution...")
            if self.angle_guess > self.launch_angle and not angle_ready:
                self.launch_angle += self.radian_step
                if self.sts.debug:
                    print(f"\n{self.name} adjusted targeting angle one unit CCW...")
            elif self.angle_guess < self.launch_angle and not angle_ready:
                self.launch_angle -= self.radian_step
                if self.sts.debug:
                    print(f"\n{self.name} adjusted targeting angle one unit CW...")
            elif self.launch_speed > self.speed_guess and not speed_ready:
                self.launch_speed -= self.speed_step
                if self.sts.debug:
                    print(f"\n{self.name} lowered launch speed one unit...")
            elif self.launch_speed < self.speed_guess and not speed_ready:
                self.launch_speed += self.speed_step
                if self.sts.debug:
                    print(f"\n{self.name} increased launch speed one unit...")

    def pick_position(self):
            if random.randint(0, 1):
                self.pos_target = random.uniform(
                    (self.pos_angle + 3*math.pi/8), (self.pos_angle + math.pi/8) )
            else:
                self.pos_target = random.uniform(
                    (self.pos_angle - 3*math.pi/8), (self.pos_angle - math.pi/8) )
            if self.sts.debug:
                print(f"\n{self.name} choose to move to {round(self.pos_target, 4)}, cururently at {round(self.pos_angle, 4)}.")
            
            self.check_moving()
        
    def move_to_position_target(self):
        self.check_moving()
        if self.pos_target > self.pos_angle and self.moving:
            self.pos_angle += self.radian_step
            self.get_surface_pos()
            if self.sts.debug:
                print(f"\n{self.name} moved one unit CCW...")
            self.reset_default_launch()
        elif self.pos_target < self.pos_angle and self.moving:
            self.pos_angle -= self.radian_step
            self.get_surface_pos()
            if self.sts.debug:
                print(f"\n{self.name} moved one unit CW...")
            self.reset_default_launch()

    def pick_position(self):
            if random.randint(0, 1):
                self.pos_target = random.uniform(
                    (self.pos_angle + 3*math.pi/8), (self.pos_angle + math.pi/8) )
            else:
                self.pos_target = random.uniform(
                    (self.pos_angle - 3*math.pi/8), (self.pos_angle - math.pi/8) )
            if self.sts.debug:
                print(f"\n{self.name} choose to move to {round(self.pos_target, 4)}, cururently at {round(self.pos_angle, 4)}.")
            
            self.check_moving()
    
    def pick_move_or_shoot(self):
        # if random.randint(0, 1):
        if True:    
            self.moving = False
            self.targeting = True
        else:
            self.targeting = False
            self.moving = True
            self.pick_position()

    def pick_target(self, _tanks):
        """ Pick a target amongst list of tanks """
        # for now, pick first tank
        return _tanks[0]

    def make_choices(self, _tanks):
        if not self.player_tank:
            if self.moving and not self.chambered_ball:
                self.move_to_position_target()
            elif self.targeting:
                if not self.chambered_ball:
                    self.chamber_ball()
                    # self.simple_target()
                    self.quick_target(self.pick_target(_tanks))
                if self.chambered_ball:
                    self.check_targeting()
                else:
                    print(f"\nERROR:  {self.name} can't chamber a ball!")
            else:
                self.pick_move_or_shoot()

            if self.moving and self.chambered_ball:
                print(f"\nERROR:  {self.name} attempting to move with a chambered ball!")
            
