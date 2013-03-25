import pygame
from pygame.locals import *
import project
import renderer
import sys
from outputtileform import OutputTileForm

WIDTH = 1024
HEIGHT = 768
FPS = 30

class TileToAsciiMapUI():
    def __init__(self, project_dir):
        pygame.init()

        self.project_dir = project_dir
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.fps_clock = pygame.time.Clock()
        self.view_mode = renderer.MAP_VIEW
        self.project = None
        self.ui_renderer = None
        self.output_tile_form = None
        self.viewing_output_tile_form = False
        self.selection_start_x = self.selection_start_y = None
        self.x_vel = self.y_vel = 0

    def handle_event(self, event):
        shift_down = pygame.key.get_mods() & KMOD_SHIFT
        x_vel = y_vel = 0

        if event.type == QUIT:
            project.save(self.project_dir, self.project)
            pygame.quit()
            sys.exit(0)
        else:
            if self.viewing_output_tile_form:
                if self.output_tile_form.process_event(event):
                    self.viewing_output_tile_form = False
            else:
                if event.type == KEYDOWN:
                    if event.key == K_LEFT:
                        self.x_vel = -1
                    elif event.key == K_RIGHT:
                        self.x_vel = 1
                    elif event.key == K_UP:
                        self.y_vel = -1
                    elif event.key == K_DOWN:
                        self.y_vel = 1
                elif event.type == KEYUP:
                    if event.key == K_LEFT or event.key == K_RIGHT:
                        self.x_vel = 0
                    elif event.key == K_UP or event.key == K_DOWN:
                        self.y_vel = 0
                    elif event.key == K_c:
                        self.view_mode = renderer.CHAR_VIEW
                    elif event.key == K_i:
                        self.view_mode = renderer.ID_VIEW
                    elif event.key == K_m:
                        self.view_mode = renderer.MAP_VIEW
                    elif event.key == K_n:
                        self.viewing_output_tile_form = True
                    elif event.key == K_r:
                        self.ui_renderer.highlight_unknown = (not self.ui_renderer.highlight_unknown)
                    elif event.key == K_u:
                        id_to_view = self.project.get_most_unknown_id()

                        if id_to_view != None:
                            self.ui_renderer.toggle_highlighted_id(id_to_view, False, remove_if_exists=False)
                            coords = self.project.get_first_instance_of(id_to_view)
                            self.ui_renderer.centre_display_on(coords[0], coords[1])
                    elif event.key == K_PAGEUP:
                        self.ui_renderer.output_tile_page_adj(-1)
                    elif event.key == K_PAGEDOWN:
                        self.ui_renderer.output_tile_page_adj(1)
                    elif event.key == K_ESCAPE:
                        self.ui_renderer.clear_highlighted_ids()
                elif event.type == MOUSEBUTTONUP:
                    screen_x, screen_y = pygame.mouse.get_pos()
                    if self.selection_start_x != None and self.selection_start_y != None:
                        map_x, map_y = self.ui_renderer.screen_to_map_coords(screen_x, screen_y)
                        map_start_x, map_start_y = self.ui_renderer.screen_to_map_coords(self.selection_start_x, self.selection_start_y)
                        self.selection_start_x = self.selection_start_y = None

                        if not shift_down:
                            self.ui_renderer.clear_highlighted_ids()

                        for x in range(min(map_start_x, map_x), max(map_start_x, map_x) + 1):
                            for y in range(min(map_start_y, map_y), max(map_start_y, map_y) + 1):
                                self.ui_renderer.toggle_highlighted_id(self.project.id_map[y][x], True, remove_if_exists=(map_start_x == map_x and map_start_y == map_y and shift_down))
                        
                elif event.type == MOUSEBUTTONDOWN:
                    screen_x, screen_y = pygame.mouse.get_pos()
                    if pygame.mouse.get_pressed()[0]:
                        output_tile = self.ui_renderer.get_output_tile_at(screen_x, screen_y)

                        if output_tile:
                            self.ui_renderer.toggle_highlighted_output_tile(output_tile, shift_down)
                        else:
                            self.selection_start_x, self.selection_start_y = screen_x, screen_y
                    elif pygame.mouse.get_pressed()[2]:
                        output_tile = self.ui_renderer.get_output_tile_at(screen_x, screen_y)

                        if output_tile:
                            self.ui_renderer.toggle_highlighted_output_tile(output_tile, True, remove_if_exists=False)
                            for id in self.ui_renderer.get_highlighted_ids():
                                self.project.set_output_tile(id, output_tile)

    def ui_velocity(self):
        shift_down = pygame.key.get_mods() & KMOD_SHIFT
        return self.x_vel * (5 if shift_down else 1), self.y_vel * (5 if shift_down else 1)

    def run(self):
        self.project = project.load(self.project_dir)
        self.ui_renderer = renderer.Renderer(self.surface, pygame.font.SysFont('consolas', 12), self.project)
        self.output_tile_form = OutputTileForm(self.project, self.surface, pygame.font.SysFont('consolas', 14))

        while True:
            for event in pygame.event.get():
                self.handle_event(event)

            self.ui_renderer.shift_display(self.ui_velocity()[0], self.ui_velocity()[1])

            self.surface.fill((0,0,0,0))
            self.ui_renderer.render(self.view_mode)
            self.ui_renderer.render_output_tile_area()
            self.ui_renderer.render_status_bar()

            if self.viewing_output_tile_form:
                self.output_tile_form.render()

            pygame.display.update()
            self.fps_clock.tick(FPS)