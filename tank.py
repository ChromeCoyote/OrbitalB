# Code for projectile

import pygame, math, random, numpy, time, os, scipy.optimize
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
                        del tank.balls
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

        self.name = "Snail"

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
        # virtual ball for drawing launch path
        self.virtual_ball = cosmos.Cannonball(self.sts, self.celestials)
        self.virtual_ball.name = "Virtual Cannonball"
        self.old_values = { "speed": 0, "angle": 0}
        self.launch_pixels = []
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
        self.spell_cooldown_timer = False
        self.spell_timer = False
        self.spell_active = False
        self.spellready_pix = False
        self.scroll_pix = False

        # for shield spell
        self.invulnerable = False
        self.Spell_shield_frames = False

        # for gravity spell
        self.orig_homeworld_mass = self.homeworld.mass
        self.heavy_mass = self.homeworld.mass
        self.Spell_gravity_frames = False
        
        # for ice spell
        self.Spell_ice_frames = [False, False]

        # for teleport spell
        self.Spell_teleport_frames = False

        # for meteor spell
        self.Spell_meteor_frames = [False, False, False]

        # for clone spell
        self.Spell_clone_frames = False
        
        # for fireball spell
        self.Spell_fireball_frames = {}

        # for shock spell
        self.Spell_shock_frames = False

        # for summon wolf spell
        self.Spell_wolf_frames = {
            "bite": False,
            "howl": False,
            "summon": False,
            "walk": False }

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
        self.Spell_teleport = settings.SPELL_TELEPORT
        self.Spell_meteor = settings.SPELL_METEOR
        self.Spell_clone = settings.SPELL_CLONE
        self.Spell_big_ball = settings.SPELL_BIG_BALL
        self.Spell_wolf = settings.SPELL_WOLF
        self.Spell_fireball = settings.SPELL_FIREBALL
        self.Spell_shock = settings.SPELL_SHOCK
        self.kill_self = settings.KILL_SELF

        # AI variables
        self.angle_guess = self.launch_angle
        self.speed_guess = self.launch_speed
        self.pos_target = self.pos_angle
       
        self.target = False
        self.tolerance = settings.DEFAULT_AI_TOLERANCE
        self.fire_weight = settings.DEFAULT_AI_FIRE_WEIGHT
        self.spell_weight = settings.DEFAULT_AI_SPELL_WEIGHT
        # timer to slow down AI tank
        self.start_wait = 0

        self.screen_displacement = settings.DEFAULT_SNAIL_DISPLACEMENT_FACTOR*self.homeworld.screen_rad
     
        # for angle finding function
        self.g = settings.GRAV_CONST * self.homeworld.mass / (self.homeworld.radius**2)
        self.target_surface_distance = 0
        # factor for simplification, equal to:  g*d/v^2
        self.A = 0
        # factor for simplification, equal to:  (2 - vp^2)*vp^2
        self.D = 0

    def fix_launch_velocity(self):
        if self.launch_speed < 0:
            self.launch_speed = 0
        elif self.launch_speed > self.escape_v:
            self.launch_speed = self.escape_v
        
        if self.launch_angle < 0:
            self.launch_angle = 2*math.pi + self.launch_angle
        elif self.launch_angle > (2*math.pi):
            self.launch_angle = self.launch_angle % (2*math.pi)

        if self.speed_guess < 0:
            self.speed_guess = 0
        elif self.speed_guess > self.escape_v:
            self.speed_guess = self.escape_v
        
        if self.angle_guess < 0:
            self.angle_guess = 2*math.pi + self.launch_angle
        elif self.angle_guess > (2*math.pi):
            self.angle_guess = self.angle_guess % (2*math.pi)
        
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
            self.balls[-1].frame_wait = 1/30
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
            if "-big" in found_chambered_ball.name.lower() \
            or "-fireball" in found_chambered_ball.name.lower():
                self.spell_active = False     
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

            if "-big" in found_chambered_ball.name.lower():
                self.spell_active = False
                self.spell_cooldown_timer = time.time()
            elif "-fireball" in found_chambered_ball.name.lower():
                self.spell_active = False
                self.spell_cooldown_timer = time.time()
                found_chambered_ball.fireball_frames = self.Spell_fireball_frames

            if self.sts.sound_on:
                self.sts.sounds["cannonball-fire"].play()
        
        return fire

    def move_balls(self):
        """ Move active balls """
        for ball in self.balls:
            if ball.active == True:
                ball.move(self.celestials, self.sts.tres)

    def check_balls(self, tanks):
        """ Check status of active balls """

        for ball in self.balls:
            if ball.active:
                ball.check_off_screen()
                
                if ball.stuck_to_celestial:
                    found_body = False
                    for body in self.celestials:
                        if ball.stuck_to_celestial == body:
                            found_body = True
                    if not found_body:
                        ball.stuck_to_celestial = False

                if not ball.armed and not ball.exploding:
                    if ( time.time() - ball.fuse_start ) > ball.fuse_length:
                        ball.armed = True
                        ball.animate = True
                        if "-big" in ball.name.lower():
                            ball.screen_rad = settings.DEFAULT_BALL_PIX_SCREEN_RAD * \
                                settings.DEFAULT_BIG_BALL_GROWTH
                        elif "-fireball" in ball.name.lower():
                            ball.screen_rad = 2 * settings.DEFAULT_BALL_PIX_SCREEN_RAD
                            if self.target:
                                target_unit = ball.get_vect(self.target.x, self.target.y)
                            else:
                                target_unit = (ball.vx, ball.vy)
                            ball.pix_rotate = math.atan2(target_unit[1], target_unit[0])
                        else:
                            ball.screen_rad = settings.DEFAULT_BALL_PIX_SCREEN_RAD
                        ball.pix_frame = 0
                        ball.load_frame()
                        ball.frame_timer = time.time()
                        if self.sts.sound_on:
                            self.sts.sounds["cannonball-armed"].play()
            
                        # if not ball.animate:
                        #    ball.color = settings.DEFAULT_ARMED_COLOR
                if ball.armed and ball.given_away and not ball.celestial_explosion:
                        if ( time.time() - ball.given_away_start ) > settings.DEFAULT_GIVEN_AWAY_TIME:
                            ball.explode()
                if ball.exploding:
                    if "-fireball" in ball.name.lower():
                        if ball.animation_finished:
                            ball.exploding = False
                            ball.active = False
                        elif ball.stuck_to_celestial:
                            ball.get_surface_pos()
                            ball.pix_rotate = ball.pos_angle - math.pi/2
                    elif ( time.time() - ball.explode_start ) > settings.DEFAULT_EXPLODE_TIME:
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

                # *******************************
                # *** SPECIAL FIREBALL CHECKS ***
                if "-fireball" in ball.name.lower() and ball.armed:
                    target_tank = False
                    for tank in tanks:
                        if f"[[[{tank.name.lower()}]]]" in ball.name.lower():
                            target_tank = tank
                    if target_tank:
                        target_vector = ball.get_unit(target_tank.x, target_tank.y)
                        target_vector = numpy.multiply(
                            settings.DEFAULT_FIREBALL_THRUST*self.sts.tres, target_vector)
                        ball.pix_rotate = math.atan2(target_vector[1], target_vector[0])
                        (ball.vx, ball.vy) = numpy.add(target_vector, (ball.vx, ball.vy))
                    else:
                        ball.explode()

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
    
    def find_launch_path(self):
        if self.old_values["speed"] != self.launch_speed or self.old_values["angle"] != self.launch_angle:
            self.launch_pixels = []
            self.virtual_ball.set_xy(self.x, self.y)
            self.get_screenxy()
            self.fix_launch_velocity()
            [self.virtual_ball.vx, self.virtual_ball.vy] = self.get_launch_velocity()

            # virtual_tres = self.sts.tres + self.sts.tres*(self.launch_speed / self.escape_v )
            virtual_tres = self.sts.tres

            home = [self.homeworld]

            self.virtual_ball.move(home, virtual_tres)
            self.launch_pixels.append( (self.virtual_ball.screen_x, self.virtual_ball.screen_y) )

            while not self.virtual_ball.check_hit(self.homeworld):
                self.virtual_ball.move(home, virtual_tres)
                if (self.virtual_ball.screen_x != self.launch_pixels[-1][0] \
                or self.virtual_ball.screen_y != self.launch_pixels[-1][1]):
                    self.launch_pixels.append( (self.virtual_ball.screen_x, self.virtual_ball.screen_y) )

            self.old_values["speed"] = self.launch_speed
            self.old_values["angle"] = self.launch_angle
    
    def draw_launch_path(self):
        
        if not self.frozen or not self.dying:
            # self.find_launch_path()
            # step = 1
            for pixel in self.launch_pixels:
                # if not (step % 10):
                self.sts.screen.set_at(pixel, self.color)
                # step += 1

    def set_launch_ellipse(self):
        r0 = self.get_dist(self.homeworld.x, self.homeworld.y)
        v0 = self.launch_speed
        R = self.homeworld.radius
        theta = self.launch_angle
        psi = cosmos.angle_between(self.pos_angle, theta)
        h = abs(r0*v0*math.sin(psi))
        # print(f"\n{self.name}'s h:  {h}")
        mu = settings.GRAV_CONST*self.homeworld.mass
        k = h**2/mu
        eps = (v0**2)/2 - mu/r0
        # e = (k - r0)/(r0*math.cos(theta))
        e = math.sqrt(1 + (2*eps*h**2)/mu**2)
        # print(f"\n{self.name}'s e:  {e}")
        if e < 1:
            a = k/(1 - e**2)
            # print(f"\n{self.name}'s semi-major axis:  {a}.")
            # screen_a = int(self.sts.screen_dist_scale*a)
            # print(f"\n{self.name}'s semi-major axis screen length:  {screen_a}.")
            b = math.sqrt(a*k)
            # print(f"\n{self.name}'s semi-minor axis:  {b}.")
            # screen_b = int(self.sts.screen_dist_scale*b)
            # print(f"\n{self.name}'s semi-minor axis screen length:  {screen_b}.")
            c = math.sqrt(a**2 - b**2)
            # print(f"\n{self.name}'s c:  {c}.")
            # ell_center = (self.homeworld.x - c, self.homeworld.y)
            # ell_screen_center = self.set_screenxy(ell_center[0], ell_center[1])
            # print(f"\nLeft:  {ell_screen_center[0] - screen_a}, Top:  {ell_screen_center[1] - screen_b}")
            # ell_rect = (ell_screen_center[0] - screen_b, ell_screen_center[1] - screen_a, 2**screen_b, 2*screen_a)
            # ellipse = pygame.draw.ellipse(self.sts.screen, self.color, ell_rect)
            self.launch_pixels = []
            # self.virtual_ball.set_xy(self.x, self.y)
            # self.get_screenxy()
            # self.fix_launch_velocity()
            # home = [self.homeworld]
            target_pos_angle = math.acos( (k - R)/(R*e) )
            rot_ang = cosmos.angle_between(self.pos_angle, target_pos_angle)
            if self.launch_angle < self.pos_angle:
                    rot_ang += math.pi
            ang = 0
            while ang < 2*math.pi:
                (self.virtual_ball.x, self.virtual_ball.y) = (a*math.cos(ang) - c, b*math.sin(ang))
                (self.virtual_ball.x, self.virtual_ball.y) = cosmos.rotate_vector(
                      (self.virtual_ball.x, self.virtual_ball.y), rot_ang)
                if self.launch_angle < self.pos_angle:
                    self.virtual_ball.y = -self.virtual_ball.y
                self.virtual_ball.get_screenxy()
                self.launch_pixels.append( (self.virtual_ball.screen_x, self.virtual_ball.screen_y) )
                ang += 5*self.radian_step
            
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
                    # special case for fireballs, grab frames from new host
                    # before frames destroyed with old host
                    if "-fireball" in ball.name.lower():
                        ball.explode()
                    tank.balls.append(ball)
    
    def ___give_balls___(self, tank):
        if self.balls:
            for ball in self.balls:
                if not ball.chambered:
                    ball.given_away = True
                    ball.given_away_start = time.time()
                    # special case for fireballs, grab frames from new host
                    # before frames destroyed with old host
                    if "-fireball" in ball.name.lower():
                        tank.balls.append(cosmos.Cannonball(tank.sts, tank.celestials))
                        new_ball = tank.balls[-1]
                        new_ball.name = ball.name
                        new_ball.given_away = True
                        # new_ball.given_away_start = time.time()
                        (new_ball.x, new_ball.y) = (ball.x, ball.y)
                        (new_ball.vx, new_ball.vy) = (ball.vx, ball.vy)
                        # (new_ball.screen_x, new_ball.screen_y) = (ball.screen_x, ball.screen.y)
                        new_ball.get_screenxy()
                        new_ball.active = ball.active
                        new_ball.radius = ball.radius
                        new_ball.explode_radius = ball.explode_radius
                        new_ball.set_screen_radius()
                        new_ball.pix_frame = ball.pix_frame
                        new_ball.animate = ball.animate
                        new_ball.fireball_frames = tank.Spell_fireball_frames

                        if ball.exploding:
                            new_ball.frame_wait = ball.frame_wait
                            new_ball.frame_timer = ball.frame_timer
                            new_ball.animate = True
                            
                            # new_ball.animate_repeat = False
                            
                            if ball.stuck_to_celestial:
                                new_ball.stuck_to_celestal = ball.stuck_to_celestial
                                new_ball.pix_frames = tank.Spell_fireball_frames["surface explode"]
                                new_ball.get_surface_pos()
                                new_ball.pix_rotate = new_ball.pos_angle - math.pi/2
                                new_ball.displace_pix(
                                    0.9*new_ball.screen_rad, (new_ball.stuck_to_celestial.screen_x, \
                                    new_ball.stuck_to_celestial.screen_y) )
                            else:
                                new_ball.pix_frames = tank.Spell_fireball_frames["space explode"]
                            
                            new_ball.load_frame()
                        else:
                            new_ball.explode()
                    
                    else:
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
    
    # def find_this_root(self, theta):
    #     Y = ( math.sin(2*(theta)) / math.sqrt(1-self.D*( math.cos(theta)**2 )) )  - self.A
    #     return Y

    def guess_launch_angle(self):
        guessed = False
        
        rads_away = cosmos.angle_between(self.target.pos_angle, self.pos_angle)

        if self.target and self.guess_launch_speed():
            R = self.homeworld.radius
            v = self.speed_guess
            vp = v / math.sqrt(R*self.g)

            term = (vp**2)/(2 - vp**2)
            if term <= 1 and term >= -1:
                self.angle_guess = 0.5*math.acos(term)    
                
                if rads_away > 0:
                    self.angle_guess = self.pos_angle + math.pi/2 - self.angle_guess
                else:
                    self.angle_guess = self.pos_angle - math.pi/2 + self.angle_guess
                
                self.fix_launch_velocity()

                guessed = True
            else:
                mu = settings.GRAV_CONST*self.homeworld.mass
                a = (5/4)*R
                # b = (1/2)*self.get_dist(self.target.x, self.target.y)
                self.speed_guess = math.sqrt( mu*(2/R - 1/a) )
                # self.angle_guess = math.asin(
                #     ( b/(R*self.speed_guess) )*math.sqrt(mu/a) )

                # if rads_away < 0:
                self.angle_guess = self.pos_angle - rads_away
                # else:
                #    self.angle_guess = self.pos_angle + rads_away

                self.fix_launch_velocity()

                # self.pick_launch_angle()
                # self.pick_launch_speed()
                guessed = True
        
        return guessed
  
    def guess_launch_speed(self):
        guessed = False
        
        if self.target:
            R = self.homeworld.radius
            rads_away = cosmos.angle_between(self.target.pos_angle, self.pos_angle)
            # d = self.get_dist(self.target.x, self.target.y)
            self.target_surface_distance = abs(rads_away)*R
            d = self.target_surface_distance
            self.speed_guess = math.sqrt( self.g*d / (d/(2*R) + 1 ) )
            guessed = True
        # else:
          #  self.pick_launch_speed()
        
        return guessed
        
    def simple_target(self):
        self.pick_launch_angle()
        self.pick_launch_speed()

    def quick_target(self):
        # self.pick_launch_speed()
                    
        if not self.guess_launch_angle():
            if self.sts.debug:
                self.sts.write_to_log(
                    f"{self.name} couldn't find a firing solution, ejecting ball...")
            self.eject_ball()

    def check_targeting(self, _tanks):
        angle_ready = False
        speed_ready = False

        if not self.guess_launch_angle():
            self.eject_ball()
        
        self.targeting = False
        for _tank in _tanks:
            if self.target == _tank:
                self.targeting = True
        
        if not self.targeting:
            self.eject_ball()

        if self.targeting:
            angle_between = cosmos.angle_between(self.angle_guess, self.launch_angle)
    
            if abs(angle_between) < (self.tolerance*self.radian_step):
                angle_ready = True
            if abs(self.launch_speed - self.speed_guess) < (self.tolerance*self.speed_step):
                speed_ready = True
        else:
            angle_ready = False
            speed_ready = False

        danger_pixie_here = self.check_for_pixies(_tanks)

        if angle_ready and speed_ready:
            if self.sts.debug:
                self.sts.write_to_log(f"{self.name} firing solution within tolerances, not adjusting firing solution...")
                self.sts.write_to_log(f"{self.name} attempting to fire cannonball...")
            if not self.fire_ball() and self.sts.debug:
                self.sts.write_to_log("ERROR firing cannonball, no ball chambered!")
        elif self.check_for_danger(_tanks) \
            or self.check_for_rogue_celestials() \
            or danger_pixie_here:

            self.eject_ball()
            
            if self.check_spell_ready():
                old_pos = self.pos_angle
                self.pos_angle += math.pi
                self.get_surface_pos()
                danger_balls_there = self.check_for_danger(_tanks)
                danger_bodies_there = self.check_for_rogue_celestials()
                danger_pixies_there = self.check_for_pixies(_tanks)
                self.pos_angle = old_pos
                self.get_surface_pos()
                if not danger_balls_there and not danger_bodies_there and not danger_pixies_there:
                    self.Spell_teleport_snail(_tanks)
                elif not danger_pixie_here:
                    self.Spell_raise_shields()
                else:
                    self.moving = True
                    # angle_between = cosmos.angle_between(danger_pixie_here.pos_angle, self.pos_angle)
                    # step_away = 2*settings.DEFAULT_STEP_AWAY_RAD
                    # if angle_between > 0:
                    #    self.pos_target = danger_pixie_here.pos_angle - step_away
                    #else:
                    #    self.pos_target = danger_pixie_here.pos_angle + step_away
            else:
                self.moving = True                    
                    
        elif self.targeting:
            if self.sts.debug:
                log_text = [f"Target launch speed is {self.speed_guess}, current launch speed is {self.launch_speed}."]
                log_text.append(f"Target launch angle is {self.angle_guess}, current launch angle is {self.launch_angle}.")
                if not angle_ready:
                    log_text.append(f"{self.name} Launch angle not within tolerances, adjusting firing solution...")
                if not speed_ready:
                    log_text.append(f"{self.name} Launch speed not within tolerances, adjusting firing solution...")
            if angle_between > 0 and not angle_ready:
                self.launch_angle += self.radian_step
                if self.sts.debug:
                    log_text.append(f"{self.name} adjusted targeting angle one unit CCW...")
            elif angle_between < 0 and not angle_ready:
                self.launch_angle -= self.radian_step
                if self.sts.debug:
                    log_text.append(f"{self.name} adjusted targeting angle one unit CW...")      
            elif self.launch_speed > self.speed_guess and not speed_ready:
                self.launch_speed -= self.speed_step
                if self.sts.debug:
                    log_text.append(f"{self.name} lowered launch speed one unit...")
            elif self.launch_speed < self.speed_guess and not speed_ready:
                self.launch_speed += self.speed_step
                if self.sts.debug:
                    log_text.append(f"{self.name} increased launch speed one unit...")
            if self.sts.debug:
                self.sts.write_to_log(log_text)

    def pick_position(self):
            if self.target:
                ang_btwn = cosmos.angle_between(self.target.pos_angle, self.pos_angle)
                if "mage" in self.name.lower():
                    self.pos_target = self.target.pos_angle + math.pi
                elif "archer" in self.name.lower():
                    if ang_btwn <= 0:
                        self.pos_target = self.target.pos_angle + 3*math.pi/4
                    else:
                        self.pos_target = self.target.pos_angle - 3*math.pi/4
                elif "berserker" in self.name.lower():
                    if self.target.frozen \
                    and abs(ang_btwn) < math.pi/4 \
                    and self.check_spell_ready():
                        self.pos_target = self.pos_angle
                    elif ang_btwn <= 0:
                        self.pos_target = self.target.pos_angle + math.pi/4
                    else:
                        self.pos_target = self.target.pos_angle - math.pi/4
                else:
                    if ang_btwn <= 0:
                        self.pos_target = self.target.pos_angle + math.pi/2
                    else:
                        self.pos_target = self.target.pos_angle - math.pi/2
            elif random.getrandbits(1):
                self.pos_target = random.uniform(
                    (self.pos_angle + 3*math.pi/8), (self.pos_angle + math.pi/8) )
            else:
                self.pos_target = random.uniform(
                    (self.pos_angle - 3*math.pi/8), (self.pos_angle - math.pi/8) )
            
            if self.pos_target < 0:
                self.pos_target = (2*math.pi) + self.pos_target
            if self.pos_target >= (2*math.pi):
                self.pos_target = self.pos_target % (2*math.pi)

            if self.sts.debug:
                self.sts.write_to_log(
                    f"{self.name} chose to move to {round(self.pos_target, 4)}, cururently at {round(self.pos_angle, 4)}.")
        
    def move_to_position_target(self, _tanks):
        danger_ball = self.check_for_danger(_tanks)
        danger_body = self.check_for_rogue_celestials()
        danger_pixie = self.check_for_pixies(_tanks)
        
        if self.check_spell_ready():
            for _tank in _tanks:
                if _tank.name != self.name \
                and self.get_dist(_tank.x, _tank.y) < 4*settings.DEFAULT_EXPLODE_RADIUS:
                    self.Spell_shock_strike()

        if danger_ball:
            if self.check_spell_ready():
                self.Spell_raise_shields()
            else:
                danger_angle = math.atan2(danger_ball.y, danger_ball.x)
                angle_between = cosmos.angle_between(danger_angle, self.pos_angle)
                
                step_away = settings.DEFAULT_STEP_AWAY_RAD
                if "-big" in danger_ball.name.lower() or "-fireball" in danger_ball.name.lower():
                    step_away *= 3

                if angle_between > 0:
                    self.pos_target = danger_angle - step_away
                else:
                    self.pos_target = danger_angle + step_away
        
        elif danger_pixie:
            step_away = settings.DEFAULT_STEP_AWAY_RAD
            angle_between = cosmos.angle_between(danger_pixie.pos_angle, self.pos_angle)
            if "wolf" in danger_pixie.name.lower():
                step_away = 2*settings.DEFAULT_STEP_AWAY_RAD
            elif danger_pixie.check_spell_ready():
                step_away = 2*settings.DEFAULT_STEP_AWAY_RAD
            if angle_between > 0:
                self.pos_target = danger_pixie.pos_angle - step_away
            else:
                self.pos_target = danger_pixie.pos_angle + step_away    
        
        elif danger_body:
            if self.check_spell_ready():
                old_pos = self.pos_angle
                self.pos_angle += math.pi
                self.get_surface_pos()
                danger_balls_there = self.check_for_danger(_tanks)
                danger_bodies_there = self.check_for_rogue_celestials()
                danger_pixie_there = self.check_for_pixies(_tanks)
                self.pos_angle = old_pos
                self.get_surface_pos()
                if not danger_balls_there \
                    and not danger_bodies_there \
                    and not danger_pixie_there:
                    self.Spell_teleport_snail(_tanks)
                else:
                    self.Spell_raise_shields()
            else:
                danger_angle = math.atan2(danger_body.y, danger_body.x)
                angle_between = cosmos.angle_between(danger_angle, self.pos_angle)
                if angle_between > 0:
                    self.pos_target = danger_angle - math.pi/4
                else:
                    self.pos_target = danger_angle + math.pi/4

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
        if "mage" in self.name.lower() or "archer" in self.name.lower():
            self.target = self.farthest_target(_tanks)
        elif "berserker" in self.name.lower():
            self.target= self.closest_target(_tanks)
        else:
            self.target = self.random_target(_tanks)
        
        if self.target:
            if random.uniform(0, 1) < self.fire_weight:
                if random.uniform(0, 1) < self.spell_weight and self.check_spell_ready():
                    
                    for _tank in _tanks:
                        if _tank.name != self.name:
                            ang_btwn = cosmos.angle_between(self.pos_angle, _tank.pos_angle)
                            if  _tank.check_for_danger(_tanks) or _tank.spell_active:
                                self.Spell_ice_counterspell(_tanks)
                                break
                           
                            elif abs(ang_btwn) > math.pi/2 and \
                            not self.check_for_danger(_tanks):
                                self.Spell_meteor_portal(_tanks)
                                break
                            elif self.find_first_armed_ball() == _tanks[_tanks.index(_tank)].check_for_danger(_tanks):
                                self.Spell_clone_cannonball()
                                break
                            elif self.clear_skies(_tanks):
                                if self.sts.debug:
                                    self.sts.write_to_log(
                                        f"{self.name} saw no celestials or cannonballs above their heads and is casting Gravity...")
                                self.Spell_raise_gravity(_tanks)
                            elif (self.moving_CW and ang_btwn < 0) or (not self.moving_CW and ang_btwn > 0):
                                self.Spell_summon_wolf()
                                break
                            elif self.find_first_armed_ball():
                                self.Spell_clone_cannonball()
                                break
                                                    
                else:
                    self.chamber_ball()
                    # self.simple_target()
                    self.quick_target()
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

    def random_target(self, _tanks):
        """ Pick a target amongst list of tanks """
        potential_targets = []
        return_tank = False
        for _tank in _tanks:
            if self.name != _tank.name:
                potential_targets.append(_tank)
        if len(potential_targets):
            return_tank = random.choice(potential_targets)

        return return_tank

    def closest_target(self, _tanks):
        closest_dist = 3*self.homeworld.radius
        return_tank = False
        for _tank in _tanks:
            if _tank.name != self.name:
                tank_dist = self.get_dist(_tank.x, _tank.y)
                if tank_dist < closest_dist:
                    closest_dist = tank_dist
                    return_tank = _tank

        return return_tank

    def farthest_target(self, _tanks):
        farthest_dist = 0
        return_tank = False
        for _tank in _tanks:
            if _tank.name != self.name:
                tank_dist = self.get_dist(_tank.x, _tank.y)
                if tank_dist > farthest_dist:
                    farthest_dist = tank_dist
                    return_tank = _tank

        return return_tank
    
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
            
            # *************************
            # *** LOAD SPELL FRAMES ***
            # *************************

            # sheild frames (for snail)
            self.Spell_shield_frames = self.load_frames_to(
                os.path.join(path_to_frames, settings.SHIELD_PATH))
            
            # gravity frames
            self.Spell_gravity_frames = self.load_frames_to(
                os.path.join(path_to_frames, settings.GRAVITY_PATH) )
            
            # ice frames
            self.Spell_ice_frames[0] = self.load_frames_to(
                os.path.join(settings.ICE_PATH, "Form") )
            self.Spell_ice_frames[1] = self.load_frames_to(
                os.path.join(settings.ICE_PATH, "Break") )
            
            # teleport frames
            self.Spell_teleport_frames = self.load_frames_to(settings.TELEPORT_PATH)
            
            # meteor frames
            self.Spell_meteor_frames[0] = self.load_frames_to(
                os.path.join(path_to_frames, settings.METEOR_PATH, "Portal-Opening") )
            self.Spell_meteor_frames[1] = self.load_frames_to(
                os.path.join(path_to_frames, settings.METEOR_PATH, "Portal-Steady") )
            self.Spell_meteor_frames[2] = self.load_frames_to(
                os.path.join(path_to_frames, settings.METEOR_PATH, "Portal-Closing") )
            
            # clone frames
            self.Spell_clone_frames = self.load_frames_to(settings.CLONE_PATH)
            
            # wolf frames
            self.Spell_wolf_frames["bite"] = self.load_frames_to(
                os.path.join(settings.WOLF_PATH, "Bite") )
            self.Spell_wolf_frames["howl"] = self.load_frames_to(
                os.path.join(settings.WOLF_PATH, "Howl") )
            self.Spell_wolf_frames["summon"] = self.load_frames_to(
                os.path.join(settings.WOLF_PATH, "Summon") )
            self.Spell_wolf_frames["walk"] = self.load_frames_to(
                os.path.join(settings.WOLF_PATH, "Walk") )
            
            # fireball frames
            self.Spell_fireball_frames["armed"] = self.load_frames_to(
                os.path.join(settings.FIREBALL_PATH, "Armed") )
            self.Spell_fireball_frames["space explode"] = self.load_frames_to(
                os.path.join(settings.FIREBALL_PATH, "Explode-Space") )
            self.Spell_fireball_frames["surface explode"] = self.load_frames_to(
                os.path.join(settings.FIREBALL_PATH, "Explode-Surface") )

            # shock frames
            self.Spell_shock_frames = self.load_frames_to(settings.SHOCK_PATH)

            # *** ICONS ***
            # Animated spellbook icon
            self.spellbook_frames = self.load_frames_to(settings.SPELLBOOK_PATH)
            # Spellready icon
            self.spellready_pix = self.load_pix_to(
                os.path.join(path_to_frames, settings.SPELLREADY_ICON_PATH) )
            # Scroll icon
            self.scroll_pix = self.load_pix_to(settings.SCROLL_ICON_PATH) 
            
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
        for _tank in _tanks:
            for ball in _tank.balls:
                ball_dist = self.get_dist(ball.x, ball.y)
                if "-big" in ball.name.lower() or "-fireball" in ball.name.lower():
                    ball_dist -= ball.explode_radius
                if ball_dist < danger_dist:
                    if ball.exploding or ball.armed:
                        dangerous_ball = ball
                        danger_dist = ball_dist
            
        return dangerous_ball

    def check_for_rogue_celestials(self):
        dangerous_body = False
        danger_dist = self.homeworld.radius*settings.DEFAULT_DANGER_RATIO*2
        for body in self.celestials:
            body_dist = self.get_dist(body.x, body.y)
            if body_dist < danger_dist and not body.homeworld:
                dangerous_body = body
                danger_dist = body_dist

        return dangerous_body

    def check_for_pixies(self, _tanks):
        dangerous_pixie = False
        danger_dist = self.homeworld.radius*settings.DEFAULT_DANGER_RATIO
        for _tank in _tanks:
            
            for pixie in _tank.effect_pixies:
                if "wolf" in pixie.name.lower():
                    pixie_dist = self.get_dist(pixie.x, pixie.y) - pixie.radius
                    if pixie_dist < danger_dist:
                        dangerous_pixie = pixie
                        danger_dist = pixie_dist
            
            if _tank.name != self.name:
                pixie_dist = self.get_dist(_tank.x, _tank.y)
                if _tank.check_spell_ready():
                    pixie_dist -= 4*settings.DEFAULT_EXPLODE_RADIUS
                if pixie_dist < danger_dist:
                    dangerous_pixie = _tank
                    danger_dist = pixie_dist
        
        return dangerous_pixie

    def check_spell_ready(self):
        
        cooled_down = True
        if self.spell_cooldown_timer:
            cooldown_time = time.time() - self.spell_cooldown_timer
            if cooldown_time < settings.DEFAULT_SPELL_COOLDOWN_TIME:
                cooled_down = False
        if not self.spell_active and cooled_down:
            spell_ready = True
        else:
            spell_ready = False
        
        return spell_ready
        
    def check_spells(self, _tanks):
        
        pixies_to_remove = []
        
        if len(self.effect_pixies) > 0:
            for pixie in self.effect_pixies:
                pixie.animation()
        
        if self.check_spell_ready() and not self.pixie_exists("spellready icon"):
            self.show_spellready_icon(_tanks)

        # Special case for shields:
        if self.invulnerable and not self.dying:
            if ( time.time() - self.spell_timer ) > settings.DEFAULT_SPELL_TIME or not self.spell_active:
                self.spell_active = False
                self.invulnerable = False
                self.frozen = False
                self.remove_effect_pixie("spellbook")
                self.set_frames(self.walking_frames)
                self.fix_snail_pix()
                self.animate = False
                self.animate_repeat = True
                self.spell_cooldown_timer = time.time()
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
                            # Using gravity to completion takes extra cooldown time (x3)
                            self.spell_cooldown_timer = time.time() + 2*settings.DEFAULT_SPELL_COOLDOWN_TIME
                            self.spell_active = False
                            if not self.player_tank:
                                self.pick_move_or_shoot(_tanks)

                else:
                    self.homeworld.mass = self.orig_homeworld_mass
                    pixie.screen_rad -= self.homeworld.screen_rad*0.01
                    if pixie.screen_rad < 0:
                        pixie.screen_rad = 0
                        pixies_to_remove.append(pixie)
                        self.spell_cooldown_timer = time.time()
                        self.remove_effect_pixie("spellbook")
                        if not self.dying:
                            self.frozen = False
                            if not self.player_tank:
                                self.pick_move_or_shoot(_tanks)
        
            elif "portal" in pixie.name.lower():
                if self.spell_active:
                    if pixie.name.lower() == "portal-opening" and pixie.animation_finished:
                        pixie.name = "portal-steady"
                        pixie.animate_repeat = True
                        pixie.set_frames(self.Spell_meteor_frames[1])
                        self.spell_timer = time.time()
                    
                    elif pixie.name.lower() == "portal-steady":
                         
                        if random.uniform(0,1) < self.sts.asteroid_chance:
                            self.summon_meteor( (pixie.x, pixie.y) )

                        if ( time.time() - self.spell_timer ) > settings.DEFAULT_SPELL_TIME:
                            pixie.name = "portal-closing"
                            pixie.animate_repeat = False
                            pixie.set_frames(self.Spell_meteor_frames[2])
                    
                    elif pixie.name.lower() == "portal-closing" and pixie.animation_finished:
                        pixies_to_remove.append(pixie)
                        if not self.dying:
                            self.frozen = False
                        self.remove_effect_pixie("spellbook")
                        # Using meteor to completion takes extra cooldown time (x2)
                        self.spell_cooldown_timer = time.time() + settings.DEFAULT_SPELL_COOLDOWN_TIME
                        self.spell_active = False
                        if not self.player_tank:
                            self.pick_move_or_shoot(_tanks)
                else:
                    pixie.frame_wait = 1/60 
                    if pixie.name == "portal-opening" and pixie.animation_finished:
                        pixie.name = "portal-closing"
                        pixie.set_frames(self.Spell_meteor_frames[2])
                    elif pixie.name == "portal-steady":
                        pixie.animate_repeat = False
                        pixie.name = "portal-closing"
                        pixie.set_frames(self.Spell_meteor_frames[2])
                    elif pixie.name == "portal-closing" and pixie.animation_finished:
                        pixies_to_remove.append(pixie)
                        self.spell_cooldown_timer = time.time()
                        self.remove_effect_pixie("spellbook")
                        self.remove_effect_pixie("spellready icon")
                        if not self.dying:
                            self.frozen = False
                            if not self.player_tank:
                                self.pick_move_or_shoot(_tanks)

            elif "ice" in pixie.name.lower():
                if self.spell_active:
                    for _tank in _tanks:
                        if _tank.name in pixie.name:
                            if _tank.dying:
                                pixie.name = "thawing-banish"
                                pixie.set_frames(self.Spell_ice_frames[1])
                                pixie.frame_wait = 1/10
                                if not self.pixie_exists("ice"):
                                    self.spell_active = False
                                    self.spell_cooldown_timer = time.time()
                                    self.remove_effect_pixie("spellbook")
                                    if not self.dying:
                                        self.frozen = False
                                        if not self.player_tank:
                                            self.pick_move_or_shoot(_tanks)
                            else:
                                _tank.frozen = True
                    
                    if ( time.time() - self.spell_timer ) > settings.DEFAULT_SPELL_TIME:
                        for _tank in _tanks:
                            if _tank.name in pixie.name and not _tank.dying:
                                _tank.frozen = False
                        pixie.name = "thawing-banish"
                        pixie.set_frames(self.Spell_ice_frames[1])
                        pixie.frame_wait = 1/10
                        if not self.pixie_exists("ice"):
                            self.spell_active = False
                            self.spell_cooldown_timer = time.time()
                            self.remove_effect_pixie("spellbook")
                            if not self.dying:
                                self.frozen = False
                                if not self.player_tank:
                                    self.pick_move_or_shoot(_tanks)
                else:
                    for _tank in _tanks:
                        if _tank.name in pixie.name and not _tank.dying:
                            _tank.frozen = False
                    pixie.name = "thawing-banish"
                    pixie.set_frames(self.Spell_ice_frames[1])
                    pixie.frame_wait = 1/60
                    self.spell_cooldown_timer = time.time()
                    self.remove_effect_pixie("spellbook")
                    if not self.dying:
                        self.frozen = False
                        if not self.player_tank:
                            self.pick_move_or_shoot(_tanks) 
            elif "wolf" in pixie.name.lower():
                if self.spell_active:
                    if "-summon" in pixie.name.lower():
                        if pixie.animation_finished:
                            pixie.screen_displacement = self.screen_displacement*1.5
                            pixie.set_frames(self.Spell_wolf_frames["howl"])
                            pixie.fix_snail_pix()
                            pixie.frame_wait = 1/5
                            pixie.name = "wolf-howl"
                            if self.sts.sound_on:
                                self.sts.sounds["wolf howl"].play()
                    elif "-howl" in pixie.name.lower():
                        if pixie.animation_finished:
                            pixie.set_frames(self.Spell_wolf_frames["walk"])
                            pixie.fix_snail_pix()
                            pixie.name = "wolf-walk"
                            pixie.animate_repeat = True
                            pixie.animate = False
                            pixie.frame_wait = 1/30
                            pixie.frame_timer = time.time()
                            self.spell_timer = time.time()
                    elif "-walk" in pixie.name.lower():
                        if ( time.time() - self.spell_timer ) > 10*settings.DEFAULT_SPELL_TIME:
                            pixie.name = "spirit-banish"
                            pixie.screen_displacement = self.screen_displacement*0.8
                            pixie.set_frames(self.Spell_wolf_frames["summon"])
                            pixie.fix_snail_pix()
                            pixie.frame_wait = 1/10
                            pixie.animate = True
                            pixie.animate_repeat = False
                            self.spell_active = False
                            self.spell_cooldown_timer = time.time()
                            self.remove_effect_pixie("scroll")
                        elif ( time.time() - pixie.frame_timer ) > \
                            pixie.frame_wait:

                            pixie.frame_timer = time.time()
                            if pixie.moving_CW:
                                pixie.move_CW()
                            else:
                                pixie.move_CCW()

                            for _tank in _tanks:
                                if pixie.check_hit(_tank):
                                    good_hit = False
                                    ang_btwn = cosmos.angle_between(
                                        _tank.pos_angle, pixie.pos_angle)
                                    if pixie.moving_CW:
                                        if ang_btwn <= 0:
                                            good_hit = True
                                    else:
                                        if ang_btwn >= 0:
                                            good_hit = True
                                    if good_hit:
                                        pixie.name = "wolf-bite"
                                        pixie.set_frames(self.Spell_wolf_frames["bite"])
                                        pixie.fix_snail_pix()
                                        pixie.frame_wait = 1/10
                                        pixie.animate = True
                                        pixie.animate_repeat = False
                                        break

                    elif "-bite" in pixie.name.lower():
                        if pixie.animation_finished:
                            if self.sts.sound_on:
                                self.sts.sounds["wolf bite"].play()
                            good_hit = False
                            for _tank in _tanks:
                                if pixie.check_hit(_tank):
                                    ang_btwn = cosmos.angle_between(
                                        _tank.pos_angle, pixie.pos_angle)
                                    if pixie.moving_CW:
                                        if ang_btwn <= 0:
                                            good_hit = True
                                    else:
                                        if ang_btwn >= 0:
                                            good_hit = True
                                    if good_hit:
                                        _tank.dying = True
                                        pixie.name = "spirit-banish"
                                        pixie.screen_displacement = self.screen_displacement*0.8
                                        pixie.set_frames(self.Spell_wolf_frames["summon"])
                                        pixie.fix_snail_pix()
                                        pixie.frame_wait = 1/10
                                        pixie.animate = True
                                        self.spell_active = False
                                        self.spell_cooldown_timer = time.time()
                                        self.remove_effect_pixie("scroll")
                            if not good_hit:
                                pixie.set_frames(self.Spell_wolf_frames["walk"])
                                pixie.fix_snail_pix()
                                pixie.name = "wolf-walk"
                                pixie.animate_repeat = True
                                pixie.animate = False
                                pixie.frame_wait = 1/30
                                pixie.frame_timer = time.time()
                        
                else:
                    pixie.name = f"{self.name}'s spirit-banish"
                    pixie.screen_displacement = self.screen_displacement*0.8
                    pixie.set_frames(self.Spell_wolf_frames["summon"])
                    pixie.fix_snail_pix()
                    pixie.animate = True
                    pixie.animate_repeat = False
                    pixie.frame_wait = 1/30
                    self.spell_cooldown_timer = time.time()
            elif "shock" in pixie.name.lower():
                if not pixie.animation_finished and not self.spell_active:
                    self.spell_active = True
                if pixie.animation_finished:
                    pixies_to_remove.append(pixie)
                    self.frozen = False
                    self.spell_active = False
                    self.remove_effect_pixie("spellbook")
                    self.spell_cooldown_timer = time.time()
                    if not self.player_tank:
                        self.pick_move_or_shoot(_tanks)
                else:
                    for _tank in _tanks:
                        if self.get_dist(_tank.x, _tank.y) < pixie.radius \
                        and _tank.name != self.name:
                            _tank.dying = True 
            elif "-banish" in pixie.name.lower():
                if pixie.animation_finished:
                    pixies_to_remove.append(pixie)
            elif pixie.name.lower() == "scroll":
                pixie.pix = self.scroll_pix
                pixie.pix_rotate = self.pix_rotate
                pixie.screen_x = self.screen_x
                pixie.screen_y = self.screen_y
                # pixie.screen_rad = self.screen_rad / 2
                pixie.displace_pix(
                    self.screen_displacement*2, (self.homeworld.screen_x, self.homeworld.screen_y) )
                pixie.transform_pix()
                if ( time.time() - pixie.frame_timer ) > settings.DEFAULT_SCROLL_TIME and not self.spell_active:
                    pixies_to_remove.append(pixie)
            elif pixie.name.lower() == "spellready icon":
                
                tank_count = 0
                tank_no = -1
                for _tank in _tanks:
                    tank_count += 1
                    if _tank.name == self.name:
                        tank_no = tank_count   
                
                pixie.screen_x = 2*self.screen_rad
                pixie.screen_y = self.height - (tank_no*self.screen_rad) - self.screen_rad

        # Clean up dead spells and effects:
        for pixie in pixies_to_remove:
            if self.sts.debug:
                self.sts.write_to_log(f"Deleting effect pixie {pixie.name}...")
            self.effect_pixies.remove(pixie)

    def check_dying(self):
        if self.dying:
            if not self.first_death:
                self.first_death = True
                self.invulnerable = False
                self.frozen = True
                self.spell_active = False
                self.animate = True
                self.animate_repeat = False
                self.set_frames(self.dying_frames)
                self.fix_snail_pix()
                self.frame_wait = 1 / 10
                self.frame_timer = time.time()
                self.remove_effect_pixie("spellbook")
                if self.sts.sound_on:
                    self.sts.sounds["dying"].play()
                if self.sts.debug:
                    self.sts.write_to_log(f"{self.name} is dying!")
            elif self.animation_finished:
                self.dying = False
                self.active = False
                if self.sts.debug:
                    self.sts.write_to_log(f"{self.name} had died :(")

    def Spell_raise_shields(self):
        shields_raised = False

        if self.check_spell_ready():
            self.animate = True
            self.animate_repeat = True
            self.frozen = True
            self.invulnerable = True
            self.spell_active = True
            self.remove_effect_pixie("spellready icon")
            
            if self.snail_color:
                self.set_frames(self.Spell_shield_frames)
                self.fix_snail_pix()
                self.animate = True
                self.frame_wait = 1 / 10
                self.frame_timer = time.time()
            
            self.read_spellbook()
            self.spell_timer = time.time()
            shields_raised = True

            if self.sts.sound_on:
                self.sts.sounds["cast spell"].play()

            if self.sts.debug:
                self.sts.write_to_log(f"{self.name} cast raise shield Spell!")

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
            self.effect_pixies[-1].frame_timer = time.time()
            self.effect_pixies[-1].animate = True
            self.effect_pixies[-1].animate_repeat = True
            self.effect_pixies[-1].name = "gravity-rising"
            self.spell_active = True
            self.remove_effect_pixie("spellready icon")
            self.frozen = True
            self.spell_timer = time.time()
            self.read_spellbook()
            if self.sts.sound_on:
                self.sts.sounds["cast spell"].play()

    def Spell_meteor_portal(self, _tanks):
        can_cast_meteor = True

        for _tank in _tanks:
            if len(_tank.effect_pixies) > 0:
                for spell in _tank.effect_pixies:
                    if "portal" in spell.name.lower():
                        can_cast_meteor = False
        
        if self.check_spell_ready() and can_cast_meteor:
            self.effect_pixies.append(cosmos.Celestial(self.sts))
            # The width of the portal is 150% of the homeworld radius,
            # and the screen radius is 150% of its actual radius to make it look better
            self.effect_pixies[-1].screen_rad = (
                self.homeworld.screen_rad*settings.DEFAULT_PORTAL_WIDTH)*1.5
            self.effect_pixies[-1].set_frames(self.Spell_meteor_frames[0])
            self.effect_pixies[-1].animate = True
            self.effect_pixies[-1].animate_repeat = False
            self.effect_pixies[-1].frame_wait = 1/30
            self.effect_pixies[-1].frame_timer = time.time()
            self.effect_pixies[-1].name = "portal-opening"
            self.effect_pixies[-1].x = self.x
            self.effect_pixies[-1].y = self.y

            # displace portal away from homeworld
            dist_vect = self.effect_pixies[-1].get_vect(self.homeworld.x, self.homeworld.y)
            dist_vect = numpy.multiply(50*self.sts.rad_scale, dist_vect)
            (self.effect_pixies[-1].x, self.effect_pixies[-1].y) = numpy.add(
                 (self.effect_pixies[-1].x, self.effect_pixies[-1].y), dist_vect )

            self.effect_pixies[-1].get_screenxy()
            self.effect_pixies[-1].pix_rotate = self.pix_rotate + math.pi/2
            
            self.spell_active = True
            self.remove_effect_pixie("spellready icon")
            self.frozen = True
            self.read_spellbook()
            if self.sts.sound_on:
                self.sts.sounds["cast spell"].play()

    def summon_meteor(self, portal_r):

        d_half = (settings.DEFAULT_PORTAL_WIDTH*self.homeworld.radius)
        portal_ang = self.pos_angle + math.pi/2

        if portal_ang:
            X = random.uniform(-1,1)*d_half*math.cos(portal_ang)
            Y = math.tan(portal_ang)*X
            X += portal_r[0]
            Y += portal_r[1]
        else:
            X = portal_r[0]
            Y = random.uniform(-1,1)*d_half*math.cos(portal_ang)
            Y += portal_r[1]

        self.celestials.append(cosmos.Celestial(self.sts))
        self.celestials[-1].set_attr(f"{self.name}'s summoned asteroid-{(X, Y)}", \
            False, settings.CERES_DENSITY, settings.CERES_RADIUS, (
                random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)) )
        
        self.celestials[-1].x = X
        self.celestials[-1].y = Y

        speed = math.sqrt(settings.GRAV_CONST * self.homeworld.mass / \
            self.homeworld.radius) * settings.DEFAULT_ASTEROID_SPEED
        velocity = numpy.multiply( -speed, self.get_unit(self.homeworld.x, self.homeworld.y) )

        self.celestials[-1].set_v(velocity[0], velocity[1])
        
        self.get_screenxy()
        self.celestials[-1].pick_dwarf_pix()
        
        if self.celestials[-1].sts.debug:
            self.sts.write_to_log(f"{self.celestials[-1].name} created!")
            self.celestials[-1].write_values()

    def Spell_ice_counterspell(self, _tanks):
        if self.check_spell_ready():
            for _tank in _tanks:
                if _tank.name != self.name:
                    _tank.frozen = True
                    if _tank.spell_active:
                        _tank.spell_active = False
                        _tank.spell_cooldown_timer = time.time()

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
            self.remove_effect_pixie("spellready icon")
            self.read_spellbook()
            if self.sts.sound_on:
                self.sts.sounds["cast spell"].play()
            self.spell_timer = time.time()

    def Spell_teleport_snail(self, _tanks):

        if self.check_spell_ready():
            self.effect_pixies.append(cosmos.Celestial(self.sts))
            self.effect_pixies[-1].name = f"{self.name}'s origin teleport-banish"
            self.effect_pixies[-1].pix_rotate = self.pix_rotate
            self.effect_pixies[-1].screen_x = self.screen_x
            self.effect_pixies[-1].screen_y = self.screen_y
            self.effect_pixies[-1].displace_pix(
                self.screen_displacement, (self.homeworld.screen_x, self.homeworld.screen_y) )
            self.effect_pixies[-1].screen_rad = self.screen_rad
            self.effect_pixies[-1].frame_wait = 1/30
            self.effect_pixies[-1].frame_timer = time.time()        
            self.effect_pixies[-1].set_frames(self.Spell_teleport_frames)
            self.effect_pixies[-1].animate = True
            self.effect_pixies[-1].animate_repeat = False

            self.pos_angle += math.pi
            
            if self.moving_CW:
                self.moving_CW = False
            else:
                self.moving_CW = True

            self.get_surface_pos()
            self.reset_default_launch()
            self.fix_snail_pix()
            self.load_frame()

            self.read_scroll()
            self.spell_cooldown_timer = time.time()
            self.remove_effect_pixie("spellready icon")
            if not self.player_tank:
                self.pick_move_or_shoot(_tanks)
            if self.sts.sound_on:
                self.sts.sounds["cast spell"].play()

            self.effect_pixies.append(cosmos.Celestial(self.sts))
            self.effect_pixies[-1].name = f"{self.name}'s destination teleport puff-banish"
            self.effect_pixies[-1].pix_rotate = self.pix_rotate
            self.effect_pixies[-1].screen_x = self.screen_x
            self.effect_pixies[-1].screen_y = self.screen_y
            self.effect_pixies[-1].displace_pix(
                self.screen_displacement, (self.homeworld.screen_x, self.homeworld.screen_y) )
            self.effect_pixies[-1].screen_rad = self.screen_rad
            self.effect_pixies[-1].frame_wait = 1/30
            self.effect_pixies[-1].frame_timer = time.time()        
            self.effect_pixies[-1].set_frames(self.Spell_teleport_frames)
            self.effect_pixies[-1].animate = True
            self.effect_pixies[-1].animate_repeat = False

    def find_first_armed_ball(self):
        first_ball = False
        if len(self.balls) > 0:
            for ball in self.balls:
                if ball.active \
                and ball.armed \
                and not ball.exploding \
                and not ball.given_away:
                    first_ball = ball
                    break
        
        return first_ball
    
    def Spell_clone_cannonball(self):
        
        first_ball = self.find_first_armed_ball()
        
        if self.check_spell_ready() and first_ball and "-fireball" not in first_ball.name.lower():
            self.effect_pixies.append(cosmos.Celestial(self.sts))
            self.effect_pixies[-1].name = f"{self.name}'s {first_ball.name}'s clone-banish"
            self.effect_pixies[-1].screen_x = first_ball.screen_x
            self.effect_pixies[-1].screen_y = first_ball.screen_y
            self.effect_pixies[-1].screen_rad = first_ball.screen_rad*1.5
            self.effect_pixies[-1].frame_wait = 1/10
            self.effect_pixies[-1].frame_timer = time.time()        
            self.effect_pixies[-1].set_frames(self.Spell_clone_frames)
            self.effect_pixies[-1].animate = True
            self.effect_pixies[-1].animate_repeat = False

            num_clones = settings.DEFAULT_NUM_CLONES
            
            if num_clones < 2:
                num_clones = 2
            if (num_clones % 2):
                num_clones -= 1

            spread = settings.DEFAULT_CLONE_SPREAD
            veer_rad = spread/(num_clones + 1)

            for clone_no in range( 1, (settings.DEFAULT_NUM_CLONES+1) ):
                
                if clone_no <= (num_clones/2):
                    nudge_rad = -spread/2 + (clone_no - 1)*veer_rad
                else:
                    nudge_rad = -spread/2 + (clone_no + 1)*veer_rad

                self.balls.append(cosmos.Cannonball(self.sts, self.celestials))
                self.total_balls += 1
                self.balls[-1].active = True
                self.balls[-1].armed = True
                self.balls[-1].set_xy(first_ball.x, first_ball.y)
                self.balls[-1].screen_rad = first_ball.screen_rad
                # ***************************************************************************
                [self.balls[-1].vx, self.balls[-1].vy] = \
                    cosmos.rotate_vector([first_ball.vx, first_ball.vy], nudge_rad)
                self.balls[-1].name = \
                    f"Cloned Cannonball #{clone_no}-{self.total_balls} of {first_ball.name}"

                self.balls[-1].color = self.color
                self.balls[-1].flash_colors = self.ball_flash_colors

                # code to load sprite frames for new cannonball
                self.balls[-1].set_frames(self.ball_frames)
                self.balls[-1].animate = True
                self.balls[-1].animate_repeat = True
                if self.sts.debug:
                    log_text = [f"{self.balls[-1].name} cloned by {self.name}!"]
                    log_text.append(f"Velocity set to: ({self.balls[-1].vx}, {self.balls[-1].vy}).")
                    log_text.append(f"Veclocity was rotated by {nudge_rad} radians.")
                    log_text.append(
                        f"{first_ball.name}'s velocity is:  ({first_ball.vx}, {first_ball.vy})")
                    
                    self.sts.write_to_log(log_text)
           
            self.read_scroll()
            self.remove_effect_pixie("spellready icon")
            if self.sts.sound_on:
                self.sts.sounds["cast spell"].play()

    def Spell_big_cannonball(self):

        big_ball = self.find_chambered_ball()

        if self.check_spell_ready() and big_ball:
            big_ball.explode_radius *= settings.DEFAULT_BIG_BALL_GROWTH
            big_ball.name += "-big"
            
            self.spell_active = True
            self.read_scroll()
            self.remove_effect_pixie("spellready icon")
            if self.sts.sound_on:
                self.sts.sounds["cast spell"].play()

    def Spell_homing_fireball(self, _tanks):
        
        fireball = self.find_chambered_ball()

        if self.check_spell_ready() and fireball:
            self.target = self.farthest_target(_tanks)
            fireball.fuse_length = settings.DEFAULT_FIREBALL_FUSE_TIME
            fireball.explode_radius = 3*settings.DEFAULT_EXPLODE_RADIUS
            fireball.name += f"-Fireball targeting [[[{self.target.name}]]]"
            fireball.set_frames(self.Spell_fireball_frames["armed"])
            fireball.frame_wait = 1/60
            fireball.pix = False

            self.spell_active = True
            self.read_scroll()
            # using fireball makes cooldown take longer
            self.remove_effect_pixie("spellready icon")
            if self.sts.sound_on:
                self.sts.sounds["cast spell"].play()

    def Spell_shock_strike(self):
        if self.check_spell_ready():
            self.read_spellbook()
            self.effect_pixies.append(cosmos.Celestial(self.sts))
            self.effect_pixies[-1].name = f"{self.name}'s shock"
            self.effect_pixies[-1].pix_rotate = self.pix_rotate
            self.effect_pixies[-1].screen_x = self.screen_x
            self.effect_pixies[-1].screen_y = self.screen_y
            self.effect_pixies[-1].displace_pix(
                0.25*self.screen_displacement, (self.homeworld.screen_x, self.homeworld.screen_y) )
            self.effect_pixies[-1].radius = 4*settings.DEFAULT_EXPLODE_RADIUS
            self.effect_pixies[-1].set_screen_radius()
            self.effect_pixies[-1].frame_wait = 1/30
            self.effect_pixies[-1].frame_timer = time.time()        
            self.effect_pixies[-1].set_frames(self.Spell_shock_frames)
            self.effect_pixies[-1].animate = True
            self.effect_pixies[-1].animate_repeat = False

            self.frozen = True
            self.spell_active = True
            self.remove_effect_pixie("spellready icon")

    def Spell_summon_wolf(self):

        if self.check_spell_ready():
            self.effect_pixies.append(Tank(self.sts, self.celestials))
            self.effect_pixies[-1].name = f"{self.name}'s wolf-summon"
            self.effect_pixies[-1].snail_color = self.snail_color
            self.effect_pixies[-1].pix_rotate = self.pix_rotate

            if not self.moving_CW:
                self.effect_pixies[-1].pos_angle = self.pos_angle + settings.DEFAULT_STEP_AWAY_RAD
            else:
                self.effect_pixies[-1].pos_angle = self.pos_angle - settings.DEFAULT_STEP_AWAY_RAD      
            self.effect_pixies[-1].get_surface_pos()
            self.effect_pixies[-1].moving_CW = self.moving_CW
            self.effect_pixies[-1].radius = settings.DEFAULT_EXPLODE_RADIUS*3
            self.effect_pixies[-1].set_screen_radius()
            self.effect_pixies[-1].screen_displacement = self.screen_displacement*0.8
            self.effect_pixies[-1].fix_snail_pix()             
            # self.effect_pixies[-1].screen_rad = self.screen_rad*1.5
        
            self.effect_pixies[-1].frame_wait = 1/10      
            self.effect_pixies[-1].set_frames(self.Spell_wolf_frames["summon"])
            self.effect_pixies[-1].animate = True
            self.effect_pixies[-1].animate_repeat = False

            self.spell_active = True
            self.read_scroll()
            self.remove_effect_pixie("spellready icon")
            if self.sts.sound_on:
                self.sts.sounds["cast spell"].play()

    def remove_effect_pixie(self, pixie_to_remove):
        removed = False        
        if isinstance(pixie_to_remove, str) and len(self.effect_pixies) > 0:
            for pixie in self.effect_pixies[:]:
                if pixie.name.lower() == pixie_to_remove.lower():
                    self.effect_pixies.remove(pixie)
                    removed = not self.pixie_exists(pixie_to_remove)
                    if self.sts.debug:
                        if removed:
                            self.sts.write_to_log(
                                f"Successfully removed {pixie_to_remove} from {self.name}'s effect list!")
                        else:
                            self.sts.write_to_log(
                                f"ERROR:  failed to remove {pixie_to_remove} from {self.name}'s effect list!")
        return removed
    
    def pixie_exists(self, pixie_to_find):
        pixie_found = False
        if isinstance(pixie_to_find, str) and len(self.effect_pixies) > 0:
            for pixie in self.effect_pixies:
                if pixie_to_find.lower() in pixie.name.lower():
                    pixie_found = pixie

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

    def read_scroll(self):
        
        self.effect_pixies.append(cosmos.Celestial(self.sts))
        self.effect_pixies[-1].name = "scroll"
        self.effect_pixies[-1].pix_rotate = self.pix_rotate
        self.effect_pixies[-1].screen_x = self.screen_x
        self.effect_pixies[-1].screen_y = self.screen_y
        self.effect_pixies[-1].displace_pix(
            self.screen_displacement*2, (self.homeworld.screen_x, self.homeworld.screen_y) )
        self.effect_pixies[-1].screen_rad = (self.screen_rad / 2)
        self.effect_pixies[-1].pix = self.scroll_pix
        self.effect_pixies[-1].transform_pix()
        self.effect_pixies[-1].frame_timer = time.time()

    def show_spellready_icon(self, _tanks):
        if not self.pixie_exists("spellready icon"):
            self.effect_pixies.append(cosmos.Celestial(self.sts))
            self.effect_pixies[-1].name = "spellready icon"
            self.effect_pixies[-1].screen_rad = self.screen_rad
            self.effect_pixies[-1].pix = self.spellready_pix
            self.effect_pixies[-1].transform_pix()
           
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