# Code for projectile

import pygame, math, random, numpy, time, os, copy
import settings, cosmos

def check_tanks(tanks, _settings):
    destroyed_tanks = []
    
    if tanks:
        for tank in tanks[:]:
            
            tank.snail_animation()

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
        
        # *** EFFECTS ***
        # Holds information for animations that are non-"physical",
        # such as spell animations
        self.effect_pixies = []

        # *** STUFF FOR SPELLS ***
        self.spell_cooldown = False
        self.spell_timer = False
        self.spell_active = False

        # for shield spell
        self.invulnerable = False
        self.Spell_shield_frames = False

        # for gravity spell
        self.orig_homeworld_mass = self.homeworld.mass
        self.heavy_mass = self.homeworld.mass
        self.Spell_gravity_frames = False
        
        # for ice spell
        self.Spell_ice_frames = [False, False]
        
        self.snail_color = False
        self.walking_frames = False
        self.firing_frames = False
        self.dying_frames = False
        self.ball_frames = False
        self.spellbook_frames = False
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
        self.Spell_shield = settings.SPELL_SHIELD
        self.Spell_gravity = settings.SPELL_GRAVITY
        self.Spell_ice = settings.SPELL_ICE

        # AI variables
        self.angle_guess = self.launch_angle
        self.speed_guess = self.launch_speed
        self.pos_target = self.pos_angle

        self.target = False
        self.tolerance = settings.DEFAULT_AI_TOLERANCE
        self.restrict_movement = False
        self.fire_weight = settings.DEFAULT_AI_FIRE_WEIGHT
        self.spell_weight = settings.DEFAULT_AI_SPELL_WEIGHT
        # timer to slow down AI tank
        self.start_wait = 0

        self.screen_displacement = settings.DEFAULT_SNAIL_DISPLACEMENT_FACTOR*self.homeworld.screen_rad
     
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
            self.total_balls += 1
            self.chambered_ball = True
            self.balls[-1].set_xy(self.x, self.y)
            self.fix_launch_velocity()
            [self.balls[-1].vx, self.balls[-1].vy] = self.get_launch_velocity()
            self.balls[-1].chambered = True
            self.balls[-1].name = f"{self.name}'s Cannonball #{self.total_balls}"

            self.balls[-1].color = self.color
            self.balls[-1].flash_colors = self.ball_flash_colors

            # code to load sprite frames for new cannonball
            self.balls[-1].set_frames(self.ball_frames)
            self.balls[-1].animate_repeat = True
            self.balls[-1].pix = False

            if self.snail_color:
                self.set_frames(self.firing_frames)
                self.fix_snail_pix()
                self.animate = True
                self.animate_repeat = False
                self.frame_wait = 1/2
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
            self.fix_snail_pix()
            self.animate = False
            self.animate_repeat = True
                    
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
                        ball.pix_frame = 0
                        ball.load_frame()
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
                self.angle_guess = self.pos_angle + math.pi/4
            else:
                self.angle_guess = self.pos_angle - math.pi/4
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
            R = self.homeworld.radius
            rads_away = cosmos.angle_between(self.target.pos_angle, self.pos_angle)
            d = abs(rads_away)*R
            v = self.launch_speed
            g = settings.GRAV_CONST * self.homeworld.mass / (R**2)
            vp = v / math.sqrt(R*g)

            radical = (1/4)*(1 - (2-vp**2)*vp**2)
            if radical > 0:
                radical = (d/(2*R) + 1)*math.sqrt(radical)
                if radical < 1 and radical > -1:
                    launch_angle = math.asin(radical)

                    if rads_away > 0:
                        self.angle_guess = self.pos_angle + math.pi/2 - launch_angle
                    else:
                        self.angle_guess = self.pos_angle - math.pi/2 + launch_angle

                    if self.angle_guess > 2*math.pi:
                        self.angle_guess = self.angle_guess % (2*math.pi)
                    if self.angle_guess < 0:
                        self.angle_guess = 2*math.pi + self.angle_guess

                    guessed = True
        else:
            self.pick_launch_angle()
        
        return guessed
  
    def guess_launch_speed(self):
        guessed = False
        if self.target:
            rads_away = cosmos.angle_between(self.target.pos_angle, self.pos_angle)
            R = self.homeworld.radius
            d = abs(rads_away)  *R
            g = settings.GRAV_CONST * self.homeworld.mass / (R**2)
            self.launch_speed = math.sqrt( g*d / (d/(2*R) + 1 ) )
            guessed = True
        else:
            self.pick_launch_speed()
        
        return guessed
        
    def simple_target(self):
        self.pick_launch_angle()
        self.pick_launch_speed()

    def quick_target(self):
        # self.pick_launch_speed()
                    
        self.guess_launch_speed()
        if not self.guess_launch_angle():
            if self.sts.debug:
                self.sts.write_to_log(
                    f"{self.name} couldn't find a firing solution, ejecting ball...")
            self.eject_ball()

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
            if self.check_spell_ready():
                self.Spell_raise_shields()
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
            if self.check_spell_ready():
                self.Spell_raise_shields()
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
                if random.uniform(0,1) < self.spell_weight and self.check_spell_ready():
                    if self.clear_skies(_tanks):
                        if self.sts.debug:
                            self.sts.write_to_log(
                                f"{self.name} saw no celestials or cannonballs above their heads and is casting Gravity...")
                        self.Spell_raise_gravity(_tanks)
                else:
                    self.chamber_ball()
                    self.simple_target()
                    # self.quick_target()
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
 
    def move_CCW(self):
        self.pos_angle += self.radian_step
        self.get_surface_pos()
        self.reset_default_launch()
        if self.snail_color:
            if self.moving_CW:
                self.moving_CW = False
            self.next_frame()
            self.fix_snail_pix()
        if not self.moving:
            self.moving = True
            self.moving_CW = False
            if self.snail_color:
                self.set_frames(self.walking_frames)
                self.fix_snail_pix()
                self.animate_repeat = True
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
            self.fix_snail_pix()
        if not self.moving:
            self.moving = True
            if self.snail_color:
                self.set_frames(self.walking_frames)
                self.fix_snail_pix()
                self.animate_repeat = True
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
            # Frames for Snails
            self.walking_frames = self.load_frames_to(
                os.path.join(path_to_frames, "Walking"))
            self.firing_frames = self.load_frames_to(
                os.path.join(path_to_frames, "Firing"))
            self.dying_frames = self.load_frames_to(
                os.path.join(path_to_frames, "Dying"))
            # Frames for Snails' Cannonballs
            self.ball_frames = self.load_frames_to(
                os.path.join(path_to_frames, "Cannonball"))
            
            # Load Spell frames
            self.Spell_shield_frames = self.load_frames_to(
                os.path.join(path_to_frames, "Spells/Shield"))
            self.Spell_gravity_frames = self.load_frames_to(
                os.path.join(path_to_frames, "Spells/Gravity") )
            self.Spell_ice_frames[0] = self.load_frames_to(
                os.path.join(settings.ICE_PATH, "Form") )
            self.Spell_ice_frames[1] = self.load_frames_to(
                os.path.join(settings.ICE_PATH, "Break") )
            
            # Spellbook animation frames
            self.spellbook_frames = self.load_frames_to(
                settings.SPELLBOOK_PATH)
            
            
    def fix_snail_pix(self):
        self.pix_flip = [self.moving_CW, False]
        self.pix_rotate = self.pos_angle - math.pi/2
        self.displace_pix(
            self.screen_displacement, (self.homeworld.screen_x, self.homeworld.screen_y) )

    def fix_pix_to_snail(self, pixie):
        return_pixie = pygame.transform.scale(pixie, (2*self.screen_rad, 2*self.screen_rad))

        rads = self.pos_angle - math.pi/2
        deg_rot = rads * 180 / math.pi
        return_pixie = pygame.transform.rotate(return_pixie, deg_rot)

        return return_pixie

    def snail_animation(self):
        if self.animate and isinstance(self.pix_frames, list) and not self.animation_finished:
            if ( time.time() - self.frame_timer) > self.frame_wait:
                self.next_frame()
                self.fix_snail_pix()
                self.frame_timer = time.time()

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

    def check_spell_ready(self):
        
        if not self.spell_cooldown or self.spell_active or ( (
            time.time() - self.spell_cooldown) > settings.DEFAULT_SPELL_COOLDOWN_TIME ):
            
            spell_ready = True

        else:
            
            spell_ready = False

        return spell_ready
        
    def check_spells(self, _tanks):
        
        pixies_to_remove = []

        if len(self.effect_pixies) > 0:
                for pixie in self.effect_pixies:
                    pixie.animation()

        # Special case for shields:
        if self.invulnerable:
            if ( time.time() - self.spell_timer ) > settings.DEFAULT_SPELL_TIME or not self.spell_active:
                self.spell_active = False
                self.invulnerable = False
                self.frozen = False
                self.remove_effect_pixie("spellbook")
                self.set_frames(self.walking_frames)
                self.fix_snail_pix()
                self.animate = False
                self.animate_repeat = True
                
                self.spell_cooldown = time.time()
                if not self.player_tank:
                    self.pick_move_or_shoot(_tanks)

        for pixie in self.effect_pixies:
            # For gravity spell...
            if "gravity" in pixie.name.lower():
                              
                if self.spell_active:
                    if pixie.name.lower() == "gravity-rising":
                        # increase mass
                        self.homeworld.mass = self.orig_homeworld_mass + (
                            settings.DEFAULT_GRAVITY_INCREASE - 1)*self.orig_homeworld_mass*(
                                (time.time() - self.spell_timer)/settings.DEFAULT_SPELL_TIME )            
                        # scale sprites
                        pixie.screen_rad = self.homeworld.screen_rad*( 
                            (time.time() - self.spell_timer)/settings.DEFAULT_SPELL_TIME )
                        # pixie.scale_pix_to_body_circle()

                        if ( time.time() - self.spell_timer ) > settings.DEFAULT_SPELL_TIME:
                            pixie.name = "gravity-steady"
                            self.spell_timer = time.time()
                    
                    elif pixie.name.lower() == "gravity-steady":
                        if ( time.time() - self.spell_timer ) > settings.DEFAULT_SPELL_TIME:
                            self.heavy_mass = self.homeworld.mass
                            pixie.name = "gravity-lowering"
                            self.spell_timer = time.time()
                    
                    elif pixie.name.lower() == "gravity-lowering":
                        # decrease mass
                        self.homeworld.mass = self.heavy_mass - (
                            settings.DEFAULT_GRAVITY_INCREASE - 1)*self.orig_homeworld_mass*(
                                (time.time() - self.spell_timer)/settings.DEFAULT_SPELL_TIME )            
                        
                        pixie.screen_rad = self.homeworld.screen_rad - self.homeworld.screen_rad*( 
                            (time.time() - self.spell_timer)/settings.DEFAULT_SPELL_TIME )

                        if ( time.time() - self.spell_timer ) > settings.DEFAULT_SPELL_TIME:
                            pixies_to_remove.append(pixie)
                            self.homeworld.mass = self.orig_homeworld_mass
                            if not self.dying:
                                self.frozen = False
                            self.remove_effect_pixie("spellbook")
                            self.spell_cooldown = time.time()
                            self.spell_active = False
                            if not self.player_tank:
                                self.pick_move_or_shoot(_tanks)

                else:
                    self.homeworld.mass = self.orig_homeworld_mass
                  
                    pixie.screen_rad -= self.homeworld.screen_rad*0.01
                    if pixie.screen_rad < 0:
                        pixie.screen_rad = 0
                        pixies_to_remove.append(pixie)
                        self.spell_cooldown = time.time()
                        self.remove_effect_pixie("spellbook")
                        if not self.dying:
                            self.frozen = False
                            if not self.player_tank:
                                self.pick_move_or_shoot(_tanks)
        
            elif "ice" in pixie.name.lower():
                if self.spell_active:
                    for _tank in _tanks:
                        if _tank.name in pixie.name:
                            _tank.frozen = True
                    
                    if ( time.time() - self.spell_timer ) > settings.DEFAULT_SPELL_TIME:
                        for _tank in _tanks:
                            if _tank.name in pixie.name:
                                _tank.frozen = False
                                pixie.name = f"{_tank.name} thawing"
                        
                        pixie.set_frames(self.Spell_ice_frames[1])
                        pixie.frame_wait = 1/10
                        if not self.pixie_exists("ice"):
                            self.spell_active = False
                        self.spell_cooldown = time.time()
                        self.remove_effect_pixie("spellbook")
                        if not self.dying:
                            self.frozen = False
                            if not self.player_tank:
                                self.pick_move_or_shoot(_tanks)
                else:
                    for _tank in _tanks:
                        if _tank.name in pixie.name:
                            _tank.frozen = False
                            pixie.name = f"{_tank.name} thawing"
                    pixie.set_frames(self.Spell_ice_frames[1])
                    pixie.frame_wait = 1/60
                    self.spell_cooldown = time.time()
                    self.remove_effect_pixie("spellbook")
                    if not self.dying:
                        self.frozen = False
                        if not self.player_tank:
                            self.pick_move_or_shoot(_tanks) 
            elif "thawing" in pixie.name.lower():
                if pixie.animation_finished:
                    pixies_to_remove.append(pixie)

        # Clean up dead spells and effects:
        for pixie in pixies_to_remove:
            if self.sts.debug:
                self.sts.write_to_log(f"Deleting effect pixie {pixie.name}...")
            self.effect_pixies.remove(pixie)

    def check_dying(self):
        if self.dying:
            if not self.first_death:
                self.first_death = True
                self.frozen = True
                self.spell_active = False
                self.animate = True
                self.animate_repeat = False
                self.set_frames(self.dying_frames)
                self.fix_snail_pix()
                self.frame_wait = 1 / 10
                self.frame_timer = time.time()
                self.remove_effect_pixie("spellbook")
            elif self.animation_finished:
                self.dying = False
                self.active = False

    def Spell_raise_shields(self):
        shields_raised = False

        if self.check_spell_ready():
            self.animate = True
            self.animate_repeat = True
            self.frozen = True
            self.invulnerable = True
            self.spell_active = True
            if self.snail_color:
                self.set_frames(self.Spell_shield_frames)
                self.fix_snail_pix()
                self.animate = True
                self.frame_wait = 1 / 10
                self.frame_timer = time.time()
            
            self.read_spellbook()
            self.spell_timer = time.time()
            shields_raised = True

        return shields_raised
    
    def Spell_raise_gravity(self, _tanks):
        can_cast_gravity = True

        for _tank in _tanks:
            if len(_tank.effect_pixies) > 0:
                for spell in _tank.effect_pixies:
                    if "gravity" in spell.name.lower():
                        can_cast_gravity = False

        if self.check_spell_ready() and can_cast_gravity:
            self.effect_pixies.append(cosmos.Celestial(self.sts))
            self.effect_pixies[-1].screen_rad = 0
            self.effect_pixies[-1].set_frames(self.Spell_gravity_frames)
            self.effect_pixies[-1].animate = True
            self.effect_pixies[-1].animate_repeat = True
            self.effect_pixies[-1].name = "gravity-rising"
            self.spell_active = True
            self.frozen = True
            self.spell_timer = time.time()
            self.read_spellbook()

    def Spell_ice_counterspell(self, _tanks):
        if self.check_spell_ready():
            for _tank in _tanks:
                if _tank.name != self.name:
  
                    _tank.frozen = True
                    _tank.spell_active = False
                    _tank.cooldown_timer = time.time()

                    self.effect_pixies.append(cosmos.Celestial(self.sts))
                    self.effect_pixies[-1].name = f"ice for {_tank.name}"
                    self.effect_pixies[-1].pix_rotate = _tank.pix_rotate
                    self.effect_pixies[-1].screen_x = _tank.screen_x
                    self.effect_pixies[-1].screen_y = _tank.screen_y
                    self.effect_pixies[-1].displace_pix(
                        _tank.screen_displacement, (self.homeworld.screen_x, self.homeworld.screen_y) )
                    self.effect_pixies[-1].screen_rad = _tank.screen_rad
                    self.effect_pixies[-1].frame_wait = 1/10
                    self.effect_pixies[-1].frame_timer = time.time()        
                    self.effect_pixies[-1].set_frames(self.Spell_ice_frames[0])
                    self.effect_pixies[-1].animate = True
                    self.effect_pixies[-1].animate_repeat = False

            self.frozen = True
            self.spell_active = True
            self.read_spellbook()
            self.spell_timer = time.time()

    def remove_effect_pixie(self, pixie_to_remove):
        removed = False        
        if isinstance(pixie_to_remove, str) and len(self.effect_pixies) > 0:
            for pixie in self.effect_pixies:
                if pixie.name.lower() == pixie_to_remove.lower():
                    self.effect_pixies.remove(pixie)
                    removed = True

        return removed
    
    def pixie_exists(self, pixie_to_find):
        pixie_found = False
        if isinstance(pixie_to_find, str) and len(self.effect_pixies) > 0:
            for pixie in self.effect_pixies:
                if pixie_to_find.lower() in pixie.name.lower():
                    pixie_found = True

        return pixie_found

    def read_spellbook(self):
        
        self.effect_pixies.append(cosmos.Celestial(self.sts))
        self.effect_pixies[-1].name = "spellbook"
        self.effect_pixies[-1].pix_rotate = self.pix_rotate
        self.effect_pixies[-1].screen_x = self.screen_x
        self.effect_pixies[-1].screen_y = self.screen_y
        self.effect_pixies[-1].displace_pix(
            self.screen_displacement*2.5, (self.homeworld.screen_x, self.homeworld.screen_y) )
        self.effect_pixies[-1].screen_rad = self.screen_rad
        self.effect_pixies[-1].frame_wait = 1/30        
        self.effect_pixies[-1].set_frames(self.spellbook_frames)
        self.effect_pixies[-1].animate = True
        self.effect_pixies[-1].animate_repeat = True
           
    def clear_skies(self, _tanks):
        all_clear = True
        log_text = False
        for body in self.celestials:
            if not body.homeworld:
                # vect = body.get_vect(self.homeworld.x, self.homeworld.y)
                ang = math.atan2(body.y, body.x)
                angbtwn = abs(cosmos.angle_between(ang, self.pos_angle))

                if self.sts.debug:
                    log_text = [ 
                        f"*** {self.name} USING CLEAR SKIES FUNCTION ***",
                        f"{body.name} at ({body.x}, {body.y}), angle {ang} rads.",
                        f"{self.name} at ({self.x}, {self.y}), angle {self.pos_angle}.",
                        f"Angle Between is {angbtwn} rads." ]

                if angbtwn < math.pi/2:
                    all_clear = False
                    if self.sts.debug and isinstance(log_text, list):
                        log_text.append(
                            f"The skies are NOT clear, {self.name} shouldn't use Gravity...")
                
                if self.sts.debug and isinstance(log_text, list):
                    self.sts.write_to_log(log_text)

        for _tank in _tanks:
            for ball in _tank.balls:
                ang = math.atan2(ball.x, ball.y)
                angbtwn = abs(cosmos.angle_between(ang, self.pos_angle))
                if angbtwn < math.pi/4:
                    all_clear = False
                
        return all_clear