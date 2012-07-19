#!/usr/bin/env python

import os
import classes
import time
import pygame
from pygame.locals import *
from ui import UserInterface
from ui import StatusBar


##
# This class defines the PyGame/SDL UI frontend
##
class SDLUserInterface(UserInterface):
    # Colors Names
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)

    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)

    AQUA = (0, 255, 255)
    FUCHSIA = (255, 0, 255)
    LIME = (0, 255, 0)
    MAROON = (128, 0, 0)
    NAVY_BLUE = (0, 0, 128)
    OLIVE = (128, 128, 0)
    PURPLE = (128, 0, 128)
    SILVER = (192, 192, 192)
    TEAL = (0, 128, 128)

    # Colors Associations
    CHR_COLOR_PLAYER = BLACK
    CHR_COLOR_ENEMY = RED
    CHR_COLOR_WIZARD = BLUE
    CHR_COLOR_ARCHER = WHITE
    CHR_COLOR_DEAD = PURPLE
    CHR_COLOR_BACKGROUND = GREEN

    # Labels (Do we want them?)
    CHR_TXT_PLAYER = "S"
    CHR_TXT_ENEMY = "B"
    CHR_TXT_ENEMY_DEAD = "X"
    CHR_TXT_WIZARD = "W"
    CHR_TXT_ARCHER = "A"
    CHR_TXT_DEAD = "D"

    # Sounds
    SND_DIR="assets"
    SUCCESS="victory.mp3"
    FAIL="bomb.mp3"

    FREQ = 48000   # same as audio CD
    BITSIZE = -16  # unsigned 16 bit
    CHANNELS = 2   # 1 == mono, 2 == stereo
    BUFFER = 1024  # audio buffer size in no. of samples

    # Sizes
    STATUSBAR_HEIGHT = 30
    FONT_SIZE = 25
    CHR_SIZE = 20

    # Frames per Second
    FRAME_RATE = 25

    # Directions
    DIRECTIONS = {
        K_RIGHT: "right",
        K_LEFT: "left",
        K_DOWN: "down",
        K_UP: "up"
    }

    def __init__(self, game_handler, width=60, height=22):
        super(SDLUserInterface, self).__init__(game_handler, width, height)

        # Define the coordinates for each main area
        # ------------------------------------------
        # | Top Status Bar                         |
        # ------------------------------------------
        # |                                        |
        # |                                        |
        # |                                        |
        # |                                        |
        # |                                        |
        # |             Game Map                   |
        # |                                        |
        # |                                        |
        # |                                        |
        # |                                        |
        # |                                        |
        # |                                        |
        # ------------------------------------------
        # | Bottom Status Bar                      |
        # ------------------------------------------

        # Topbar coords
        topbar_x = 0
        topbar_y = 0

        # Map coords
        map_x = 0
        map_y = topbar_x + SDLUserInterface.STATUSBAR_HEIGHT

        # Map Size
        map_width = width * SDLUserInterface.CHR_SIZE
        map_height = height * SDLUserInterface.CHR_SIZE

        # Bottombar coords
        bottombar_x = 0
        bottombar_y = map_y + map_height

        # Main Window Size
        window_height = SDLUserInterface.STATUSBAR_HEIGHT * 2 + map_height
        window_width = map_width

        # Initialize PyGame
        pygame.init()
        pygame.display.set_caption('Hello Game')

        # Set up the sounds
        pygame.mixer.init(SDLUserInterface.FREQ,
                        SDLUserInterface.BITSIZE,
                        SDLUserInterface.CHANNELS,
                        SDLUserInterface.BUFFER)
        self.level_completed_sound = pygame.mixer.Sound(os.path.join(SDLUserInterface.SND_DIR,
                                        SDLUserInterface.SUCCESS))
        self.level_completed_sound.set_volume(0.5)
        self.game_over_sound = pygame.mixer.Sound(os.path.join(SDLUserInterface.SND_DIR,
                                        SDLUserInterface.FAIL))
        self.game_over_sound.set_volume(0.5)

        self.clock = pygame.time.Clock()

        # We don't want to use the mouse (... yet)
        pygame.mouse.set_visible(0)

        # Setup the font to be used for the statusbars
        basicFont = pygame.font.SysFont(None, SDLUserInterface.FONT_SIZE)

        # Build the Main Window
        self.windowSurface = pygame.display.set_mode((window_width,
                                window_height),
                                0, 32)

        # Build the WorldMap
        self.world_map = SDLWorldMap(self.windowSurface,
                            width, height, map_x, map_y)

        # Build the topbar
        self.topbar = SDLTopBar(basicFont,
                        self.windowSurface,
                        self.world_map,
                        bar_width = window_width,
                        pos_x=topbar_x,
                        pos_y=topbar_y)

        # Build the bottombar
        self.bottombar = SDLBottomBar(basicFont,
                            self.windowSurface,
                            self.world_map,
                            bar_width = window_width,
                            pos_x=bottombar_x,
                            pos_y=bottombar_y)

    def draw_window(self):
        self.windowSurface.fill(SDLUserInterface.CHR_COLOR_BACKGROUND)
        self.topbar.show()
        self.world_map.print_map()
        self.bottombar.show()
        pygame.display.update()

    def set_statusbar_character(self, character):
        self.bottombar.set_character(character)

    def set_status(self, msg):
        self.bottombar.set_message(msg)
        self.draw_window()

    def get_student(self):
        return self.student

    def add_student(self, attributes):
        student = SDLPlayer(self, attributes)
        self.student = student
        student.show()
        self.world_map.add_character(self.student)

    def add_engineer(self, attributes):
        wizard = SDLWizard(self, attributes)
        self.engineer = wizard
        wizard.show()
        self.world_map.add_character(self.engineer)

    def add_enemy(self, attributes):
        bug = SDLEnemy(self, attributes)
        self.bugs.append(bug)
        bug.show()
        self.world_map.add_character(bug)

    def mainloop(self):
        while True:
            tickFPS = self.clock.tick(SDLUserInterface.FRAME_RATE)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.game_handler.quit_game()
                elif event.type == KEYDOWN:
                    if event.key in (K_LEFT, K_RIGHT, K_UP, K_DOWN):
                        self.student.move(SDLUserInterface.DIRECTIONS[event.key])
                        for bug in self.bugs:
                            bug.act(self.student,
                                    SDLUserInterface.DIRECTIONS)
                    elif event.key == K_x:
                        self.game_handler.quit_game()
                    elif event.key == K_a:
                        for bug in self.bugs:
                            self.student.attack(bug)
                            bug.act(self.student,
                                    SDLUserInterface.DIRECTIONS)

            if self.exit_loop() == True:
                print "Exiting the loop"
                break


    def notify_level_finished(self):
        print "Yay!"
        self.level_completed_sound.play()
        self.set_status("Level Completed!")
        pygame.time.delay(3 * 1000)

    def notify_game_over(self):
        print "Doh!"
        self.game_over_sound.play()
        self.set_status("GAME OVER!")
        pygame.time.delay(3 * 1000)
        
##
# Canvas / Layout classes
##
class SDLStatusBar(StatusBar):
    def __init__(self, basicFont, windowSurface, world_map,
            bar_width, pos_x=0, pos_y=0,
            character=None):
        super(SDLStatusBar, self).__init__(character)

        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = bar_width
        self.basic_font = basicFont
        self.world_map = world_map
        self.windowSurface = windowSurface
        self.rect = pygame.Rect(self.pos_x, self.pos_y,
                        self.width, SDLUserInterface.STATUSBAR_HEIGHT)

    def show(self):
        self.render_text()

    def set_character(self, character):
        self.character = character

    def render_text(self):
        pygame.draw.rect(self.windowSurface, self.text_bg, self.rect)
        self.text = self.basic_font.render(self.text_msg, True,
                self.text_fg, self.text_bg)
        self.windowSurface.blit(self.text, self.rect)


    def set_message(self, msg=''):
        self.text_msg = msg
        self.render_text()


class SDLTopBar(SDLStatusBar):
    def __init__(self, basicFont, windowSurface, world_map,
            bar_width, pos_x=0, pos_y=0, character=None):
        super(SDLTopBar, self).__init__(basicFont, windowSurface, world_map,
                bar_width, pos_x=pos_x, pos_y=pos_y, character=character)

        self.text_fg = SDLUserInterface.WHITE
        self.text_bg = SDLUserInterface.BLUE
        self.set_message('Use arrow keys to move, "a" to attack and "x" to exit')


class SDLBottomBar(SDLStatusBar):
    def __init__(self, basicFont, windowSurface, world_map,
            bar_width, pos_x, pos_y, character=None):
        super(SDLBottomBar, self).__init__(basicFont, windowSurface, world_map,
                bar_width, pos_x=pos_x, pos_y=pos_y, character=character)

        self.text_fg = SDLUserInterface.WHITE
        self.text_bg = SDLUserInterface.RED


##
# UI representation of the WorldMap
##
class SDLWorldMap(classes.WorldMap):
    def __init__(self, windowSurface, width, height, offset_x=0, offset_y=0):
        super(SDLWorldMap, self).__init__(width, height)
        self.offset_x = offset_x
        self.offset_y = offset_y

    def print_map(self):
        for y in range(self.height):
            for x in range(self.width):
                cell = self.map[x][y]
                if cell is not None:
                    cell.show(self.offset_x, self.offset_y)

    def add_character(self, character):
        self.map[character.x][character.y] = character

    def remove_character(self, character):
        self.map[character.x][character.y] = None


##
# Base Character class
##
class SDLCharacter(classes.Character):
    def __init__(self, ui, attributes):
        pos_x = int(attributes[0])
        pos_y = int(attributes[1])
        hp = int(attributes[2])
        super(SDLCharacter, self).__init__(ui, pos_x, pos_y, hp)
        self.windowSurface = ui.windowSurface
        self.font = pygame.font.SysFont(None, SDLUserInterface.FONT_SIZE)


    def is_player(self):
        if self.text == SDLUserInterface.CHR_TXT_PLAYER:
            return True
        return False

    def set_dead(self):
        self.text = SDLUserInterface.CHR_TXT_DEAD
        self.color = SDLUserInterface.CHR_COLOR_DEAD
        self.hp = 0

    def show(self, offset_x=0, offset_y=0):
        self.rect = pygame.Rect(self.x * SDLUserInterface.CHR_SIZE + offset_x,
                        self.y * SDLUserInterface.CHR_SIZE + offset_y,
                        SDLUserInterface.CHR_SIZE,
                        SDLUserInterface.CHR_SIZE)
        pygame.draw.rect(self.windowSurface, self.color, self.rect)

        self.text_overlay = self.font.render(self.text, True,
                                SDLUserInterface.CHR_COLOR_BACKGROUND, self.color)
        self.windowSurface.blit(self.text_overlay, self.rect)

    def get_label(self):
        return self.text


##
# All the characters
##
class SDLPlayer(SDLCharacter, classes.Player):
    def __init__(self, ui, attributes):
        SDLCharacter.__init__(self, ui, attributes)
        self.text = SDLUserInterface.CHR_TXT_PLAYER
        self.color = SDLUserInterface.CHR_COLOR_PLAYER


class SDLEnemy(SDLCharacter, classes.Enemy):
    def __init__(self, ui, attributes):
        SDLCharacter.__init__(self, ui, attributes)
        self.text = SDLUserInterface.CHR_TXT_ENEMY
        self.color = SDLUserInterface.CHR_COLOR_ENEMY


class SDLWizard(SDLCharacter, classes.Wizard):
    def __init__(self, ui, attributes):
        SDLCharacter.__init__(self, ui, attributes)
        self.text = SDLUserInterface.CHR_TXT_WIZARD
        self.color = SDLUserInterface.CHR_COLOR_WIZARD


class SDLArcher(SDLCharacter, classes.Archer):
    def __init__(self, ui, attributes):
        SDLCharacter.__init__(self, ui, attributes)
        self.text = SDLUserInterface.CHR_TXT_ARCHER
        self.color = SDLUserInterface.CHR_COLOR_ARCHER

# vim: expandtab tabstop=4 shiftwidth=4 softtabstop=4
