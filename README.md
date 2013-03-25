TileMapAsciiConverter
=====================

A python application for converting tile based maps into ascii representations

Requirements
=====================
The application was developed using python 2.7 with the following libraries
- pygame 1.9.1 => http://www.pygame.org/download.shtml
- PIL 1.1.7 => http://effbot.org/downloads/PIL-1.1.7.win32-py2.7.exe

Usage
=====================
The application has two running modes

Create:
- This is used to create new projects from a single image file
- Usage
-- python main.py create <directory> -f <image_file> -x <tile_width> -y <tile_width>
- This can take some time to complete depending on the speed of your PC and the size of the image. It will provide process information whilst running

Edit:
- This is used to edit the projects created using the create command
- Usage
-- python main.py edit <directory>

Help
=====================
Help text is displayed in the command line when running in edit mode until a better solution presents itself.
