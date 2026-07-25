# Copyright 2026 NorCalRobotics
# Unmodified use and code review only. No AI/ML training or redistribution rights.
import io
import os
import logging
from typing import List, Tuple, Optional
from js import FileList, document, window, Uint8Array  # Import the JavaScript File type representation
import jpeg_lat_long_extractor
from kml_generator import KmlGenerator
import http_server


class PwaLogHandler(logging.Handler):
    def __init__(self, element_id):
        super().__init__()
        self.element_id = element_id
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S')
        self.logger = logging.getLogger()
        self.setFormatter(formatter)
        self.logger.addHandler(self)
        self.logger.setLevel(logging.INFO)

    def emit(self, record):
        msg = self.format(record)
        document.getElementById(self.element_id).innerHTML += msg + '<br>'
        window.console.log(msg)


pwa_logger = PwaLogHandler('conversion-log')
http_server.http_put_logger = pwa_logger.logger
jpeg_lat_long_extractor.extractor_logger = pwa_logger.logger


async def convert_photos_to_kml(kml_name: str, photo_list: FileList) -> str:
    generator = KmlGenerator()
    pwa_logger.logger.info(f"Starting KML generation for {len(photo_list)} photos.")

    for photo in photo_list:
        photo_buffer = await photo.arrayBuffer()
        t_lat_long = jpeg_lat_long_extractor.get_photo_latlong(io.BytesIO(photo_buffer.to_bytes()))
        if t_lat_long is None:
            pwa_logger.logger.info(f"Warning: No GPS data found in {photo.name}. Skipping this photo.")
            continue
        latitude, longitude = t_lat_long
        latitude_s = "%f" % latitude
        longitude_s = "%f" % longitude
        generator.add_placemark(photo.name, photo.name, latitude_s, longitude_s)
        pwa_logger.logger.info(f"Added {photo.name} with coordinates ({latitude_s}, {longitude_s}) to KML.")

    kml_filename = os.path.basename(kml_name) + '.kml'
    generator.write_kml(kml_filename)
    pwa_logger.logger.info(f"KML file '{kml_filename}' has been created successfully.")

    kml_mimetype = 'application/vnd.google-earth.kml+xml'
    with open(kml_filename, 'rb') as f:
        kml_data = f.read()
    arr = Uint8Array.new(kml_data)
    kml_blob = window.Blob.new([arr], {'type': kml_mimetype})
    kml_url = window.URL.createObjectURL(kml_blob)

    link = f'<a id="download-link" href="{kml_url}" download="{kml_filename}">Download {kml_filename}</a>'
    document.getElementById('downloads-container').innerHTML += link + '<br>'
    pwa_logger.logger.info("KML generation completed.")

    return kml_filename


window.convert_photos_to_kml = convert_photos_to_kml