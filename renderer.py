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

class Renderer():
    def __init__(self, game_surface, font, project):
        self.game_surface = game_surface
        self.font = font
        self.highlighted_ids = []
        self.highlighted_output_tiles = []
        self.project = project
        self.highlighter = pygame.Surface((project.tile_width, project.tile_height), flags=pygame.SRCALPHA)
        self.highlighter.fill((200,0,0,100))
        self.output_tile_highlighter = pygame.Surface((OUTPUT_TILE_AREA_DIMENSIONS[0], OUTPUT_TILE_AREA_ROW_HEIGHT), flags=pygame.SRCALPHA)
        self.output_tile_highlighter.fill((200,0,0,100))

        # This corresponds to the fixed position output tile area
        self.tile_surface = pygame.Surface(OUTPUT_TILE_AREA_DIMENSIONS, flags=pygame.SRCALPHA)
        self.num_output_tile_rows = (OUTPUT_TILE_AREA_DIMENSIONS[1] - OUTPUT_TILE_AREA_PADDING_TOP) // OUTPUT_TILE_AREA_ROW_HEIGHT
        self.output_tile_page = 0
        self.selected_row = -1
        self.leftmost_tile = 0
        self.topmost_tile = 0

    def get_num_tiles_x(self):
        return self.game_surface.get_width() // self.project.tile_width

    def get_num_tiles_y(self):
        return self.game_surface.get_height() // self.project.tile_height

    def shift_display(self, amount_x, amount_y):
        self.leftmost_tile = min(max(0, self.leftmost_tile + amount_x), len(self.project.id_map[0]) - self.get_num_tiles_x())
        self.topmost_tile = min(max(0, self.topmost_tile + amount_y), len(self.project.id_map) - self.get_num_tiles_y())

    def get_highlighted_ids(self):
        ids = []
        for output_tile in self.highlighted_output_tiles:
            ids = ids + self.project.get_ids_from_output_tile(output_tile)

        return list(set(ids + self.highlighted_ids))

    def num_output_tile_pages(self):
        return len(self.project.output_tiles) // self.num_output_tile_rows

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

    def render(self, surface, view_mode):
        num_tiles_x = self.get_num_tiles_x()
        num_tiles_y = self.get_num_tiles_y()
        highlighted_ids = self.get_highlighted_ids()

        for col in range(self.leftmost_tile, self.leftmost_tile + num_tiles_x):
            for row in range(self.topmost_tile, self.topmost_tile + num_tiles_y):
                try:
                    id = self.project.id_map[row][col]
                except Exception:
                    print self.topmost_tile, num_tiles_y, row
                    sys.exit(0)
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
                    self.game_surface.blit(self.highlighter, (x,y))

    def get_output_tile_at(self, screen_x, screen_y):
        if (screen_x > self.output_area_left() and screen_x < self.output_area_left() + OUTPUT_TILE_AREA_DIMENSIONS[0] and 
            screen_y > self.output_area_top() and screen_y < self.output_area_top() + OUTPUT_TILE_AREA_DIMENSIONS[1]):
            row = (screen_y - self.output_area_top()) // OUTPUT_TILE_AREA_ROW_HEIGHT + self.output_tile_page * self.num_output_tile_rows

            if row < len(self.project.output_tiles):
                return self.project.output_tiles.values()[row]

        return None

    def get_tile_at(self, screen_x, screen_y):
        x = self.leftmost_tile + screen_x // self.project.tile_width
        y = self.topmost_tile + screen_y // self.project.tile_height

        if y < len(self.project.id_map) and x < len(self.project.id_map[y]):
            return self.project.id_map[y][x]
        else:
            return None

    def output_area_left(self):
        return self.game_surface.get_width() - self.tile_surface.get_width() - OUTPUT_TILE_AREA_MARGIN_RIGHT

    def output_area_top(self):
        return self.game_surface.get_height() - self.tile_surface.get_height() - OUTPUT_TILE_AREA_MARGIN_BOTTOM

    def render_output_tile_area(self, surface):
        self.tile_surface.fill((255,255,255,255))
        pygame.draw.rect(self.tile_surface, (0, 0, 0), (0, 0, self.tile_surface.get_width() - 1, self.tile_surface.get_height() - 1), 1)

        self.tile_surface.blit(self.font.render("(" + str(self.output_tile_page + 1) + "/" + str(self.num_output_tile_pages() + 1) + ")", 1, (0, 0 ,0)), (OUTPUT_TILE_AREA_DIMENSIONS[0] - 50, 0))

        count = 0
        page_count = 0
        for output_tile in self.project.output_tiles.values():
            if count > self.output_tile_page * self.num_output_tile_rows and count < (self.output_tile_page + 1) * self.num_output_tile_rows:
                if output_tile.r + output_tile.g + output_tile.b > 600:
                    background_color = (50,50,50)
                else:
                    background_color = (250,250,250)

                pygame.draw.rect(self.tile_surface, background_color, (0, OUTPUT_TILE_AREA_PADDING_TOP + page_count * OUTPUT_TILE_AREA_ROW_HEIGHT, self.tile_surface.get_width(), OUTPUT_TILE_AREA_PADDING_TOP + (page_count + 1) * OUTPUT_TILE_AREA_ROW_HEIGHT))
                self.tile_surface.blit(self.font.render(output_tile.identifier + " - " + output_tile.char, 1, output_tile.color), 
                                       (OUTPUT_TILE_AREA_PADDING_LEFT, OUTPUT_TILE_AREA_PADDING_TOP + page_count * OUTPUT_TILE_AREA_ROW_HEIGHT))

                if output_tile in self.highlighted_output_tiles:
                    self.tile_surface.blit(self.output_tile_highlighter, (0, OUTPUT_TILE_AREA_PADDING_TOP + page_count * OUTPUT_TILE_AREA_ROW_HEIGHT))

                page_count += 1
            count += 1

        self.game_surface.blit(self.tile_surface, (self.output_area_left(), self.output_area_top()))