import os
import chevron
from www_server import WwwServer
from typing import Final


class KmlGenerator:
    # Mapping EXIF integers to CSS degrees
    rotation_none: Final = "0deg"
    orientation_mapping: Final = {
        1: rotation_none,
        3: "180deg",
        6: "90deg",
        8: "270deg"
    }

    def __init__(self, template_path="kml_template.mustache"):
        with open(template_path, "r") as f:
            self.template = f.read()

        self.placemarks = []

        if WwwServer is None:
            self.hosting = None
        else:
            self.hosting = WwwServer()

    def css_orientation_style(self, orientation=1):
        rotation = self.orientation_mapping.get(orientation, self.rotation_none)
        if rotation == self.rotation_none:
            return ""

        style_t = """
        transform: rotate({0});
        -webkit-transform: rotate({0});
        transform-origin: center;
        image-orientation: from-image; /* Look at the EXIF tag and rotate */
        """
        style_f = " ".join(style_t.strip().split())

        return style_f.format(rotation)

    def add_placemark(self, photo_filename, photo_path, latitude, longitude, orientation=1):
        photo_name = os.path.splitext(photo_path)[0]
        if self.hosting is not None:
            self.hosting.upload_photo(photo_filename)
            img_url = self.hosting.get_www_url(photo_path)
        else:
            img_url = "file:///" + photo_filename

        self.placemarks.append({
            "name": photo_name,
            "photo_url": img_url,
            "latitude": latitude,
            "longitude": longitude,
            "style_attr": self.css_orientation_style(orientation)
        })

    def write_kml(self, output_filename):
        data = {
            "document_name": output_filename,
            "placemarks": self.placemarks
        }

        with open(output_filename, 'w') as output_kml:
            output_kml.write(chevron.render(self.template, data))
