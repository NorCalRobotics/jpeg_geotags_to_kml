import os
import chevron
try:
    from www_server import WwwServer
except ModuleNotFoundError:
    WwwServer = None
except ImportError:
    WwwServer = None


class KmlGenerator:
    def __init__(self, template_path="kml_template.mustache"):
        with open(template_path, "r") as f:
            self.template = f.read()

        self.placemarks = []

        if WwwServer is None:
            self.hosting = None
        else:
            self.hosting = WwwServer()

    def add_placemark(self, photo_filename, photo_path, latitude, longitude):
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
            "longitude": longitude
        })

    def write_kml(self, output_filename):
        data = {
            "document_name": output_filename,
            "placemarks": self.placemarks
        }

        with open(output_filename, 'w') as output_kml:
            output_kml.write(chevron.render(self.template, data))
