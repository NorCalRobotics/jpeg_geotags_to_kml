# Copyright 2026 NorCalRobotics
# Unmodified use and code review only. No AI/ML training or redistribution rights.
import os
import json
import base64
import asyncio
import logging
from urllib.parse import urlparse
from js import File, window, document, fetch, Object # Import the JavaScript window object
from pyodide.ffi import to_js

http_put_logger = logging


def validate_config(config):
    if not isinstance(config, dict):
        raise ValueError('Configuration must be a JSON object.')
    if str(config.get('upload_protocol', '')).upper() != 'HTTP_PUT':
        raise ValueError('upload_protocol must be HTTP_PUT.')
    if not isinstance(config.get('upload_url'), str) or not config['upload_url'].strip():
        raise ValueError('upload_url must be a non-empty string.')
    if not isinstance(config.get('url_fmt'), str) or not config['url_fmt'].strip():
        raise ValueError('url_fmt must be a non-empty string.')
    if not isinstance(config.get('headers'), dict):
        raise ValueError('headers must be an object.')
    if not isinstance(config['headers'].get('Content-Type'), str) or not config['headers']['Content-Type'].strip():
        raise ValueError('headers.Content-Type must be a non-empty string.')

    sample_config = {'hostname': 'example.com', 'upload_dir': 'Photos/example', 'username': 'admin', 'password': 'password'}
    try:
        upload_url = config['upload_url'].format(sample_config, photo_path='photo.jpg')
        public_url = config['url_fmt'].format(sample_config, photo_path='photo.jpg')
    except Exception as exc:
        raise ValueError(f'Invalid Python format string: {exc}')

    upload_parsed = urlparse(upload_url)
    public_parsed = urlparse(public_url)
    if not upload_parsed.scheme or not upload_parsed.netloc:
        raise ValueError('upload_url must resolve to an absolute URL.')
    if not public_parsed.scheme or not public_parsed.netloc:
        raise ValueError('url_fmt must resolve to an absolute URL.')

    return True


def validate_cloud_config(config_json):
    try:
        config = json.loads(config_json) if isinstance(config_json, str) else config_json
    except Exception as exc:
        return {'ok': False, 'error': f'Invalid JSON: {exc}'}

    try:
        validate_config(config)
    except Exception as exc:
        return {'ok': False, 'error': str(exc)}

    return {'ok': True}


def sync_cloud_config():
    global server
    
    if type(window.config) is str:
        try:
            settings = json.loads(window.config)
        except Exception as exc:
            http_put_logger.error(f"Failed to parse cloud config JSON: {exc}")
            return
    elif hasattr(window.config, 'to_py'):
        settings = window.config.to_py()
    else:
        settings = window.config
    
    server = settings


window.validate_cloud_config = validate_cloud_config

"""Load the server settings from the config file"""
try:
    server = json.load(open('cloud.json', 'r'))
except IOError:
    http_put_logger.warning('HTTP-PUT Image Server settings file "cloud.json" not found.')
    server = None
    HttpPutServer = None

if server is not None:
    window.sync_cloud_config = sync_cloud_config

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
