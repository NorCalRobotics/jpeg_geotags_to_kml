## Configuration:
### Specify your photo collections:
Edit the file [photo_collection_settings.json](photo_collection_settings.json) to set the photo gallery directory that will be processed,
or alternatively delete photo_collection_settings.json and specify the photo gallery directories to process at command-line arguments.
#### photo_gallery_directory setting:
Set this value to the pathname of the local directory where the collection of photos is stored.
(On Windows, use / instead of \ in the path)

### Specify photo web hosting for KML publishing:
Edit the file [www_server.json](www_server.json) to configure your publicly available image hosting server, if you want your photos
to be uploaded so that your KML file can be published to other computers. If you only intend to use your KML
file on the same PC where the photos are locally saved, then you can just delete this file.
#### hostname
Your hosting server's hostname, i.e. FQDN such as www.my-photos.com
#### local_ip
Your hosting server's IP address used when making the SFTP connection.
This will override the hostname setting, if specified.
#### username
Username for authentication with your hosting server
#### password
Password for authentication with your hosting server
#### hostkey_type
Hostkey type, for authentication with your hosting server (known hosts list)
Typical value: "ecdsa-sha2-nistp256"
#### hostkey
Hostkey for authentication with your hosting server (known hosts list)
#### upload_protocol
Currently ony SFTP protocol is supported
#### upload_dir
Directory on the hosting server's filesystem where photos will be uploaded to.
#### sftp_dest_fmt
String used with format() function to generate the SFTP file destination.
Should be set to "{0[hostname]}:{0[upload_dir]}/{photo_path}", normally.
This can self-reference fields in this config file, such as in the case of the pattern "{0[local_ip]}".
The pattern "{photo_path}" will be replaced by each photo's filename.
#### http_dir
HTTP subdirectory where images are hosted, if applicable.
#### url_fmt
String used with format() function to generate the hosted image URL.
Should be set to "http://{0[hostname]}/{0[http_dir]}/{photo_path}", normally.
This can self-reference fields in this config file, such as in the case of the pattern "{0[http_dir]}".
The pattern "{photo_path}" will be replaced by each photo's filename.

## Dependencies:
This project requires the modules [pillow](https://pypi.org/project/Pillow/) and [pysftp](https://pypi.org/project/pysftp/). You can install these using [pip](https://pypi.org/project/pip/).
For Windows, if your python interpretter is in the default installed location,
you can run [install_pypi_requirements.bat](install_pypi_requirements.bat) to do this.
Otherwise, run `pip install pillow pysftp` as per normal [python](https://www.python.org/) procedures.

## Usage:
Finally, to run the main script, run [photo_gallery_dir_to_kml.py](photo_gallery_dir_to_kml.py) with your locally installed python interpretter as per normal python procedures.

## Unit tests:
You can also execute unit tests of the modules [jpeg_lat_long_extractor.py](jpeg_lat_long_extractor.py) and [www_server.py](www_server.py), by running either of those files as a script in your python interpretter.
This might be useful to resolve any problems that occur stemming from missing dependencies or configuration issues.
