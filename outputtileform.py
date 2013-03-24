import pygame
from pygame.locals import *
import re
from project import OutputTile

VALID_IDENTIFIER_REGEX = re.compile('^[a-zA-Z_]{1,20}$')
VALID_CHAR_REGEX = re.compile('^.$')
VALID_COLOR_REGEX = re.compile('^\(?[012]?\d?\d,\s*[012]?\d?\d,\s*[012]?\d?\d\)?$')

# Text box enum
IDENTIFIER_TEXT_BOX = 1
CHAR_TEXT_BOX = 2
COLOR_TEXT_BOX = 3

IDENTIFIER_TEXT_BOX_WIDTH = 200
IDENTIFIER_TEXT_BOX_HEIGHT = 15
IDENTIFIER_TEXT_BOX_DIMENSIONS = (IDENTIFIER_TEXT_BOX_WIDTH, IDENTIFIER_TEXT_BOX_HEIGHT)

CHAR_TEXT_BOX_WIDTH = 200
CHAR_TEXT_BOX_HEIGHT = 15
CHAR_TEXT_BOX_DIMENSIONS = (CHAR_TEXT_BOX_WIDTH, CHAR_TEXT_BOX_HEIGHT)

COLOR_TEXT_BOX_WIDTH = 200
COLOR_TEXT_BOX_HEIGHT = 15
COLOR_TEXT_BOX_DIMENSIONS = (COLOR_TEXT_BOX_WIDTH, COLOR_TEXT_BOX_HEIGHT)

OUTPUT_TILE_FORM_WIDTH = 250
OUTPUT_TILE_FORM_HEIGHT = 65
OUTPUT_TILE_FORM_PADDING_TOP = 5
OUTPUT_TILE_FORM_PADDING_BOTTOM = 5
OUTPUT_TILE_FORM_PADDING_LEFT = 25
OUTPUT_TILE_FORM_PADDING_RIGHT = 25

TEXT_BOX_MARGIN_BOTTOM = 5

class OutputTileForm():

    def __init__(self, project, screen, font):
        self.project = project
        self.screen = screen
        self.font = font
        self.identifier = ""
        self.char = ""
        self.color = ""
        
        # These surfaces are used to render the form.
        self.surface = pygame.Surface((OUTPUT_TILE_FORM_WIDTH, OUTPUT_TILE_FORM_HEIGHT))
        self.identifier_text_box_surface = pygame.Surface((IDENTIFIER_TEXT_BOX_WIDTH, IDENTIFIER_TEXT_BOX_HEIGHT))
        self.char_text_box_surface = pygame.Surface((CHAR_TEXT_BOX_WIDTH, CHAR_TEXT_BOX_HEIGHT))
        self.color_text_box_surface = pygame.Surface((COLOR_TEXT_BOX_WIDTH, COLOR_TEXT_BOX_HEIGHT))

        # Track the text box which is currently being edited
        self.selected_text_box = IDENTIFIER_TEXT_BOX

        # Set each key to 1 to indicate that the field is not valid
        self.text_boxes = {IDENTIFIER_TEXT_BOX: self.identifier_text_box_surface, CHAR_TEXT_BOX: self.char_text_box_surface, COLOR_TEXT_BOX: self.color_text_box_surface}
        self.valid = {IDENTIFIER_TEXT_BOX: False, CHAR_TEXT_BOX: False, COLOR_TEXT_BOX: False}
        self.validators = {IDENTIFIER_TEXT_BOX: VALID_IDENTIFIER_REGEX, CHAR_TEXT_BOX: VALID_CHAR_REGEX, COLOR_TEXT_BOX: VALID_COLOR_REGEX}
        self.text = {IDENTIFIER_TEXT_BOX: '', CHAR_TEXT_BOX: '', COLOR_TEXT_BOX: ''}
        
    def process_event(self, event):
        '''
            Returns true if we should close the form otherwise returns false
        '''
        if event.type == MOUSEBUTTONDOWN:
            screen_x, screen_y = pygame.mouse.get_pos()
            self.selected_text_box = self.get_text_box_at_pos(screen_x, screen_y)
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                return True
            elif event.key == K_RETURN:
                if self.all_fields_valid():
                    self.save_output_tile()
                    return True
            elif self.selected_text_box:
                if event.key == K_TAB:
                    self.selected_text_box = self.selected_text_box % 3 + 1
                elif event.key == K_BACKSPACE:
                    self.text[self.selected_text_box] = self.text[self.selected_text_box][0:-1]
                elif event.key >= K_EXCLAIM and event.key <= K_z:
                    if self.selected_text_box == CHAR_TEXT_BOX:
                        self.text[self.selected_text_box] = ""
                    
                    self.text[self.selected_text_box] += event.unicode

        return False

    def save_output_tile(self):
        r,g,b = self.text[COLOR_TEXT_BOX].split(",")
        self.project.output_tiles[self.text[IDENTIFIER_TEXT_BOX]] = OutputTile(self.text[IDENTIFIER_TEXT_BOX], self.text[CHAR_TEXT_BOX], int(r), int(g), int(b))

    def surface_rect(self):
        return ((self.screen.get_width() - self.surface.get_width()) // 2, (self.screen.get_height() - self.surface.get_height()) // 2, OUTPUT_TILE_FORM_WIDTH, OUTPUT_TILE_FORM_HEIGHT)

    def get_text_box_at_pos(self, screen_x, screen_y):
        surface_rect = self.surface_rect()
        surface_x = screen_x - surface_rect[0]
        surface_y = screen_y - surface_rect[1]

        for text_box in self.text_boxes:
            rect = self.text_box_rect(text_box)

            if (surface_x > rect[0] and surface_x < rect[0] + rect[2] and
                surface_y > rect[1] and surface_y < rect[1] + rect[3]):
                return text_box

        return None

    def all_fields_valid(self):
        all_valid = True
        for text_box, text in self.text.iteritems():
            all_valid = all_valid and self.validate(text_box, text)

        return all_valid

    def validate(self, text_box, text):
        validator = self.validators[text_box]
        if validator.match(text):
            self.valid[text_box] = True
            return True
        else:
            self.valid[text_box] = False
            return False

    def text_box_rect(self, text_box):
        if text_box == IDENTIFIER_TEXT_BOX:
            return (OUTPUT_TILE_FORM_PADDING_LEFT, OUTPUT_TILE_FORM_PADDING_TOP, IDENTIFIER_TEXT_BOX_WIDTH, IDENTIFIER_TEXT_BOX_HEIGHT)
        elif text_box == CHAR_TEXT_BOX:
            return (OUTPUT_TILE_FORM_PADDING_LEFT, OUTPUT_TILE_FORM_PADDING_TOP + IDENTIFIER_TEXT_BOX_HEIGHT + TEXT_BOX_MARGIN_BOTTOM, CHAR_TEXT_BOX_WIDTH, CHAR_TEXT_BOX_HEIGHT)
        elif text_box == COLOR_TEXT_BOX:
            return (OUTPUT_TILE_FORM_PADDING_LEFT, OUTPUT_TILE_FORM_PADDING_TOP + IDENTIFIER_TEXT_BOX_HEIGHT + CHAR_TEXT_BOX_HEIGHT + 2 * TEXT_BOX_MARGIN_BOTTOM, COLOR_TEXT_BOX_WIDTH, COLOR_TEXT_BOX_HEIGHT)

    def render(self):
        self.surface.fill((0,0,0))

        for text_box, surface in self.text_boxes.iteritems():
            if text_box == self.selected_text_box:
                surface.fill((255,255,255))
            else:
                surface.fill((200,200,200))

            text = self.text[text_box]
            if self.selected_text_box == text_box:
                text += "|"

            surface.blit(self.font.render(text, 1, (0,0,0)), (0, 0))

            rect = self.text_box_rect(text_box)
            self.surface.blit(surface, (rect[0], rect[1]))

            self.validate(text_box, self.text[text_box])
            if not self.valid[text_box]:
                pygame.draw.rect(self.surface, (255,0,0), rect, 1)

        surface_rect = self.surface_rect()
        self.screen.blit(self.surface, (surface_rect[0], surface_rect[1]))