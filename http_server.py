import os
import json
import base64
import asyncio
import logging
from js import File, window, document, fetch, Object # Import the JavaScript window object
from pyodide.ffi import to_js

http_put_logger = logging


"""Load the server settings from the config file"""
try:
    server = json.load(open('cloud.json', 'r'))
except IOError:
    http_put_logger.warning('HTTP-PUT Image Server settings file "cloud.json" not found.')
    server = None
    HttpPutServer = None

if server is not None:
    window.configuration = server
    """Validate the server's upload protocol"""
    try:
        if server['upload_protocol'].upper() != 'HTTP_PUT':
            http_put_logger.warning('Specified HTTP-PUT Image Server upload protocol "%s" is not supported.' % server['upload_protocol'])
            server = None
            HttpPutServer = None
    except KeyError:
        http_put_logger.warning('HTTP-PUT Image Server upload protocol was not specified.')
        server = None
        HttpPutServer = None

if server is not None:
    class HttpPutServer:
        def __init__(self):
            self.logger = http_put_logger

        def get_www_url(self, photo_name):
            try:
                return server['url_fmt'].format(server, photo_path=photo_name)
            except KeyError as e:
                e.message = 'HTTP-PUT Image Server URL format was not specified.'
                self.logger.error(e.message)
                raise e

        async def upload_photo_ex(self, photo_js_object : File):
            upload_url = server['upload_url'].format(server, photo_path=photo_js_object.name)
            self.logger.info(f"Uploading {photo_js_object.name} to {upload_url}...") 
            response = await fetch(upload_url, to_js({
                'method': 'PUT',
                'headers': server["headers"],
                'body': photo_js_object
            }, dict_converter=Object.fromEntries))

            response_text = await response.text()

            if response.ok:
                self.logger.info(f"Upload successful [{response.status} {response.statusText}]: {photo_js_object.name}")
            else:
                self.logger.error(f"Upload failed [{response.status} {response.statusText}]: {response_text}")
            return response_text

        def upload_photo(self, photo_name : str):
            photo_js_object = None
            for file in document.getElementById('photo-picker').files:
                if file.name == photo_name:
                    photo_js_object = file
                    break
            
            if photo_js_object is None:
                self.logger.error(f"No pending file named {photo_name} found!")
                return None
            
            return asyncio.create_task(self.upload_photo_ex(photo_js_object))


def unit_test():
    """Uploads test photo to HTTP-PUT Image Server and then prints out the URL."""

    http_server = HttpPutServer()
    http_server.upload_photo(os.path.realpath("test_photo.jpg"))
    print(http_server.get_www_url("test_photo.jpg"))


if __name__ == "__main__":
    unit_test()
