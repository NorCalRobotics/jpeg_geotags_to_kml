Configuration:
Edit the file [photo_collection_settings.json](photo_collection_settings.json) to set the photo gallery directory that will be processed,
or alternatively delete photo_collection_settings.json and specify the photo gallery directories to process at command-line arguments.

Edit the file [www_server.json](www_server.json) to configure your publicly available image hosting server, if you want your photos
to be uploaded so that your KML file can be published to other computers. If you only intend to use your KML
file on the same PC where the photos are locally saved, then you can just delete this file.

Dependencies:
This project requires the modules [pillow](https://pypi.org/project/Pillow/) and [pysftp](https://pypi.org/project/pysftp/). You can install these using [pip](https://pypi.org/project/pip/).
For Windows, if your python interpretter is in the default installed location,
you can run [install_pypi_requirements.bat](install_pypi_requirements.bat) to do this.
Otherwise, run `pip install pillow pysftp` as per normal [python](https://www.python.org/) procedures.

Usage:
Finally, to run the main script, run [photo_gallery_dir_to_kml.py](photo_gallery_dir_to_kml.py) with your locally installed python interpretter as per normal python procedures.

Unit tests:
You can also execute unit tests of the modules [jpeg_lat_long_extractor.py](jpeg_lat_long_extractor.py) and [www_server.py](www_server.py), by running either of those files as a script in your python interpretter.
This might be useful to resolve any problems that occur stemming from missing dependencies or configuration issues.
