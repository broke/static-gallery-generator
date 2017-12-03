# Static Gallery Generator

## Dependencies

- Python
  - Pillow
  - Jinja2

## Configuration

To configure the static gallery generator just edit *config.py*.

## Usage

Just put your photos in directories to your configured *GALLERY_PATH*.
Each directory in this path creates a new collection in your final gallery html.
The name of each collection is the directory name.
Comments for your photos are extracted from EXIF informations of your source
images. The generator is looking for exif *user comment* in the first place.
Falling back to exif image description and using *DEFAULT_IMG_DESC* when both
fields are empty.
Now you can run *generate.py* to create your photo gallery.

## Themes

Just lace a new theme into *theme* directory. Just take the *simple* theme as
example to create your own.