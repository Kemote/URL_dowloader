import string
import random
import requests
from threading import Thread
from io import BytesIO
from zipfile import ZipFile


def thread(func):
    def wrapper(*args):
        thread = Thread(target=func, args=args)
        thread.start()
        return thread
    return wrapper


class ZippedUrls:
    def __init__(self, received_urls, storage_on_disk):
        self._received_urls = received_urls
        self._in_memory_zip_file = None
        self._id = self.generate_zip_id(32)
        self._storage_on_disk = storage_on_disk
        self._status = 'in-progress'

    @property
    def id(self):
        return self._id

    @property
    def status(self):
        return self._status

    @property
    def is_stored_on_disk(self):
        return self._storage_on_disk

    @property
    def archive(self):
        return self._in_memory_zip_file

    @thread
    def create_zip(self):
        """
        Download files from provided URls to memory and create zip files
        """

        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, 'w') as zip_file:
            for url in self._received_urls:
                file_name = self._get_url_file_name(url)
                file_as_bytes = self._get_url_as_bytes(url)
                zip_file.writestr(file_name, file_as_bytes)
        self._in_memory_zip_file = zip_buffer.getvalue()
        zip_buffer.close()
        print('store on disk? %s' % self._storage_on_disk)
        if self._storage_on_disk:
            self._store_archive_on_disk()
        else:
            self._status = 'completed'

    def _store_archive_on_disk(self):
        """
        Save file from memory to disk
        """

        print('start to downloading')
        with open('URL_downloader/stored_archives/%s.zip' % self._id, 'wb') as file:
            zip_as_bytes = BytesIO(self._in_memory_zip_file)
            file.write(zip_as_bytes.read())
        self._in_memory_zip_file = None
        self._status = 'completed'

    @staticmethod
    def _get_url_file_name(url):
        """
        Get file name from url
        :param url: url of file
        :return: string with file name
        """

        url_head = requests.head(url)
        url_header_dict = url_head.headers  # dict with http headers
        if 'Location' in url_header_dict.keys():
            url = url_header_dict['Location']
        file_name = url.split('/')[-1]
        return file_name

    @staticmethod
    def _get_url_as_bytes(url):
        """
        Get file from url as bytes object
        :param url: file url
        :return: file as bytes
        """

        file = requests.get(url, allow_redirects=True)
        file_as_binary_stream = BytesIO(file.content)
        file_as_bytes = file_as_binary_stream.read()
        return file_as_bytes

    @staticmethod
    def generate_zip_id(length):
        """
        Generate random alphanumeric string
        :param length: integer variable with string length
        :return: alphanumeric string which will be used as archive id
        """

        chars = string.ascii_lowercase + string.digits + '-'
        zip_id = ''.join(random.choice(chars) for i in range(length))
        return zip_id
