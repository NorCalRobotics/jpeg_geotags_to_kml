import io
import os
from typing import List, Tuple, Optional
from js import FileList, document, window, Uint8Array  # Import the JavaScript File type representation
from jpeg_lat_long_extractor import get_photo_latlong
from kml_generator import KmlGenerator


def log_append(message):
    document.getElementById('conversion-log').innerHTML += message + '<br>'


async def convert_photos_to_kml(kml_name: str, photo_list: FileList) -> str:
    generator = KmlGenerator()
    log_append(f"Starting KML generation for {len(photo_list)} photos.")

    for photo in photo_list:
        photo_buffer = await photo.arrayBuffer()
        t_lat_long = get_photo_latlong(io.BytesIO(photo_buffer.to_bytes()))
        if t_lat_long is None:
            log_append(f"Warning: No GPS data found in {photo.name}. Skipping this photo.")
            continue
        latitude, longitude = t_lat_long
        latitude_s = "%f" % latitude
        longitude_s = "%f" % longitude
        generator.add_placemark(photo.name, photo.name, latitude_s, longitude_s)
        log_append(f"Added {photo.name} with coordinates ({latitude_s}, {longitude_s}) to KML.")

    kml_filename = os.path.basename(kml_name) + '.kml'
    generator.write_kml(kml_filename)
    log_append(f"KML file '{kml_filename}' has been created successfully.")

    kml_mimetype = 'application/vnd.google-earth.kml+xml'
    with open(kml_filename, 'rb') as f:
        kml_data = f.read()
    arr = Uint8Array.new(kml_data)
    kml_blob = window.Blob.new([arr], {'type': kml_mimetype})
    kml_url = window.URL.createObjectURL(kml_blob)

    link = f'<a id="download-link" href="{kml_url}" download="{kml_filename}">Download {kml_filename}</a>'
    document.getElementById('downloads-container').innerHTML += link + '<br>'
    log_append("KML generation completed.")

    return kml_filename


window.convert_photos_to_kml = convert_photos_to_kml