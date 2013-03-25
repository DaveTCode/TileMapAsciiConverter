import sys
import argparse
import extract_tiles
import tile_to_ascii_map_ui

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert an image into ascii by tiles")
    parser.add_argument("type", choices=["create", "edit"])
    parser.add_argument("project_directory")
    parser.add_argument("-f", "--imagefile")
    parser.add_argument("-x", "--tilewidth", type=int)
    parser.add_argument("-y", "--tileheight", type=int)
    
    args = parser.parse_args()
    if args.type == "create":
        if not args.imagefile:
            print("You must specify an image file to create a new project")
            sys.exit(1)
        elif not args.tilewidth:
            print("You must specify a tile width to create a new project")
            sys.exit(1)
        elif not args.tileheight:
            print("You must specify a tile height to create a new project")
            sys.exit(1)
        else:
            creator = extract_tiles.ProjectCreator(args.imagefile, args.project_directory, args.tilewidth, args.tileheight)
            creator.create()
    elif args.type == "edit":
        print("Selecting Tiles:")
        print("Left click => Select/Deselect tile")
        print("Shift + Left click => Select/Deselect tile keeping current selection")
        print("")
        print("Output Tiles:")
        print("n => Add a new output tile")
        print("Right click => Converts the selected tiles into the output tile clicked on")
        print("")
        print("Viewing modes:")
        print("m => Map view")
        print("c => Character view")
        print("i => Id view")
        print("")
        print("Functions")
        print("r => Grey out known tiles")
        print("u => Find unknown tile")
        print("")
        


        ui = tile_to_ascii_map_ui.TileToAsciiMapUI(args.project_directory)
        ui.run()