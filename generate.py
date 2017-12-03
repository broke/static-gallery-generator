#!/usr/bin/env python

import os
import glob
import shutil

from PIL import Image, ImageOps
import jinja2

from config import SITENAME
from config import THEME
from config import SIZE
from config import GALLERY_PATH
from config import OUTPUT_PATH
from config import DEFAULT_IMG_DESC

VERSION = '0.9.0'

def generate_output_dirs(collections):
    """This function is used to generate the output directory tree. Existing
       directories are kept.
    """
    print('creating directory tree:')
    try:
        os.mkdir(OUTPUT_PATH)
    except OSError:
        print('  {:<60}{:>20}'.format('Output dir allready exists',
                                      '[Ignoring]'))
    try:
        os.mkdir(os.path.join(OUTPUT_PATH, GALLERY_PATH))
    except OSError:
        print('  {:<60}{:>20}'.format('Collection base dir allready exists',
                                      '[Ignoring]'))
    for collection in collections:
        coll_path = os.path.join(OUTPUT_PATH, GALLERY_PATH, collection)
        thumb_path = os.path.join(OUTPUT_PATH, GALLERY_PATH, collection,
                                  'thumbnails')
        try:
            os.mkdir(coll_path)
        except OSError:
            print('  {:<60}{:>20}'.format('Collection dir \'' + collection +
                                          '\' allready exists', '[Ignoring]'))

        try:
            os.mkdir(thumb_path)
        except OSError:
            print('  {:<60}{:>20}'.format('Thumbnail dir for collection \''
                                          + collection + '\' allready exists',
                                          '[Ignoring]'))

    print('  {:>80}'.format('[Done]'))

def generate_thumbnails(photos):
    """This function is used to generate thumbnails for detected photos in all
       collections and copy these to thier final location in the the output
       directory.
    """
    for infile in photos:
        image = Image.open(infile)
        image = ImageOps.fit(image, SIZE, Image.ANTIALIAS)
        path, file = os.path.split(infile)
        thumb_output_dir = os.path.join(OUTPUT_PATH, path, 'thumbnails', file)
        image.save(thumb_output_dir, "JPEG")

def copy_photos(photos):
    """This function is used to copy all photos from the collections to the
       output directory.
    """
    for infile in photos:
        path, file = os.path.split(infile)
        photo_output_dir = os.path.join(OUTPUT_PATH, path, file)
        shutil.copyfile(infile, photo_output_dir)

def generate_html(collections):
    """This function is used to generate the HTML file to browse the photo
       gallary.
    """
    print('generating HTML:')
    collection_info = list()
    # Sorting collections for sorted display
    collections.sort()

    for collection in collections:
        in_path = os.path.join(GALLERY_PATH, collection)
        suffixes = ('/*.jpg', '*.jpeg')
        photos_origin = list()
        for suffix in suffixes:
            path = glob.glob(in_path + '/' + suffix)
            photos_origin.extend(path)

        photos_origin.sort()

        photos_info = list()
        for photo in photos_origin:
            path, file = os.path.split(photo)

            # TODO: Use a more elegant way to get exif informations
            exif_info = Image.open(photo)._getexif()
            exif_description = DEFAULT_IMG_DESC
            if exif_info is None:
                print('Image ' + file + ' has no Exif information')
            else:
                # Exif: user comment
                if 37510 in exif_info.keys():
                    # removing leading \x00's where ever this come from
                    exif_decoded = exif_info[37510].decode('utf-8').lstrip('\x00')
                    if exif_decoded:
                        exif_description = exif_decoded
                    else:
                        print('Image ' + file +
                              ' has no description, using default')

                # Exif: image description
                elif 270 in exif_info.keys():
                    # removing leading \x00's where ever this come from
                    exif_decoded = exif_info[270].decode('utf-8').lstrip('\x00')
                    if exif_decoded:
                        exif_description = exif_decoded
                    else:
                        print('Image ' + file +
                              ' has no description, using default')
                else:
                    print('Image ' + file +
                          ' has no description, using default')

            info = {'origin': photo,
                    'thumbnail': os.path.join(path, 'thumbnails', file),
                    'description': exif_description
                   }
            photos_info.append(info)

        collection_info.append({'name': collection, 'photos': photos_info})

    template_base = os.path.join('themes', THEME)
    loader = jinja2.FileSystemLoader(template_base)
    env = jinja2.Environment(loader=loader)
    template = env.get_template('index.html')
    render = template.render(version=VERSION,
                             sitename=SITENAME,
                             thumbnail_size=SIZE,
                             collections=collection_info)

    with open(os.path.join(OUTPUT_PATH, 'index.html'), 'w') as file_writer:
        file_writer.write(render)

    print('  {:>80}'.format('[Done]'))

def copy_static():
    """This function is used to copy static directories/files to the output
       directory.
    """
    print('copying static content:')
    in_dir = os.path.join('themes', THEME, 'static')
    out_dir = os.path.join(OUTPUT_PATH, 'static')
    shutil.rmtree(out_dir, ignore_errors=True)
    shutil.copytree(in_dir, out_dir)
    print('  {:>80}'.format('[Done]'))

def main():
    # Enumerate collection directories in input directory
    ph_collections = os.listdir(GALLERY_PATH)

    # Create output directory structure
    generate_output_dirs(ph_collections)

    print('generating thumbnails:')
    for collection in ph_collections:
        in_path = os.path.join(GALLERY_PATH, collection)
        photos = glob.glob(in_path + '/*.jpg')
        generate_thumbnails(photos)
        copy_photos(photos)
        print('  {:<60}{:>20}'.format(collection, '[Done]'))

    generate_html(ph_collections)

    copy_static()

if __name__ == '__main__':
    main()
