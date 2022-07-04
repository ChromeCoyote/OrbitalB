# Code for projectile

import pygame, math, random, numpy, time, os
import settings, cosmos

def check_tanks(tanks, _settings):
    destroyed_tanks = []
    
    if tanks:
        for tank in tanks[:]:
            
            dying_frame = tank.snail_animation()

            if tank.invulnerable:
                if ( time.time() - tank.shield_timer ) > settings.DEFAULT_SHIELD_TIME:
                    tank.invulnerable = False
                    tank.frozen = False
                    tank.shield_cooldown = time.time()
                    tank.set_frames(tank.walking_frames)
                    tank.fix_snail_frame()
                    tank.animate = False
                    if not tank.player_tank:
                        tank.pick_move_or_shoot(tanks)
            
            if tank.dying:
                if not tank.first_death:
                    tank.first_death = True
                    tank.frozen = True
                    tank.animate = True
                    tank.set_frames(tank.dying_frames)
                    tank.load_frame(0)
                    tank.fix_snail_frame()
                    tank.frame_wait = 1 / 10
                    tank.frame_timer = time.time()
                elif dying_frame == ( len(tank.pix_frames) - 1):
                        tank.dying = False
                        tank.active = False

            if not tank.active:
                if _settings.debug:
                    _settings.write_to_log(f"{tank.name} being destroyed...")    
                if tank.balls:
                    if tank != tanks[0]:
                    # give destroyed tank's balls to first tank's balls
                        tank.give_balls(tanks[0])
                        if _settings.debug:
                            _settings.write_to_log(f"Cannonballs from {tank.name} given to {tanks[0].name}'s cannonball list.")
                    elif tank != tanks[-1]:
                    # give destroyed tank's balls to last tank's balls
                        tank.give_balls(tanks[-1])
                        if _settings.debug:
                            _settings.write_to_log(f"Cannonballs from {tank.name} given to {tanks[-1].name}'s ball list.")
                    else:
                        if _settings.debug:
                            _settings.write_to_log(f"Only one tank left, can't give cannonballs away!")
                destroyed_tanks.append(tank)
                tanks.remove(tank)
                if _settings.debug:
                    _settings.write_to_log(f"Tank successfully destroyed!")
        
        if not destroyed_tanks:
            destroyed_tanks = False
    else:
        destroyed_tanks = False

    return destroyed_tanks
 
class Tank (cosmos.Celestial):
    """ Class for surface roaming tanks """

    def __init__(self, sts, celestials):
        """ Initialize variables for tank """
        super().__init__(sts)

        self.name = "Player Tank"

        self.radius = 0.1            # 100 m meter radius
        
        self.homeworld = False       # not the homeworld ;)
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
        # self.num_balls = 0
        self.total_balls = 0

        self.player_tank = True     # default player tank
        self.winner = False         # not a winner yet!

        self.moving = False
        self.moving_CW = False
        self.targeting = False
        self.frozen = False
        
        self.dying = False
        self.first_death = False
        
        self.invulnerable = False
        self.shield_timer = False
        self.shield_cooldown = False

        self.snail_color = False
        self.walking_frames = False
        self.firing_frames = False
        self.dying_frames = False
        self.ball_frames = False
        self.shield_frames = False

        self.ball_flash_colors = False

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
        self.eject_ball_key = settings.EJECT_BALL
        self.activate_shields = settings.ACTIVATE_SHIELDS

        # AI variables
        self.angle_guess = self.launch_angle
        self.speed_guess = self.launch_speed
        self.pos_target = self.pos_angle

        self.target = False
        self.tolerance = settings.DEFAULT_AI_TOLERANCE
        self.restrict_movement = False
        self.fire_weight = settings.DEFAULT_AI_FIRE_WEIGHT
        # timer to slow down AI tank
        self.start_wait = 0

        self.displacement_factor = settings.DEFAULT_SNAIL_DISPLACEMENT_FACTOR
     
        # orbital constant
        if self.homeworld:
            self.mu = settings.GRAV_CONST*self.homeworld.mass
        else:
            self.mu = 0

    def fix_launch_velocity(self):
        if self.launch_speed < 0:
            self.launch_speed = 0
        elif self.launch_speed > self.escape_v:
            self.launch_speed = self.escape_v
        
        if self.launch_angle < 0:
            self.launch_angle = 0
        elif self.launch_angle > (2*math.pi):
            self.launch_angle = self.launch_angle % (2*math.pi)
        
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
        if self.pos_angle < 0:
            self.pos_angle = 2*math.pi + self.pos_angle
        if self.pos_angle > (2*math.pi):
            self.pos_angle = self.pos_angle % (2*math.pi)
        
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
            self.targeting = True
            self.moving = False
            self.balls.append(cosmos.Cannonball(self.sts, self.celestials))
            # self.num_balls = len(self.balls)    # set number of balls counted in balls list
            self.total_balls += 1
            self.chambered_ball = True
            self.balls[-1].set_xy(self.x, self.y)
            self.fix_launch_velocity()
            [self.balls[-1].vx, self.balls[-1].vy] = self.get_launch_velocity()
            self.balls[-1].chambered = True
            self.balls[-1].name = f"{self.name}'s Cannonball #{self.total_balls}"

            self.balls[-1].color = self.color
            self.balls[-1].flash_colors = self.ball_flash_colors

            # code to load sprite frames
            self.balls[-1].set_frames(self.ball_frames)
            self.balls[-1].pix = False

            if self.snail_color:
                self.set_frames(self.firing_frames)
                self.load_frame(0)
                self.fix_snail_frame()
                self.animate = True
                self.frame_wait = 1/3
                self.frame_timer = time.time()

            chamber_success = True

        return chamber_success

    def find_chambered_ball(self):
        
        found_chambered_ball = False
        
        for ball in self.balls:
            if ball.chambered:
                found_chambered_ball = ball

        if not found_chambered_ball:
            self.chambered_ball = False
    
        return found_chambered_ball
                        
    def eject_ball(self):
        found_chambered_ball = self.find_chambered_ball()
        if found_chambered_ball:
            self.balls.remove(found_chambered_ball)
            self.chambered_ball = False
            self.targeting = False
            self.set_frames(self.walking_frames)
            self.fix_snail_frame()
            self.animate = False
                    
    def fire_ball(self):
        """ Fire chambered cannonball """
        fire = False
        found_chambered_ball = self.find_chambered_ball()

        if found_chambered_ball:        # if a ball is chambered...
            self.chambered_ball = False         # set chamber to empty
            found_chambered_ball.chambered = False   # set chambered ball's status to not so
            found_chambered_ball.active = True       # set chambered ball to active
            [found_chambered_ball.vx, found_chambered_ball.vy] = self.get_launch_velocity()
            [found_chambered_ball.x, found_chambered_ball.y] = (self.x, self.y)
            found_chambered_ball.get_screenxy()
            found_chambered_ball.fuse_start = time.time()
            
            self.targeting = False
            fire = True
        
        return fire

    def move_balls(self):
        """ Move active balls """
        for ball in self.balls:
            if ball.active == True:
                ball.move(self.celestials)
                ball.check_off_screen()
    
    def check_balls(self, tanks):
        """ Check status of active balls """

        for ball in self.balls[:]:
            if ball.active:
                ball.check_off_screen()
                if not ball.armed and not ball.exploding:
                    if ( time.time() - ball.fuse_start ) > settings.DEFAULT_FUSE_TIME:
                        ball.armed = True
                        ball.animate = True
                        ball.screen_rad = settings.DEFAULT_BALL_PIX_SCREEN_RAD
                        ball.load_frame(0)
                        ball.frame_timer = time.time()
            
                        # if not ball.animate:
                        #    ball.color = settings.DEFAULT_ARMED_COLOR
                if ball.armed and ball.given_away and not ball.celestial_explosion:
                        if ( time.time() - ball.given_away_start ) > settings.DEFAULT_GIVEN_AWAY_TIME:
                            ball.explode()
                if ball.exploding:
                    if ( time.time() - ball.explode_start ) > settings.DEFAULT_EXPLODE_TIME:
                        ball.exploding = False
                        ball.active = False
                        if self.sts.debug:
                            self.sts.write_to_log(
                                f"{ball.name} explosion timer has expired, marked for removal...")
                    else:
                        if ball.stuck_to_celestial:
                            ball.get_surface_pos()
                        if not ball.celestial_explosion:
                            ball.expand()
                            ball.flash()

                ball.animation()               
                ball.check_impact(tanks)
                
                # if self.sts.debug and ball.celestial_explosion:
                #    ball.write_ball_values()
            
        for ball in self.balls:
            if not ball.active and not ball.chambered:
                self.balls.remove(ball)

    def detonate_ball(self):
        blew_up = False
        for ball in self.balls:
            if ball.active and ball.armed and not blew_up and not ball.given_away:
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

    def write_tank_values(self):
        """Print properties of tank"""
        printx = 0
        printy = 0
        tank_text = []
        super().write_values()
        tank_text.append("ADDITIONAL INFORMATION FOR TANK:")
        tank_text.append(f"The tanks's launch angle is {self.launch_angle} radians.")
        tank_text.append(f"The tank's launch speed is {self.launch_speed}.")
        (printx, printy) = self.get_launch_velocity()
        tank_text.append(f"The tank's launch velocity is ({printx, printy}).")
        (printx, printy) = self.draw_launch_v()
        tank_text.append(f"The tip of the launch vector on screen should be:  <{printx, printy}>.")

    def display_ball_stats(self):
        ball_text = []
        ball_text.append(f"INFORMATION FOR {self.name}'s CANNONBALLS:")
        ball_text.append(f"Cannonballs in memory for {self.name}:  {len(self.balls)}.")
        ball_text.append(f"Total cannonballs fired or chambered for {self.name}:  {self.total_balls}.")
        self.sts.write_to_log(ball_text)
        ball_number = 0
        for ball in self.balls:
            ball_number += 1
            (f"{self.name}'s CANNONBALL #{ball_number} OF {len(self.balls)}:")
            ball.write_ball_values()

    def check_smush(self, body):
        if not body.homeworld and super().check_hit(body):
            self.dying = True
            if self.sts.debug:
                self.sts.write_to_log(f"{self.name} has been smushed by {body.name}!")

    def give_balls(self, tank):
        if self.balls:
            for ball in self.balls:
                if not ball.chambered:
                    ball.given_away = True
                    ball.given_away_start = time.time()
                    tank.balls.append(ball)
    
    def pick_launch_angle(self):
        if self.target:
            ang_bwn = cosmos.angle_between(self.target.pos_angle, self.pos_angle)
            if ang_bwn > 0:
                self.angle_guess = self.pos_angle + math.pi/3
            else:
                self.angle_guess = self.pos_angle - math.pi/3
        else:
            if random.getrandbits(1):
                self.angle_guess = random.uniform(
                    (self.pos_angle + 3*math.pi/8), (self.pos_angle + math.pi/8) )
            else:
                self.angle_guess = random.uniform(
                    (self.pos_angle - 3*math.pi/8), (self.pos_angle - math.pi/8) )
    
    def pick_launch_speed(self):
        if self.target:
            self.speed_guess = \
                settings.SIMPLE_SPEED_GUESS_HIGHER*self.escape_v * \
                    math.sqrt( self.get_dist(self.target.x, self.target.y)/(2*self.homeworld.radius) )
        else:
            self.speed_guess = random.uniform(
                settings.SIMPLE_SPEED_GUESS_LOWER*self.escape_v, settings.SIMPLE_SPEED_GUESS_HIGHER*self.escape_v)
    
    def guess_launch_angle(self):
        guessed = False
        if self.target:
            radical_factor = self.mu / (self.homeworld.radius * self.launch_speed**2)
            if radical_factor >= 0:
                radical_factor = math.sqrt(radical_factor)
                if radical_factor <= 1 and radical_factor >= -1:
                    self.angle_guess = math.asin(radical_factor)
                    if self.angle_guess < 0:
                        self.angle_guess = 2*math.pi + self.angle_guess
                    if self.angle_guess > (2*math.pi):
                        self.angle_guess = self.angle_guess % (2*math.pi)
                    guessed = True
            else:
                self.pick_launch_angle()
        
        return guessed
  
    def guess_launch_speed(self):
        guessed = False
        if self.target:
            if self.pos_angle and self.launch_angle:
                radical_factor = self.mu / (self.homeworld.radius * (math.sin(self.launch_angle)) ** 2)
            else:
                radical_factor = 0
            if radical_factor > 0:
                self.speed_guess = math.sqrt(radical_factor)
                guessed = True
            else:
                self.pick_launch_speed()
        
        return guessed
        
    def simple_target(self):
        self.pick_launch_angle()
        self.pick_launch_speed()

    def quick_target(self):
        self.pick_launch_speed()
        if not self.guess_launch_angle():
            if not self.guess_launch_speed():
                if self.sts.debug:
                    self.sts.write_to_log(
                        f"{self.name} couldn't find a firing solution, ejecting ball...")
                self.eject_ball()
                self.target = False

    def check_targeting(self, _tanks):
        angle_ready = False
        speed_ready = False

        angle_between = cosmos.angle_between(self.angle_guess, self.launch_angle)
    
        if abs(angle_between) < (self.tolerance*self.radian_step):
            angle_ready = True
        if abs(self.launch_speed - self.speed_guess) < (self.tolerance*self.speed_step):
            speed_ready = True

        if angle_ready and speed_ready:
            if self.sts.debug:
                self.sts.write_to_log(f"{self.name} firing solution within tolerances, not adjusting firing solution...")
                self.sts.write_to_log(f"{self.name} attempting to fire cannonball...")
            if not self.fire_ball() and self.sts.debug:
                self.sts.write_to_log("ERROR firing cannonball, no ball chambered!")
        elif self.check_for_danger(_tanks):
            self.eject_ball()
            if self.check_shields_ready():
                self.raise_shields()
        elif self.targeting:
            if self.sts.debug and not angle_ready:
                self.sts.write_to_log(f"{self.name} Launch angle not within tolerances, adjusting firing solution...")
            if self.sts.debug and not speed_ready:
                if self.sts.debug and not angle_ready:
                    self.sts.write_to_log(f"{self.name} Launch speed not within tolerances, adjusting firing solution...")
            if angle_between > 0 and not angle_ready:
                    self.launch_angle += self.radian_step
                    if self.sts.debug:
                        self.sts.write_to_log(f"{self.name} adjusted targeting angle one unit CCW...")
            elif angle_between < 0 and not angle_ready:
                self.launch_angle -= self.radian_step
                if self.sts.debug:
                        self.sts.write_to_log(f"{self.name} adjusted targeting angle one unit CW...")      
            elif self.launch_speed > self.speed_guess and not speed_ready:
                self.launch_speed -= self.speed_step
                if self.sts.debug:
                    self.sts.write_to_log(f"{self.name} lowered launch speed one unit...")
            elif self.launch_speed < self.speed_guess and not speed_ready:
                self.launch_speed += self.speed_step
                if self.sts.debug:
                    self.sts.write_to_log(f"{self.name} increased launch speed one unit...")

    def pick_position(self):
            if random.getrandbits(1):
                self.pos_target = random.uniform(
                    (self.pos_angle + 3*math.pi/8), (self.pos_angle + math.pi/8) )
            else:
                self.pos_target = random.uniform(
                    (self.pos_angle - 3*math.pi/8), (self.pos_angle - math.pi/8) )
            
            if self.pos_target < 0:
                self.pos_target = (2*math.pi) + self.pos_target
            if self.pos_target >= (2*math.pi):
                self.pos_target = self.pos_target % (2*math.pi)
            
            if self.restrict_movement:
                if self.pos_target < math.pi and self.pos_target > math.pi/2:
                    self.pos_target = math.pi
                elif self.pos_target > 0 and self.pos_target < math.pi/2:
                    self.pos_target = 0

            if self.sts.debug:
                self.sts.write_to_log(
                    f"{self.name} chose to move to {round(self.pos_target, 4)}, cururently at {round(self.pos_angle, 4)}.")
        
    def move_to_position_target(self, _tanks):
        danger_ball = self.check_for_danger(_tanks)
        
        if danger_ball:
            if self.check_shields_ready():
                self.raise_shields()
            else:
                danger_angle = math.atan2(danger_ball.y, danger_ball.x)
                angle_between = cosmos.angle_between(danger_angle, self.pos_angle)
                if angle_between > 0:
                    self.pos_target = danger_angle - math.pi/8
                else:
                    self.pos_target = danger_angle + math.pi/8
        
        angle_between = cosmos.angle_between(self.pos_target, self.pos_angle)

        if abs(angle_between) < self.tolerance*self.radian_step:
            self.moving = False
        elif angle_between > 0:
            self.move_CCW()
            if self.sts.debug:
                self.sts.write_to_log(f"{self.name} moved one unit CCW...")
        elif angle_between < 0:
            self.move_CW()
            if self.sts.debug:
                self.sts.write_to_log(f"{self.name} moved one unit CW...")

    def pick_move_or_shoot(self, _tanks):
        self.pick_target(_tanks)
        if self.target:
            if random.uniform(0, 1) < self.fire_weight:
                self.chamber_ball()
                self.simple_target()
                if self.sts.debug:
                    self.sts.write_to_log(f"{self.name} chose to shoot...")
            else:
                self.targeting = False
                self.pick_position()
                self.move_to_position_target(_tanks)
                if self.sts.debug:
                    self.sts.write_to_log(f"{self.name} chose to move...")
        elif self.check_for_danger(_tanks):
            self.pos_target = random.uniform(0, 2*math.pi)
            self.move_to_position_target(_tanks)
        else:
            self.moving = False
            self.targeting = False
            self.detonate_ball()
            if self.chambered_ball:
                self.eject_ball()
            if self.sts.debug:
                self.sts.write_to_log(
                    f"No targets for {self.name}, chose to back down...")

    def pick_target(self, _tanks):
        """ Pick a target amongst list of tanks """
        potential_targets = []
        for _tank in _tanks:
            if self.name != _tank.name:
                potential_targets.append(_tank)
        if len(potential_targets):
            self.target = random.choice(potential_targets)
        else:
            self.target = False
 
    def make_choices(self, _tanks):
        if not self.player_tank:
            if ( time.time() - self.start_wait) > settings.DEFAULT_AI_WAIT_TIME:
                if self.moving:
                    self.move_to_position_target(_tanks)
                elif self.targeting:
                    if self.sts.debug:
                        self.sts.write_to_log(f"{self.name} is checking targeting info...")
                    self.check_targeting(_tanks)
                else:
                    self.pick_move_or_shoot(_tanks)

                if self.moving and self.chambered_ball:
                    self.eject_ball()
                    if self.sts.debug:
                        self.sts.write_to_log(f"ERROR:  {self.name} attempting to move with a chambered ball!")
                
                self.start_wait = time.time()
    
    def displace_pix_from_homeworld(self):
        displace_vector = numpy.subtract(
            (self.screen_x, self.screen_y), (self.homeworld.screen_x, self.homeworld.screen_y) )
        displace_vector = numpy.multiply(self.displacement_factor, displace_vector)
        self.pix_offset_x = int(displace_vector[0])
        self.pix_offset_y = int(displace_vector[1])
 
    def move_CCW(self):
        self.pos_angle += self.radian_step
        self.get_surface_pos()
        self.reset_default_launch()
        if self.snail_color:
            if self.moving_CW:
                self.moving_CW = False
            self.next_frame()
            self.fix_snail_frame()
        if not self.moving:
            self.moving = True
            self.moving_CW = False
            if self.snail_color:
                self.set_frames(self.walking_frames)
                self.fix_snail_frame()
                self.animate = False
        # self.get_screenxy()

    def move_CW(self):
        self.pos_angle -= self.radian_step
        self.get_surface_pos()
        self.reset_default_launch()
        # self.get_screenxy()
        if self.snail_color:
            if not self.moving_CW:
                self.moving_CW = True
            self.next_frame()
            self.fix_snail_frame()
        if not self.moving:
            self.moving = True
            if self.snail_color:
                self.set_frames(self.walking_frames)
                self.fix_snail_frame()
                self.animate = False
            
    def load_snail_frames(self):
        if self.snail_color.lower() == "green":
            path_to_frames = os.path.join(settings.SNAILS_PATH, "Green_Snail")
            self.ball_flash_colors = settings.DEFAULT_GREEN_SNAIL_FLASH_COLORS
            snail_success = True
        elif self.snail_color.lower() == "red":
            path_to_frames = os.path.join(settings.SNAILS_PATH, "Red_Snail")
            self.ball_flash_colors = settings.DEFAULT_RED_SNAIL_FLASH_COLORS
            snail_success = True
        elif self.snail_color.lower() == "yellow":
            path_to_frames = os.path.join(settings.SNAILS_PATH, "Yellow_Snail")
            self.ball_flash_colors = settings.DEFAULT_YELLOW_SNAIL_FLASH_COLORS
            snail_success = True
        else:
            snail_success = False
            if self.sts.debug:
                self.sts.write_to_log(
                    f"Invalid color {self.snail_color} used in tank.load_snail_frames() for {self.name}.")
        
        if snail_success:
            self.walking_frames = self.load_frames_to(
                os.path.join(path_to_frames, "Walking"))
            self.firing_frames = self.load_frames_to(
                os.path.join(path_to_frames, "Firing"))
            self.dying_frames = self.load_frames_to(
                os.path.join(path_to_frames, "Dying"))
            self.ball_frames = self.load_frames_to(
                os.path.join(path_to_frames, "Cannonball"))
            self.shield_frames = self.load_frames_to(
                os.path.join(path_to_frames, "Shielded"))
            
    def fix_snail_frame(self):
        self.scale_pix_to_body_circle()
        if self.moving_CW:
            self.flip_pix(self.moving_CW, False)
        self.rotate_pix( self.pos_angle - math.pi/2 )
        self.displace_pix_from_homeworld()

    def snail_animation(self):
        if self.animate and isinstance(self.pix_frames, list):
            if ( time.time() - self.frame_timer) > self.frame_wait:
                self.next_frame()
                self.fix_snail_frame()
                self.frame_timer = time.time()
        
        return self.pix_frame

    def check_for_danger(self, _tanks):
        dangerous_ball = False
        danger_dist = self.homeworld.radius*settings.DEFAULT_DANGER_RATIO
        if not self.player_tank:
            for _tank in _tanks:
                for ball in _tank.balls:
                    ball_dist = self.get_dist(ball.x, ball.y)
                    if ball_dist < danger_dist:
                        if ball.exploding or ball.armed:
                            dangerous_ball = ball
                            danger_dist = ball_dist

        return dangerous_ball

    def check_shields_ready(self):
        if not self.shield_cooldown or ( (
            time.time() - self.shield_cooldown) > settings.DEFAULT_SHIELD_COOLDOWN_TIME ):
            
            shields_ready = True
        else:
            shields_ready = False

        return shields_ready
        
    def raise_shields(self):
        shields_raised = False

        if self.check_shields_ready():
            self.animate = True
            self.frozen = True
            self.invulnerable = True
            self.shield_timer = time.time()
            if self.snail_color:
                self.set_frames(self.shield_frames)
                self.load_frame(0)
                self.fix_snail_frame()
                self.animate = True
                self.frame_wait = 1 / 10
                self.frame_timer = time.time()
            
            shields_raised = True

        return shields_raised
        