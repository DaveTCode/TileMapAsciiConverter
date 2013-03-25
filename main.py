import pygame
from pygame.locals import *
import project
import renderer
import sys
from outputtileform import OutputTileForm

project_dir = raw_input('Please select the project directory (relative path): ')

cProject = project.load(project_dir)

pygame.init()
game_surface = pygame.display.set_mode((1024, 768))
fps_clock = pygame.time.Clock()

view_mode = renderer.MAP_VIEW

ui_renderer = renderer.Renderer(game_surface, pygame.font.SysFont('consolas', 12), cProject)
x_vel = y_vel = 0
shift_down = False
output_tile_form = OutputTileForm(cProject, game_surface, pygame.font.SysFont('consolas', 14))
viewing_output_tile_form = False
selection_start_x = -1
selection_start_y = -1

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            project.save(project_dir, cProject)
            pygame.quit()
            sys.exit(0)
        else:
            if viewing_output_tile_form:
                if output_tile_form.process_event(event):
                    viewing_output_tile_form = False
            else:
                if event.type == KEYDOWN:
                    if event.key == K_LEFT:
                        x_vel = -1
                    elif event.key == K_RIGHT:
                        x_vel = 1
                    elif event.key == K_UP:
                        y_vel = -1
                    elif event.key == K_DOWN:
                        y_vel = 1
                    elif event.key == K_RSHIFT or event.key == K_LSHIFT:
                        shift_down = True
                elif event.type == KEYUP:
                    if event.key == K_LEFT or event.key == K_RIGHT:
                        x_vel = 0
                    elif event.key == K_UP or event.key == K_DOWN:
                        y_vel = 0
                    elif event.key == K_c:
                        view_mode = renderer.CHAR_VIEW
                    elif event.key == K_i:
                        view_mode = renderer.ID_VIEW
                    elif event.key == K_m:
                        view_mode = renderer.MAP_VIEW
                    elif event.key == K_n:
                        viewing_output_tile_form = True
                    elif event.key == K_r:
                        ui_renderer.highlight_unknown = (not ui_renderer.highlight_unknown)
                    elif event.key == K_u:
                        id_to_view = cProject.get_most_unknown_id()
                        ui_renderer.toggle_highlighted_id(id_to_view, False, remove_if_exists=False)
                        coords = cProject.get_first_instance_of(id_to_view)
                        ui_renderer.centre_display_on(coords[0], coords[1])
                    elif event.key == K_PAGEUP:
                        ui_renderer.output_tile_page_adj(-1)
                    elif event.key == K_PAGEDOWN:
                        ui_renderer.output_tile_page_adj(1)
                    elif event.key == K_RSHIFT or event.key == K_LSHIFT:
                        shift_down = False
                elif event.type == MOUSEBUTTONUP:
                    screen_x, screen_y = pygame.mouse.get_pos()
                    if selection_start_x != -1 and selection_start_y != -1:
                        map_x, map_y = ui_renderer.screen_to_map_coords(screen_x, screen_y)
                        map_start_x, map_start_y = ui_renderer.screen_to_map_coords(selection_start_x, selection_start_y)
                        selection_start_x = selection_start_y = -1

                        if not shift_down:
                            ui_renderer.clear_highlighted_ids()

                        for x in range(min(map_start_x, map_x), max(map_start_x, map_x) + 1):
                            for y in range(min(map_start_y, map_y), max(map_start_y, map_y) + 1):
                                ui_renderer.toggle_highlighted_id(cProject.id_map[y][x], True, remove_if_exists=False)
                        
                elif event.type == MOUSEBUTTONDOWN:
                    screen_x, screen_y = pygame.mouse.get_pos()
                    if pygame.mouse.get_pressed()[0]:
                        output_tile = ui_renderer.get_output_tile_at(screen_x, screen_y)

                        if output_tile:
                            ui_renderer.toggle_highlighted_output_tile(output_tile, shift_down)
                        else:
                            selection_start_x, selection_start_y = screen_x, screen_y
                    elif pygame.mouse.get_pressed()[2]:
                        output_tile = ui_renderer.get_output_tile_at(screen_x, screen_y)

                        if output_tile:
                            ui_renderer.toggle_highlighted_output_tile(output_tile, True, remove_if_exists=False)
                            for id in ui_renderer.get_highlighted_ids():
                                cProject.set_output_tile(id, output_tile)

    ui_renderer.shift_display(x_vel * (5 if shift_down else 1), y_vel * (5 if shift_down else 1))

    game_surface.fill((0,0,0,0))
    ui_renderer.render(view_mode)
    ui_renderer.render_output_tile_area()
    ui_renderer.render_status_bar()

    if viewing_output_tile_form:
        output_tile_form.render()

    pygame.display.update()
    fps_clock.tick(30)