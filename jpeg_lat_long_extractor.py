import logging
from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS


def gps_tag_latlong_to_float(t_subject, hemisphere):
    """Converts a latitude or longitude GPS tag tuple to a floating point number"""

    t_degs = t_subject[0]
    t_mins = t_subject[1]
    t_secs = t_subject[2]

    degrees = float(t_degs[0]) / float(t_degs[1])
    minutes = float(t_mins[0]) / float(t_mins[1])
    seconds = float(t_secs[0]) / float(t_secs[1])

    sign = 1.0 if hemisphere in ('N', 'E') else -1.0

    value = degrees + (minutes / 60.0) + (seconds / 3600.0)

    return sign * value


def get_photo_latlong(photo_path):
    """Extracts the latitude and longitude from a photo file."""

    try:
        photo = Image.open(photo_path)
    except IOError:
        return None

    if photo.format != "JPEG":
        return None

    dir(photo)

    exif_table = dict()
    for tag_id, exif_value in photo.getexif().items():
        tag_name = TAGS.get(tag_id)
        if tag_name is None:
            continue

        logging.debug(tag_name + (" = %d" % tag_id))
        exif_table[tag_name] = exif_value

    if 'GPSInfo' not in exif_table:
        return None

    gps_info = dict()
    gps_ifd = exif_table['GPSInfo']
    for tag_id, gps_value in gps_ifd.items():
        geo_tag = GPSTAGS.get(tag_id)
        logging.debug(geo_tag + (" = %d" % tag_id))
        gps_info[geo_tag] = gps_value

    try:
        t_lat = gps_info['GPSLatitude']
        latitude = gps_tag_latlong_to_float(t_lat, gps_info['GPSLatitudeRef'])
        t_long = gps_info['GPSLongitude']
        longitude = gps_tag_latlong_to_float(t_long, ['GPSLongitudeRef'])
    except KeyError:
        return None

    return latitude, longitude


def unit_test():
    """Reads test photo geotag and prints out the location."""

    t_lat_long = get_photo_latlong("test_photo.jpg")
    if t_lat_long is not None:
        latitude, longitude = t_lat_long
        print("latitude: %f" % latitude)
        print("longitude: %f" % longitude)


if __name__ == "__main__":
    unit_test()
