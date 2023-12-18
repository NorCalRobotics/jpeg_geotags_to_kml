import os
from www_server import WwwServer

kml_template_filename = "output_template.kml"
doc_name_pattern = "<document name />"
placemarks_pattern = "<Placemarks>"

placemark_template_filename = "placemark_template.kml"
placemark_name_pattern = "<placemark name />"
placemark_img_pattern = "<placemark img />"
img_local_url_fmt = "file:///%s"
placemark_img_fmt = '<img style="max-width:500px;" src="%s">'
lati_pattern = "LATITUDE"
long_pattern = "LONGITUDE"
jpeg_pattern = "JPEG_FILENAME"
url_pattern = "JPEG_URL"


class KmlGenerator:
    def __init__(self):
        with open(placemark_template_filename, "r") as placemark_template_file:
            self.placemark_template = placemark_template_file.read()

        with open(kml_template_filename, "r") as kml_template_file:
            self.kml_template = kml_template_file.read()

        self.placemarks = ""
        self.delim = ""

        if WwwServer is None:
            self.hosting = None
        else:
            self.hosting = WwwServer()

    def add_placemark(self, photo_filename, photo_path, latitude, longitude):
        placemark_name = '<name>' + os.path.splitext(photo_path)[0] + '</name>'
        if self.hosting is not None:
            self.hosting.upload_photo(photo_filename)
            img_url = self.hosting.get_www_url(photo_path)
        else:
            img_url = img_local_url_fmt % photo_filename
        placemark_img = placemark_img_fmt % img_url

        pm0 = self.placemark_template.replace(placemark_name_pattern, placemark_name)
        pm1 = pm0.replace(placemark_img_pattern, placemark_img)
        pm2 = pm1.replace(lati_pattern, latitude)
        pm3 = pm2.replace(long_pattern, longitude)
        pm4 = pm3.replace(jpeg_pattern, os.path.splitext(photo_path)[0])
        pm5 = pm4.replace(url_pattern, img_url)

        self.placemarks += self.delim + pm5
        self.delim = "\n"

    def write_kml(self, output_filename):
        with open(output_filename, 'w') as output_kml:
            kml0 = self.kml_template.replace(doc_name_pattern, '<name>' + output_filename + '</name>')
            kml = kml0.replace(placemarks_pattern, self.placemarks)
            output_kml.write(kml)
