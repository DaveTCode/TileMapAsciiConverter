import collections
import glob
import pygame
import os

class Project():

    def __init__(self, tile_width, tile_height, image_width_tiles, image_height_tiles, id_image_mapping, id_map, output_tiles, id_to_output_tile_mapping):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.image_width_tiles = image_width_tiles
        self.image_height_tiles = image_height_tiles
        self.id_image_mapping = id_image_mapping
        self.id_map = id_map
        self.output_tiles = output_tiles
        self.id_to_output_tile_mapping = id_to_output_tile_mapping
        self.id_counts = collections.Counter([item for sublist in self.id_map for item in sublist])

    def get_image_by_id(self, id):
        return self.id_image_mapping[id]

    def get_tile_by_id(self, id):
        if id in self.id_to_output_tile_mapping:
            return self.id_to_output_tile_mapping[id]
        else:
            return None

    def set_output_tile(self, id, output_tile):
            self.id_to_output_tile_mapping[id] = output_tile

    def get_ids_from_output_tile(self, output_tile):
        ids = []

        for id, tile in self.id_to_output_tile_mapping.iteritems():
            if output_tile == tile:
                ids.append(id)

        return ids

    def unknown_id_count(self):
        '''
            Corresponds to the number of ids which don't have a related output tile.
        '''
        return reduce(lambda x, y: x + 1 if not y in self.id_to_output_tile_mapping else x, self.id_image_mapping.keys(), 0)

    def unknown_tile_count(self):
        '''
            Corresponds to the number of tiles which have ids that are unknown.
        '''
        unknown = 0
        for row in self.id_map:
            unknown += reduce(lambda x, y: x + 1 if not y in self.id_to_output_tile_mapping else x, row, 0)

        return unknown

    def get_most_unknown_id(self):
        '''
            Retrieve the id of the tile which has the most instances but is also unknown.
        '''
        for id in self.id_counts:
            if not id in self.id_to_output_tile_mapping:
                return id

        return None

    def get_first_instance_of(self, id):
        '''
            Find the first place that a given id appears.
        '''
        for y in range(0, len(self.id_map)):
            for x in range(0, len(self.id_map[y])):
                if self.id_map[y][x] == id:
                    return x,y

        return None

def save(project_dir, project):
    def _save_output_tiles():
        with open(os.path.join(project_dir, "output_tiles.txt"), "w") as output_tiles_file:
            for identifier in project.output_tiles:
                tile = project.output_tiles[identifier]
                output_tiles_file.write("{0},{1},{2},{3},{4}\n".format(tile.identifier, tile.char, tile.r, tile.g, tile.b))

    def _save_output_tile_id_mappings():
        with open(os.path.join(project_dir, "output_tiles_id_mapping.txt"), "w") as mappings_file:
            for id in project.id_to_output_tile_mapping:
                mappings_file.write("{0},{1}\n".format(id, project.id_to_output_tile_mapping[id].identifier))

    _save_output_tiles()
    _save_output_tile_id_mappings()

def load(project_dir):
    def _load_project_file():
        tile_width, tile_height, image_width_tiles, image_height_tiles = 0, 0, 0, 0
        with open(os.path.join(project_dir, 'tiles.project')) as project_file:
            for line in project_file:
                line = line.strip()
                if line.startswith("tile_width"):
                    tile_width = int(line.split("=")[1])
                elif line.startswith("tile_height"):
                    tile_height = int(line.split("=")[1])
                elif line.startswith("image_width_tiles"):
                    image_width_tiles = int(line.split("=")[1])
                elif line.startswith("image_height_tiles"):
                    image_height_tiles = int(line.split("=")[1])

        return tile_width, tile_height, image_width_tiles, image_height_tiles

    def _load_id_map():
        id_map = []
        with open(os.path.join(project_dir, 'id_map.txt')) as id_map_file:
            for line in id_map_file:
                id_map.append([int(x) for x in line.strip().split(",")])

        return id_map

    def _load_image_tiles():
        image_tiles = {}
        for tile_file in os.listdir(project_dir):
            if tile_file.endswith(".png"):
                image_tiles[int(tile_file.replace(".png", ""))] = pygame.image.load(os.path.join(project_dir, tile_file))

        return image_tiles

    def _load_output_tiles():
        output_tiles = {}
        with open(os.path.join(project_dir, "output_tiles.txt")) as output_tiles_file:
            for line in output_tiles_file:
                parts = line.strip().split(",")
                output_tiles[parts[0]] = OutputTile(parts[0], parts[1], int(parts[2]), int(parts[3]), int(parts[4]))

        return output_tiles

    def _load_output_tile_id_mapping(output_tiles):
        mapping = {}
        with open(os.path.join(project_dir, "output_tiles_id_mapping.txt")) as mapping_file:
            for line in mapping_file:
                idStr, identifier = line.strip().split(",")
                id = int(idStr)
                mapping[id] = output_tiles[identifier]                    

        return mapping

    tile_width, tile_height, image_width_tiles, image_height_tiles = _load_project_file()
    output_tiles = _load_output_tiles()

    return Project(tile_width, tile_height, image_width_tiles, image_height_tiles, _load_image_tiles(), _load_id_map(), output_tiles, _load_output_tile_id_mapping(output_tiles))

class OutputTile():

    def __init__(self, identifier, char, r, g, b):
        self.identifier = identifier
        self.char = char
        self.r = r
        self.g = g
        self.b = b
        self.color = pygame.Color(r, g, b, 0)

    def __str__(self):
        return self.identifier