import io
import os
from typing import List, Tuple, Optional
from js import File  # Import the JavaScript File type representation
from jpeg_lat_long_extractor import get_photo_latlong
from kml_generator import KmlGenerator

async def convert_photos_to_kml(kml_name: str, photo_list: List[File]) -> str:
    generator = KmlGenerator()

    for photo in photo_list:
        photo_buffer = await photo.arrayBuffer()
        t_lat_long = get_photo_latlong(io.BytesIO(photo_buffer.to_bytes()))
        if t_lat_long is None:
            continue
        latitude, longitude = t_lat_long
        latitude_s = "%f" % latitude
        longitude_s = "%f" % longitude
        generator.add_placemark(photo.name, photo.name, latitude_s, longitude_s)

    kml_filename = os.path.basename(kml_name) + '.kml'
    generator.write_kml(kml_filename)
    return kml_filename