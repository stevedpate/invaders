#!/opt/homebrew/bin/python3
#
# Steve Pate - 2018-2020

import pygame, random

DEFAULT_ALIEN_SPEED = 400
SPEED_DROP = 30
STARTING_POSITION = 500
DEFAULT_MOVES = 60
ALIENS_PER_ROW = 10
MOVE_INCREASE = 10
BARRIER_START = 480
BARRIER_XBLOCKS = 10
BARRIER_YBLOCKS = 8
BARRIER_XSIZE = 8
BARRIER_YSIZE = 6

WHITE = (255, 255, 255)
GREEN = (78, 255, 87)
BLUE = (80, 255, 239)
PURPLE = (203, 0, 255)
RED = (237, 28, 36)
YELLOW = (241, 255, 0)

width = 800
height = 600

def display_text(screen, text, x, y, size, color):
    """Display the text passed at position (x, y) in the specified color
    """
    font = pygame.font.Font('fonts/space_invaders.ttf', size)
    text = font.render(text, True, color)
    screen.blit(text, (x, y))

def get_lr(l_or_r, vposition):
    """ We pass in Game.self.vposition and 'l' or 'r'. We return the left-most or
        right-most position, for example:
       
            get_lr('l', [0, 0, 0, 5, 5, 5, 5, 5, 5, 5]) returns 3
            get_lr('r', [5, 5, 0, 0, 0, 0, 0, 0, 0, 0]) returns 1
       
        We use this in conjunction with invader_block[] to find the left-most or right-most 
        column of invaders to determine when to switch them down and left or right.
    """
    if l_or_r == 'l':
        for i,_ in enumerate(vposition):
            if vposition[i] != 0:
                break
    else: # assume 'r'
        for i,_ in reversed(list(enumerate(vposition))):
            if vposition[i] != 0:
                break
    return i

def calc_switch(vpos_array):
    """Called to determined when to ship invaders direction
    """
    lfound = rfound = False
    left = right = 0
    
    for i in range(0, len(vpos_array) - 1):
        if not lfound and vpos_array[i] != 0:
            left = i
            lfound = True
        if not rfound and vpos_array[(i+1) * -1] != 0:
            right = len(vpos_array) - i - 1
            rfound = True
    return (left, right)

class Barrier(pygame.sprite.Sprite):
    """ This class represents the barrier. We instantiate for a single barrier.
    """

    def __init__(self, lrtop, xpos, ypos):
        super().__init__()
        self.image = pygame.Surface([BARRIER_XSIZE, BARRIER_YSIZE])
        self.image.fill((78, 255, 87))
        self.rect = self.image.get_rect()
        self.rect.centerx = lrtop + (xpos * BARRIER_XSIZE)
        self.rect.centery = BARRIER_START + (ypos * BARRIER_YSIZE)

    def update(self):
        screen.blit(self.image, self.rect)

class Bomb(pygame.sprite.Sprite):
    """
    This class represents a Invader "bomb" / laser
    """

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('images/enemylaser.png')
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.moves = 0

    def move(self):
        self.moves += 1
        if self.moves == 5:
            self.moves = 0
            self.rect.centery += 5

class Laser(pygame.sprite.Sprite):
    """
    This class represents the ship's laser
    """

    def __init__(self, vposition):
        super().__init__()
        self.image = pygame.image.load('images/laser.png')
        self.rect = self.image.get_rect()
        self.rect.centerx = vposition
        self.rect.centery = height - 30
        self.moves = 0

    def move(self):
        self.rect.centery -= 5
        self.moves += 1
        if self.moves == 1:
            self.moves = 0
            self.rect.centery -= 5

class Ship(pygame.sprite.Sprite):
    """
    This class represents the invaders
    """

    def __init__(self):
        super().__init__()
        self.ship_explode = pygame.image.load('images/ship_explode.png')
        self.ship_explode = pygame.transform.scale(self.ship_explode, (40, 35))
        self.explode_rect = self.ship_explode.get_rect()
        self.ship_image = pygame.image.load('images/ship.png')
        self.ship_image = pygame.transform.scale(self.ship_image, (40, 35))
        self.image = self.ship_image
        self.ship_hit = pygame.mixer.Sound('sounds/shipexplosion.wav')
        self.ship_hit.set_volume(0.5)
        self.rect = self.image.get_rect()
        self.rect.centerx = width / 2
        self.rect.centery = height - 30

    def kill(self):
        self.image = self.ship_explode

    def restore_image(self):
        self.image = self.ship_image

class Mystery(pygame.sprite.Sprite):
    """
    This class represents the mystery ship
    """

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('images/mystery.png')
        self.image = pygame.transform.scale(self.image, (60, 35))
        self.myfont = pygame.font.Font('fonts/space_invaders.ttf', 20)
        self.enter = pygame.mixer.Sound('sounds/mysteryentered.wav')
        self.enter.set_volume(0.5)
        self.killed = pygame.mixer.Sound('sounds/mysterykilled.wav')
        self.killed.set_volume(0.5)
        self.rect = self.image.get_rect()
        self.rect.centery = 55
        self.moves = 0
        self.hit_score = 0
        self.need_to_kill = False
        self.score_display = 0
        self.flash = 0

        # 50-50 chance of which direction the mystery ship is going in

        if random.randint(0, 1) == 0:
            self.direction = 1              # left to right
            self.rect.centerx = 0
        else:
            self.direction = -1             # right to left
            self.rect.centerx = width - 1
            
    def update(self):
        if self.hit_score == 0:
            self.moves += 1
            if self.moves == 818:
                self.moves = 0
                self.need_to_kill = True
            else:
                if self.hit_score == 0:
                    self.rect.centerx += self.direction

    def mystery_hit(self):
        self.hit_score = ['100', '150', '300'][random.randint(0,2)]
        self.image = self.myfont.render(self.hit_score, False, (255, 255, 255))
        self.rect.centerx += 5
        self.rect.centery += 2
    
    def flash_score(self, screen):
        if (self.flash % 2) == 0:
            screen.blit(self.image, self.rect)
        self.score_display += 1
        if self.score_display == 10:
            self.score_display = 0
            self.flash += 1
            if self.flash == 8:
                self.need_to_kill = True

class Invader(pygame.sprite.Sprite):
    """
    This class represents the invaders
    """

    def __init__(self, invader_type, row, column, wave):
        super().__init__()
        self.image1 = pygame.image.load('images/enemy' + str(invader_type) +
                                        '_1.png')
        self.image1 = pygame.transform.scale(self.image1, (40, 35))
        self.image2 = pygame.image.load('images/enemy' + str(invader_type) +
                                        '_2.png')
        self.image2 = pygame.transform.scale(self.image2, (40, 35))
        color = ['purple', 'blue', 'green']
        self.imageh = pygame.image.load('images/explosion'
                      + color[invader_type - 1] + '.png')
        self.imageh = pygame.transform.scale(self.imageh, (40, 35))
        self.image = self.image1
        self.which_image = 1
        self.direction = 5
        self.update_row_moves = False
        self.row_moves = DEFAULT_MOVES
        self.moves = 0
        self.hit = False
        self.column = column
        self.multiplier = 1
        self.bomb = False
    
        # Set location for the block

        self.rect = self.image.get_rect()
        self.rect.x = 10 + (column * 50)

        # this is the height of each invader. "wave" is used to determine how far
        # down the screen we start each wave first time around or after all
        # invaders have been killed and we launch a new wave.

        self.rect.y = (STARTING_POSITION / 2) + (wave * 30) - (row * 40)
        #print('(', str(self.rect.x) + ',', self.rect.y, ')')

        self.hposition = row
        self.vposition = column

    def coords(self):
        return (self.rect.x, self.rect.y)

    def update(self):
        if self.hit:
            self.kill()
        if self.which_image == 1:
            self.which_image = 2
            self.image = self.image2
        else:
            self.which_image = 1
            self.image = self.image1

        if self.direction > 0:
            d = 'R'
        else:
            d = 'L'
        if self.update_row_moves:
            x = 'Y'
        else:
            x = 'N'
        self.moves += 1
        if self.moves == self.row_moves:
            if self.update_row_moves:
                self.row_moves += MOVE_INCREASE * self.multiplier
                self.update_row_moves = False
                self.multiplier = 1
            self.moves = 0
            self.rect.y += 5
            self.direction *= -1
        else:
            self.rect.x += self.direction

    def set_to_kill(self):
        self.hit = True
        self.image = self.imageh

# The Game class. We instantiate and load everything here. After a game is over,
# everything is freed and we can start again.

class Game():
    def __init__(self):
        self.last_invader_move = pygame.time.get_ticks()
        self.speed = DEFAULT_ALIEN_SPEED
        self.left_most = 0
        self.right_most = ALIENS_PER_ROW - 1
        self.wave = 1

        # Top LH corner of the block of aliens that is moving around. We use
        # this as a base for choosing where to launch an alien bomb from.

        self.block_x = 0
        self.block_y = 140

        # Scores. See if there's a high score table and if so, load what's there.
        # There is no sanity checking of what we've read.

        self.myfont = pygame.font.Font('fonts/space_invaders.ttf', 20)
        self.title = self.myfont.render('SCORE', False, (255, 255, 255))
        self.high_score_hdr = self.myfont.render('HIGH SCORE', False, (255, 255, 255))
        self.wave_hdr = self.myfont.render('WAVE ', False, (255, 255, 255))
        self.score = 0
        file = open('high_score', 'r')
        try:
            self.high_score = int(file.read().rstrip())
        except IOError:
            self.high_score = 0
        self.game_start_high_score = self.high_score
        file.close()

        # Load and setup sounds

        self.invader_sound = 1
        self.als1 = pygame.mixer.Sound('sounds/0.wav')
        self.als1.set_volume(0.5)
        self.als2 = pygame.mixer.Sound('sounds/1.wav')
        self.als2.set_volume(0.5)
        self.fire_laser = pygame.mixer.Sound('sounds/shoot.wav')
        self.fire_laser.set_volume(0.5)
        self.explode_ship = pygame.mixer.Sound('sounds/shipexplosion.wav')
        self.explode_ship.set_volume(0.5)
        self.invader_hit = pygame.mixer.Sound('sounds/invaderkilled.wav')
        self.invader_hit.set_volume(0.5)

        # Misc stuff

        self.scroll_rate = 0

        # Load the ship and set ship attributes

        self.life_image = pygame.image.load('images/ship.png')
        self.life_image = pygame.transform.scale(self.life_image, (30, 20))
        self.rect = self.life_image.get_rect()
        self.ship_kill = False
        self.lives = 3
        self.ship_hit = 0   # set to "1" if the ship gets hit with a bomb

        # There are no lasers, invader bombs or a mystery ship at the
        # start of the game

        self.laser = False
        self.mystery = False
        self.invader_bombs = pygame.sprite.Group()
        
        # This is a group of the 'current' invaders. We will know when the
        # last one has been shot by checking to see of the group is empty.
        
        self.invaders = pygame.sprite.Group()
        
        # This is a group of every sprite - invaders, ship, laser. We use
        # if for drawing everything onto the screen once we've figure out
        # aliens hit (to be removed), bits of the barrier hit, etc
        
        self.all_sprites_list = pygame.sprite.Group()

        # Load the ship. We put it in its own group so we can do a simple
        # group collision check with the invaders group to see if they've
        # reached the ship (and thus end of the game).

        self.ship = Ship()
        self.all_sprites_list.add(self.ship)

        # Load barriers. There are 4 blocks of green-filled rectangles.

        self.barriers = pygame.sprite.Group()

        for b in range(80, 800, 200):
            for x in range(BARRIER_XBLOCKS):
                for y in range(BARRIER_YBLOCKS):
                    br = Barrier(b, x, y)
                    self.barriers.add(br)

        # Let's grab some invaders. We'll call this function every time
        # the last one dies. We pass in self.wave (1, 2, 3, ...) so we
        # can adjust the starting height (lower each time). active_columns
        # counts columns in the invader block that has invaders. We use
        # it to calculate how many bombs we drop at any one time.

        self.load_invaders(self.wave)
        self.active_columns = 10        # used to calculate # invader bombs
        self.bombs = 0

    def write_high_score(self):
        if self.score > self.game_start_high_score:
            file = open('high_score', 'w')
            file.write(str(self.score))
            file.close()

    def load_invaders(self, wave):
        """ Build the block of Invaders
        """
        self.moves = 0
        self.left_most = 0
        self.right_most = ALIENS_PER_ROW - 1
        self.vposition = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]

        if wave > 8:    # after wave 8 we don't push the new pack of invaders any lower
            wave = 8
        
        self.invader_block = [[] for y in range(5)]
        row = 0
        for invader_type in [3, 3, 2, 2, 1]:      # number = type of invader
            for column in range(ALIENS_PER_ROW):
                invader = Invader(invader_type, row, column, wave)
                self.invader_block[4 - row].append(invader)
            
                # Add the block to the list of objects
                self.invaders.add(invader)
                self.all_sprites_list.add(invader)
            row += 1

    def initial_menu(self):
        """Display the main menu and wait for a key to be pressed
        """
        my = pygame.image.load('images/mystery.png')
        my = pygame.transform.scale(my, (60, 35))
        i1 = pygame.image.load('images/enemy1_1.png')
        i1 = pygame.transform.scale(i1, (40, 35))
        i2 = pygame.image.load('images/enemy2_1.png')
        i2 = pygame.transform.scale(i2, (40, 35))
        i3 = pygame.image.load('images/enemy3_1.png')
        i3 = pygame.transform.scale(i3, (40, 35))

        y = 0
        y2 = height * -1
        while True:
            keyinput = pygame.key.get_pressed()
            if keyinput[pygame.K_ESCAPE]:
                raise SystemExit
        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
    
            if keyinput[pygame.K_RETURN]:
                break

            screen.blit(background,(0, y))
            screen.blit(background,(0, y2))
            display_text(screen, 'SPACE INVADERS', 170, 150, 45, GREEN)
            screen.blit(i1, (250, 250))
            screen.blit(i2, (250, 300))
            screen.blit(i3, (250, 350))
            screen.blit(my, (240, 400))
            display_text(screen, 'PRESS ANY KEY TO START', 200, 550, 25, GREEN)
            display_text(screen, '10 points', 350, 250, 25, PURPLE)
            display_text(screen, '20 points', 350, 300, 25, BLUE)
            display_text(screen, '30 points', 350, 350, 25, GREEN)
            display_text(screen, '????????', 350, 400, 25, RED)
            pygame.display.flip()
            if (y > height):
                y = 0
                y2 = height * -1
            else:
                y += 1
                y2 += 1

    def main_loop(self): # This is the main program loop
        done = False
        i = y = 0
        y2 = height * -1

        while not done:
            i += 1
            keyinput = pygame.key.get_pressed()
            if keyinput[pygame.K_ESCAPE]:
                pygame.quit()
                raise SystemExit
        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            # Last time around, we detected that an invader bomb hit the ship.
            # We leave the explosion for a while before we shift back to the
            # ship image again.

            if self.ship_hit:
                self.ship_hit += 1
                if self.ship_hit == 80:         # keep the explosion for 80 loops
                    self.ship.restore_image()
                    self.ship_hit = 0

            # Check to see if a key is pressed and we need to move the ship or the "fire"
            # button has been pressed. We can only do this when the ship is active (not 
            # hit by an alien bomb - see above)

            if not self.ship_hit:
                if keyinput[pygame.K_z]:
                    self.ship.rect.centerx -= 3
                    self.ship.rect.centerx = max(25, self.ship.rect.centerx)
                if keyinput[pygame.K_x]:
                    self.ship.rect.centerx += 3
                    self.ship.rect.centerx = min(width - 26, self.ship.rect.centerx)

                # Check to see if the "fire" button has been pressed and we should fire the laser
    
                if keyinput[pygame.K_SPACE] and not self.laser:
                    self.laser = Laser(self.ship.rect.centerx)
                    self.all_sprites_list.add(self.laser)
                    self.fire_laser.play()

            # Update all the invaders (swap images) XXX calling "all_sprites_list.update"
            # so not just updating invaders.
            
            time_now = pygame.time.get_ticks()
            if (time_now - self.last_invader_move) > self.speed:
                self.last_invader_move = time_now
                self.all_sprites_list.update()
                if self.invader_sound == 0:
                    self.invader_sound = 1
                    self.als2.stop()
                    self.als1.play()
                else: 
                    self.invader_sound = 0
                    self.als1.stop()
                    self.als2.play()

            # Move the ship's laser further up the screen

            if self.laser:
                self.laser.move()
                
                # Check if the laser has collided with barrier
    
                for sprite in self.barriers:
                    if pygame.sprite.collide_rect(self.laser, sprite):
                        sprite.kill()
                        self.laser.kill()
                        self.laser = False
                        break
                
                # Check if the laser has collided with an invader bomb. Make sure
                # that we will have the laser (it hasn't hit a barrier)
    
                if self.laser:
                    for bomb in self.invader_bombs:
                        if pygame.sprite.collide_rect(self.laser, bomb):
                            bomb.kill()
                            self.laser.kill()
                            self.laser = False
                            break
                
            # Check if the laser has collided with an invader. We check again
            # to make sure we still have a laser since it may have just
            # collided with a barrier and been removed (see above).
    
            if self.laser:
                for sprite in self.invaders:
                    if pygame.sprite.collide_rect(self.laser, sprite):
                        self.score += 10
                        self.invader_hit.play()
                        self.laser.kill()
                        sprite.set_to_kill()
                        self.laser = False
                        self.vposition[sprite.column] -= 1
                        if self.vposition[sprite.column] == 0:
                            #self.adjust_lr(sprite.column)
                            self.active_columns -= 1
                        break
                if self.laser and self.laser.rect.centery < 10:
                    self.laser.kill()
                    self.laser = False

            # Create new invader bombs. active_columns counts invader block columns
            # that have invaders active (non empty). We don't allow bombs from all
            # active columns at once.

            if self.bombs < (self.active_columns / 3):
                # We don't always want to launch one. Make it random.
                if random.randint(0, 100) == 1:
                    while True:
                        fire_column = random.randint(0, 9)
                        if self.vposition[fire_column] == 0: # XXX can in theory get stuck forever
                            continue
                        lowest_invader = self.vposition[fire_column] - 1
                        lowest_alien = self.invader_block[lowest_invader][fire_column]
                        break

                    bomb = Bomb(lowest_alien.rect.x + 25, lowest_alien.rect.y + 35)
                    self.invader_bombs.add(bomb)
                    self.all_sprites_list.add(bomb)
                    self.bombs += 1

            # If we have some Invader bombs, move them further down the screen
            # and see if they collide with anything.

            for bomb in self.invader_bombs:
                bomb.move()
                
                # Check to see if a bomb has collided with barrier
    
                for barrier in self.barriers:
                    if pygame.sprite.collide_rect(bomb, barrier):
                        barrier.kill()
                        bomb.kill()
                        self.bombs -= 1
                        continue
                
                # Check to see if the bomb has gone off the bottom of the screen

                if bomb.rect.centery > height:
                    bomb.kill()
                    self.bombs -= 1
                    continue

                # Check to see if the bomb has hit the ship

                if pygame.sprite.collide_rect(bomb, self.ship):
                    self.ship_kill = True
                    self.ship.kill()
                    self.explode_ship.play()
                    self.ship_hit = 1
                    self.lives -= 1
                    if self.lives == 0:
                        self.write_high_score()
                        done = True
                    bomb.kill()
                    self.bombs -= 1
        
            # Scroll the background. Clear the screen and display parts of the 
            # background image on top of each other to create a scrolling effect.

            screen.blit(background,(0, 0))
            screen.blit(background,(0, y))
            screen.blit(background,(0, y2))
            self.scroll_rate += 1
            if self.scroll_rate == 3:
                self.scroll_rate = 0
                if (y > height):
                    y = 0
                    y2 = height * -1
                else:
                    y += 1
                    y2 += 1

            # Draw all the sprites (invaders, ship, alien, lasers)

            self.all_sprites_list.draw(screen)

            # Randomly kick off a mystery ship

            if not self.mystery:
                if random.randint(0, 1000) < 1:
                    self.mystery = Mystery()
                    self.mystery.enter.play()

            # Update mystery ship progress and check for laser hit

            if self.mystery:
                if self.mystery.need_to_kill:
                    self.mystery.kill()
                    self.mystery = False
            if self.mystery:
                if self.laser:
                    if pygame.sprite.collide_rect(self.mystery, self.laser):
                        self.mystery.mystery_hit()
                        self.score += int(self.mystery.hit_score)
                        self.mystery.killed.play()
                self.mystery.update()
                if self.mystery.hit_score != 0:
                    self.mystery.flash_score(screen)
                else:
                    screen.blit(self.mystery.image, self.mystery.rect)

            # Barriers ... display them but, before we do that, we check
            # for collisions with the invaders group. If there are any
            # collisions, the barriers hit are removed.

            pygame.sprite.groupcollide(self.barriers, self.invaders, True, False)
            self.barriers.update()

            # Update the number of "lives" - icons at the top of the screen

            for i in range(0, self.lives):
                screen.blit(self.life_image, (380 + (i * 35), 12))

            # Update the scores
        
            if self.score > self.high_score:
                self.high_score = self.score
            self.sc = len(str(self.score))
            sct = '0' * (6 - len(str(self.score))) + str(self.score)
            score_text= self.myfont.render(sct, False, GREEN)
        
            hsc = len(str(self.high_score))
            hsct = '0' * (6 - len(str(self.high_score))) + str(self.high_score)
            high_score_text = self.myfont.render(hsct, False, GREEN)
            wave_text = self.myfont.render(str(self.wave), False, GREEN)
        
            screen.blit(self.title, (10, 10))
            screen.blit(score_text, (95, 10))
            screen.blit(self.high_score_hdr, (550, 10))
            screen.blit(high_score_text, (700, 10))
            screen.blit(self.wave_hdr, (250, 10))
            screen.blit(wave_text, (320, 10))
        
            # Go ahead and update the screen with what we've drawn.

            pygame.display.flip()

            # Check to see if the invaders have squashed the ship. If so,
            # we decrement the number of lives and repeat until self.lives == 0

            for sprite in self.invaders:
                if pygame.sprite.collide_rect(self.ship, sprite):
                    self.ship_kill = True
                    self.ship.kill()
                    self.lives -= 1
                    for sprite in self.invaders:
                        sprite.kill()
                    self.load_invaders(self.wave)
                    if self.lives == 0:
                        self.write_high_score()
                        done = True
                    break

            # Check to see if we've run out of invaders and need to reload!

            if not self.invaders and self.lives != 0:
                self.wave += 1
                self.load_invaders(self.wave)

# Initialize pygame and set the height and width of the screen based on 
# the background image, Display the window title. Set up sounds.

pygame.init()
pygame.font.init()
pygame.mixer.pre_init(44100, -16, 1, 4096)

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Space Invaders (escape key to exit)")
background = pygame.image.load('images/sky-background.jpg').convert()

while True:
    game = Game()           # Set everything up
    game.initial_menu()     # Display the menu and wait for return to be pressed
    game.main_loop()        # Off we go ...

pygame.quit()
