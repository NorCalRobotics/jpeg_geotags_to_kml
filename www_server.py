import os
import json
import pysftp
import base64
import logging

"""Load the server settings from the config file"""
try:
    server = json.load(open('www_server.json', 'r'))
except IOError:
    logging.warn('WWW Server settings file "www_server.json" not found.')
    server = None
    WwwServer = None

if server is not None:
    """Validate the server's upload protocol"""
    try:
        if server['upload_protocol'].upper() != 'SFTP':
            logging.warn('Specified WWW Server upload protocol "%s" is not supported.' % server['upload_protocol'])
            server = None
            WwwServer = None
    except KeyError:
        logging.warn('WWW Server upload protocol was not specified.')
        server = None
        WwwServer = None

if server is not None:
    class WwwServer:
        def __init__(self):
            pass

        def get_www_url(self, photo_path):
            try:
                return server['url_fmt'].format(server, photo_path=photo_path)
            except KeyError as e:
                e.message = 'WWW Server URL format was not specified.'
                logging.error(e.message)
                raise e

        def get_sftp_dest(self, photo_path):
            try:
                return server['sftp_dest_fmt'].format(server, photo_path=photo_path)
            except KeyError as e:
                e.message = 'WWW Server SFTP destination format was not specified.'
                logging.error(e.message)
                raise e

        def upload_photo(self, photo_filename):
            try:
                hostname = server['local_ip']
            except KeyError:
                hostname = server['hostname']

            try:
                username = server['username']
            except KeyError as e:
                e.message = 'WWW Server username was not specified.'
                logging.error(e.message)
                raise e

            try:
                password = base64.decodestring(server['password'])
            except KeyError as e:
                e.message = 'WWW Server password was not specified.'
                logging.error(e.message)
                raise e

            """
            try:
                hostkey_type = server['hostkey_type']
            except KeyError as e:
                e.message = 'WWW Server hostkey type was not specified.'
                logging.error(e.message)
                raise e

            try:
                hostkey = server['hostkey']
            except KeyError as e:
                e.message = 'WWW Server hostkey was not specified.'
                logging.error(e.message)
                raise e

            cnopts = pysftp.CnOpts()
            cnopts.hostkeys.add(hostname, hostkey_type, FingerprintKey(hostkey))
            """

            try:
                dest_filename = server['upload_dir'] + '/' + os.path.basename(photo_filename)
            except KeyError:
                logging.warn('WWW Server upload directory was not specified.')
                dest_filename = None

            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None

            sftp = pysftp.Connection(host=hostname, username=username, password=password, cnopts=cnopts)
            sftp.put(photo_filename, dest_filename)
            sftp.close()


def unit_test():
    """Uploads test photo to WWW server and then prints out the URL."""

    http_server = WwwServer()
    http_server.upload_photo(os.path.realpath("test_photo.jpg"))
    print(http_server.get_www_url("test_photo.jpg"))


if __name__ == "__main__":
    unit_test()
