import os
import sys
import json
from jpeg_lat_long_extractor import get_photo_latlong
from kml_generator import KmlGenerator
from google_earth_importable_csv_generator import CsvGenerator

try:
    settings = json.load(open('photo_collection_settings.json', 'r'))
    photo_gallery_directory = settings['photo_gallery_directory']
except IOError:
    photo_gallery_directory = None
except KeyError:
    photo_gallery_directory = None


def process_photos_in_directory(photo_directory):
    """Extracts latitude/longitude from photo files within a given directory,
    and creates a KML file with placemarks for the photos.
    This KML file can be imported into Google Earth"""

    generator = KmlGenerator()
    csv_generator = CsvGenerator(os.path.basename(photo_directory) + '.csv')

    for photo_path in os.listdir(photo_directory):
        photo_filename = photo_directory + "/" + photo_path

        t_lat_long = get_photo_latlong(photo_filename)
        if t_lat_long is not None:
            latitude, longitude = t_lat_long
            latitude_s = "%f" % latitude
            longitude_s = "%f" % longitude
            csv_generator.add_placemark(photo_path, latitude_s, longitude_s)
            generator.add_placemark(photo_filename, photo_path, latitude_s, longitude_s)

    generator.write_kml(os.path.basename(photo_directory) + '.kml')


def main():
    """Reads photo geotags and marks their locations in Google Earth."""

    if photo_gallery_directory is not None:
        process_photos_in_directory(photo_gallery_directory)

    for directory in sys.argv[1:]:
        process_photos_in_directory(os.path.realpath(directory))


if __name__ == "__main__":
    main()
