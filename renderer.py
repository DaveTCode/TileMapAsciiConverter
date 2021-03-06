import pygame
import sys

MAP_VIEW = 1
ID_VIEW = 2
CHAR_VIEW = 3

OUTPUT_TILE_AREA_DIMENSIONS = (150, 300)
OUTPUT_TILE_AREA_MARGIN_BOTTOM = 10
OUTPUT_TILE_AREA_MARGIN_RIGHT = 10
OUTPUT_TILE_AREA_PADDING_LEFT = 5
OUTPUT_TILE_AREA_PADDING_TOP = 15
OUTPUT_TILE_AREA_ROW_HEIGHT = 15

STATUS_AREA_MARGIN_LEFT = 10
STATUS_AREA_MARGIN_RIGHT = 10
STATUS_AREA_MARGIN_TOP = 10
STATUS_AREA_HEIGHT = 20

class Renderer():
    def __init__(self, game_surface, font, project):
        self.game_surface = game_surface
        self.font = font
        self.highlighted_ids = []
        self.highlighted_output_tiles = []
        self.project = project
        
        self.selected_highlight = pygame.Surface((project.tile_width, project.tile_height), flags=pygame.SRCALPHA)
        self.selected_highlight.fill((200,0,0,100))

        self.known_highlight = pygame.Surface((project.tile_width, project.tile_height), flags=pygame.SRCALPHA)
        self.known_highlight.fill((80,80,80,100))

        self.output_tile_highlighter = pygame.Surface((OUTPUT_TILE_AREA_DIMENSIONS[0], OUTPUT_TILE_AREA_ROW_HEIGHT), flags=pygame.SRCALPHA)
        self.output_tile_highlighter.fill((200,0,0,100))

        self.status_area_surface = pygame.Surface((game_surface.get_width() - STATUS_AREA_MARGIN_RIGHT - STATUS_AREA_MARGIN_LEFT, STATUS_AREA_HEIGHT), flags=pygame.SRCALPHA)

        self.tile_surface = pygame.Surface(OUTPUT_TILE_AREA_DIMENSIONS, flags=pygame.SRCALPHA)
        self.num_output_tile_rows = (OUTPUT_TILE_AREA_DIMENSIONS[1] - OUTPUT_TILE_AREA_PADDING_TOP) // OUTPUT_TILE_AREA_ROW_HEIGHT
        self.output_tile_page = 0
        self.selected_row = -1
        self.leftmost_tile = 0
        self.topmost_tile = 0
        self.highlight_unknown = False

    def get_num_tiles_x(self):
        return self.game_surface.get_width() // self.project.tile_width

    def get_num_tiles_y(self):
        return self.game_surface.get_height() // self.project.tile_height

    def get_highlighted_ids(self):
        ids = []
        for output_tile in self.highlighted_output_tiles:
            ids = ids + self.project.get_ids_from_output_tile(output_tile)

        return list(set(ids + self.highlighted_ids))

    def num_output_tile_pages(self):
        return len(self.project.output_tiles) // self.num_output_tile_rows

    def get_output_tile_at(self, screen_x, screen_y):
        if (screen_x > self.output_area_left() and screen_x < self.output_area_left() + OUTPUT_TILE_AREA_DIMENSIONS[0] and 
            screen_y > self.output_area_top() and screen_y < self.output_area_top() + OUTPUT_TILE_AREA_DIMENSIONS[1]):
            row = (screen_y - self.output_area_top()) // OUTPUT_TILE_AREA_ROW_HEIGHT + self.output_tile_page * self.num_output_tile_rows - 1

            if row < len(self.project.output_tiles):
                return self.project.output_tiles.values()[row]

        return None

    def get_tile_at(self, screen_x, screen_y):
        x,y = self.screen_to_map_coords(screen_x, screen_y)

        return self.project.get_id_at(x, y)

    def screen_to_map_coords(self, screen_x, screen_y):
        x = self.leftmost_tile + screen_x // self.project.tile_width
        y = self.topmost_tile + screen_y // self.project.tile_height

        return x,y

    def output_area_left(self):
        return self.game_surface.get_width() - self.tile_surface.get_width() - OUTPUT_TILE_AREA_MARGIN_RIGHT

    def output_area_top(self):
        return self.game_surface.get_height() - self.tile_surface.get_height() - OUTPUT_TILE_AREA_MARGIN_BOTTOM

    def clear_highlighted_ids(self):
        self.highlighted_ids = []
        self.highlighted_output_tiles = []

    def centre_display_on(self, x, y):
        if len(self.project.id_map) > 0:
            self.leftmost_tile = x - self.get_num_tiles_x() // 2
            self.topmost_tile = y - self.get_num_tiles_y() // 2

    def shift_display(self, amount_x, amount_y):
        self.leftmost_tile += amount_x
        self.topmost_tile += amount_y

    def output_tile_page_adj(self, amount):
        self.output_tile_page = min(max(0, amount + self.output_tile_page), len(self.project.output_tiles) // self.num_output_tile_rows)

    def toggle_highlighted_id(self, id, append, remove_if_exists=True):
        if id in self.highlighted_ids:
            if remove_if_exists:
                self.highlighted_ids.remove(id)
        else:
            if append:
                self.highlighted_ids.append(id)
            else:
                self.highlighted_output_tiles = []
                self.highlighted_ids = [id]

    def toggle_highlighted_output_tile(self, output_tile, append, remove_if_exists=True):
        ids = self.project.get_ids_from_output_tile(output_tile)

        for id in ids:
            if id in self.highlighted_ids:
                self.highlighted_ids.remove(id)

        if output_tile in self.highlighted_output_tiles:
            if remove_if_exists:
                self.highlighted_output_tiles.remove(output_tile)
        else:
            if append:
                self.highlighted_output_tiles.append(output_tile)
            else:
                self.highlighted_ids = []
                self.highlighted_output_tiles = [output_tile]

    def render(self, view_mode):
        num_tiles_x = self.get_num_tiles_x()
        num_tiles_y = self.get_num_tiles_y()
        highlighted_ids = self.get_highlighted_ids()

        for col in range(self.leftmost_tile, self.leftmost_tile + num_tiles_x):
            for row in range(self.topmost_tile, self.topmost_tile + num_tiles_y):
                id = self.project.get_id_at(col, row)

                if id != None:
                    x, y = (col - self.leftmost_tile) * self.project.tile_width, (row - self.topmost_tile) * self.project.tile_height

                    if view_mode == MAP_VIEW:
                        output_image = self.project.get_image_by_id(id)
                        
                        self.game_surface.blit(output_image, (x, y))
                    elif view_mode == ID_VIEW:
                        self.game_surface.blit(self.font.render(str(id), 1, (255, 255, 255, 0)), (x, y))
                    elif view_mode == CHAR_VIEW:
                        output_tile = self.project.get_tile_by_id(id)
                        char = output_tile.char if output_tile else "?"
                        color = output_tile.color if output_tile else pygame.Color(255, 255, 255, 0)

                        self.game_surface.blit(self.font.render(char, 1, color), (x, y))

                    if id in highlighted_ids:
                        self.game_surface.blit(self.selected_highlight, (x, y))

                    if self.highlight_unknown and self.project.get_tile_by_id(id):
                        self.game_surface.blit(self.known_highlight, (x, y))

    def render_output_tile_area(self):
        self.tile_surface.fill((250,250,250))
        pygame.draw.rect(self.tile_surface, (50, 50, 50), (0, 0, self.tile_surface.get_width() - 1, self.tile_surface.get_height() - 1), 2)

        self.tile_surface.blit(self.font.render("(" + str(self.output_tile_page + 1) + "/" + str(self.num_output_tile_pages() + 1) + ")", 1, (0, 0 ,0)), (OUTPUT_TILE_AREA_DIMENSIONS[0] - 50, 0))

        count = 0
        page_count = 0
        for output_tile in self.project.output_tiles.values():
            if count >= self.output_tile_page * self.num_output_tile_rows and count < (self.output_tile_page + 1) * self.num_output_tile_rows:
                x = OUTPUT_TILE_AREA_PADDING_LEFT
                y = OUTPUT_TILE_AREA_PADDING_TOP + page_count * OUTPUT_TILE_AREA_ROW_HEIGHT

                if output_tile.r + output_tile.g + output_tile.b > 382.5:
                    pygame.draw.rect(self.tile_surface, (50, 50, 50), (0, y, self.tile_surface.get_width(), OUTPUT_TILE_AREA_ROW_HEIGHT))

                self.tile_surface.blit(self.font.render(output_tile.identifier + " - " + output_tile.char, 1, output_tile.color), (x, y))

                if output_tile in self.highlighted_output_tiles:
                    self.tile_surface.blit(self.output_tile_highlighter, (0, OUTPUT_TILE_AREA_PADDING_TOP + page_count * OUTPUT_TILE_AREA_ROW_HEIGHT))

                page_count += 1
            count += 1

        self.game_surface.blit(self.tile_surface, (self.output_area_left(), self.output_area_top()))

    def render_status_bar(self):
        self.status_area_surface.fill((250,250,250,100))

        status_string = "Unknown: {0} ({1} ids)".format(self.project.unknown_tile_count(), self.project.unknown_id_count())
        status_string_surface = self.font.render(status_string, 1, (50, 50, 50))
        self.status_area_surface.blit(status_string_surface, (0, 0))

        self.game_surface.blit(self.status_area_surface, (STATUS_AREA_MARGIN_LEFT, STATUS_AREA_MARGIN_TOP))