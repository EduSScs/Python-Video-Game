import pygame, time, random, os
#from SpaceShip import SpaceShip
pygame.init()   
pygame.font.init()

# Setting up Display
SCREEN_SIZE = 1000
WINDOW = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption('Space Attack')

# Get Background
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join('Content', 'space_background.png')), (SCREEN_SIZE, SCREEN_SIZE))

# Get Spaceships Images
PLAYER_SHIP = pygame.image.load(os.path.join('Content', 'player_spaceship.png'))
PURPLE_ALIEN = pygame.image.load(os.path.join('Content', 'purple_alien.png'))
BLUE_SHIP = pygame.image.load(os.path.join('Content', 'blue_ship.png'))
RED_SHIP = pygame.image.load(os.path.join('Content', 'red_ship.png'))
ASTEROID = pygame.image.load(os.path.join('Content', 'asteroid.png'))
# Laser Images

BLAST = pygame.image.load(os.path.join('Content', 'blast.png'))
ALIEN_SPIT = pygame.image.load(os.path.join('Content', 'alien_spit.png'))
ENEMY_FIRE = pygame.image.load(os.path.join('Content', 'enemy_fire.png'))
RED_LASER = pygame.image.load(os.path.join('Content', 'pixel_laser_red.png'))
YELLOW_LASER = pygame.image.load(os.path.join('Content', 'pixel_laser_yellow.png'))

class SpaceShip:
    CD = 15
    def __init__(self, x, y, hit_points=100):
        self.x = x
        self.y = y
        self.hit_points = hit_points
        self.space_ship_sprite = None
        self.laser_sprite = None
        self.shoot_cd = 0
        self.current_lasers = []

    def create(self, window):
        WINDOW.blit(self.space_ship_sprite,(self.x,self.y))
        for laser in self.current_lasers:
            laser.create(window)

    def laser_motion(self, speed, user):
        self.cd()
        for laser in self.current_lasers:
                laser.motion(speed)
                if laser.out_of_bounds(SCREEN_SIZE):
                    self.current_lasers.remove(laser)
                elif laser.collide(user):
                    user.hit_points -= 10
                    self.current_lasers.remove(laser)

    def cd(self):
        if self.shoot_cd >= self.CD:
            self.shoot_cd = 0
        elif self.shoot_cd > 0:
            self.shoot_cd += 1

    def fire(self):
        if self.shoot_cd == 0:
            laser = Laser(self.x, self.y, self.laser_sprite)
            self.current_lasers.append(laser)
            self.shoot_cd = 1

    def height(self):
        return self.space_ship_sprite.get_height()

    def width(self):
        return self.space_ship_sprite.get_width()

class Laser:
    def __init__ (self, x, y, sprite):
        self.x = x
        self.y = y
        self.sprite = sprite
        self.mask = pygame.mask.from_surface(self.sprite)

    def create(self, window):
        WINDOW.blit(self.sprite, (self.x, self.y))

    def motion(self, speed):
        self.y += speed

    def collide(self, obj):
        return crash(self, obj)
        
    def out_of_bounds(self, height):
        return self.y >= height or self.y <= 0

# We get the difference of the top left pixel from the object called to the laser
# Then we check for an overlap of the first obj mask with the second obj given the distance between them
# If theres any intersection we return True because there is an result
def crash (obj, obj2):
    diff_x = obj2.x - obj.x
    diff_y = obj2.y - obj.y
    return obj.mask.overlap(obj2.mask, (diff_x, diff_y)) != None

class Attacker(SpaceShip):
    COLORS = {
        'purple' : (PURPLE_ALIEN, ALIEN_SPIT),
        'blue' : (BLUE_SHIP, ENEMY_FIRE),
        'asteroid' : (ASTEROID, None),
        'red' : (RED_SHIP, ENEMY_FIRE)
    }
    def __init__(self, x, y, color, hit_points=100):
        super().__init__(x, y, hit_points)
        self.space_ship_sprite, self.laser_sprite = self.COLORS[color]
        self.mask = pygame.mask.from_surface(self.space_ship_sprite)
    
    def motion(self, speed):
        if (self.space_ship_sprite==ASTEROID):
            self.y += speed+2
        else:
            self.y += speed
    
    def fire(self):
        if self.shoot_cd == 0:
            if (self.space_ship_sprite==PURPLE_ALIEN):
                laser = Laser(self.x-12, self.y, self.laser_sprite)
            elif (self.space_ship_sprite==BLUE_SHIP or self.space_ship_sprite==RED_SHIP):
                laser = Laser(self.x+17, self.y+18, self.laser_sprite)
            elif (self.space_ship_sprite==ASTEROID):
                laser = Laser(0, -100, BLAST)
            else:
                laser = Laser(self.x-12, self.y, self.laser_sprite)
            self.current_lasers.append(laser)
            self.shoot_cd = 1

class  User(SpaceShip):
    CD = 10
    def __init__(self, x, y, hit_points=100):
        super().__init__(x, y, hit_points)
        self.laser_sprite = BLAST
        self.space_ship_sprite = PLAYER_SHIP
        self.mask = pygame.mask.from_surface(self.space_ship_sprite)
        self.max_hit_points = hit_points

    def laser_motion(self, speed, enemies):
        self.cd()
        for laser in self.current_lasers:
            laser.motion(speed)
            if laser.out_of_bounds(SCREEN_SIZE):
                self.current_lasers.remove(laser)
            else:
                for enemy in enemies:
                    if laser.collide(enemy):
                        enemies.remove(enemy)
                        self.current_lasers.remove(laser)
    
    def fire(self):
        if self.shoot_cd == 0:
            laser = Laser(self.x+22, self.y-25, self.laser_sprite)
            self.current_lasers.append(laser)
            self.shoot_cd = 1


def main():
    game_running = True
    fail = False
    lost_time = 0
    fail_font = pygame.font.SysFont('arial', 80)
    game_font = pygame.font.SysFont('arial', 40)
    lives = 3
    level = 0
    FPS = 30
    speed = 6
    laser_speed = 7
    clock = pygame.time.Clock()
    spaceship = User(300, 650)
    enemies = []
    num_enemies = 3
    enemies_speed = 2
    possible_colors = ['purple', 'blue', 'asteroid', 'red']

    def update_display():
        WINDOW.blit(BACKGROUND, (0,0))
        show_level = game_font.render('Level: '+str(level), 1, (0, 255, 0))
        WINDOW.blit(show_level, (5, 5))
        show_lives = game_font.render('Lifes: '+str(lives), 1, (255, 0, 0))
        WINDOW.blit(show_lives, (SCREEN_SIZE-5-show_lives.get_width(), 5))
        pygame.draw.rect(WINDOW, (255, 0, 0), (spaceship.x, spaceship.y + spaceship.height()+5, spaceship.width(), 8))
        pygame.draw.rect(WINDOW, (0, 255, 0), (spaceship.x, spaceship.y + spaceship.height()+5, spaceship.width()*(spaceship.hit_points/spaceship.max_hit_points), 8))
        spaceship.create(WINDOW)
        for enemy in enemies:
            enemy.create(WINDOW)
        
        if fail:
            fail_message = fail_font.render('Game Over', 1, (255, 0, 0))
            WINDOW.blit(fail_message, (SCREEN_SIZE/2-fail_message.get_width()/2, SCREEN_SIZE/2))

        pygame.display.update()



    while game_running:
        clock.tick(FPS)

        update_display()

        if spaceship.hit_points <= 0 or lives <= 0:
            fail = True
            lost_time += 1
        
        if fail:
            if lost_time > FPS * 5:
                game_running = False
            else:
               continue
            

        if len(enemies)==0:
            num_enemies +=7
            level += 1
            for x in range(num_enemies):
                enemy = Attacker(random.randint(10, SCREEN_SIZE-50), random.randint(-1000, -50), random.choice(possible_colors))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

# Returns a dictionary with all the buttons being pressed currently
        buttons = pygame.key.get_pressed()
        if buttons[pygame.K_SPACE]:
            spaceship.fire()
        if (buttons[pygame.K_UP] or buttons[pygame.K_w]) and spaceship.y-speed>0:
            spaceship.y -= speed*2
        if (buttons[pygame.K_DOWN] or buttons[pygame.K_s]) and spaceship.y+speed+spaceship.height()<SCREEN_SIZE:
            spaceship.y += speed*2
        if (buttons[pygame.K_LEFT] or buttons[pygame.K_a]) and spaceship.x-speed>0:
            spaceship.x -= speed*2
        if (buttons[pygame.K_RIGHT] or buttons[pygame.K_d]) and spaceship.x+speed+spaceship.width()<SCREEN_SIZE:
            spaceship.x += speed*2

        for enemy in enemies:
            enemy.motion(enemies_speed)
            enemy.laser_motion(laser_speed, spaceship)

            if crash(enemy, spaceship):
                enemies.remove(enemy)
                spaceship.hit_points -= 10
            elif random.randint(0, 180)==0:
                enemy.fire()

            if enemy.y+enemy.height()>SCREEN_SIZE:
                enemies.remove(enemy)
                if enemy.space_ship_sprite != ASTEROID:
                    lives -= 1
        
        spaceship.laser_motion(-laser_speed, enemies)

def tittle_screen():
    tittle_font = pygame.font.SysFont('arial', 60)
    while True:
        WINDOW.blit(BACKGROUND, (0,0))
        tittle = tittle_font.render('Press The Space Bar To Start', 1, (255, 255, 255)) 
        WINDOW.blit(tittle, (SCREEN_SIZE/2-tittle.get_width()/2, SCREEN_SIZE/2-tittle.get_height()/2))
        pygame.display.update()
        pressing = pygame.key.get_pressed()
        for event in pygame.event.get():
            if pressing[pygame.K_SPACE]:
                main()
            if event.type == pygame.QUIT:
                quit()

tittle_screen()