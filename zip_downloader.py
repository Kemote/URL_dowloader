from io import BytesIO
from flask import request, Response
from werkzeug.wsgi import FileWrapper


class Downloader:
    def __init__(self, zip_archive, byte_range=None):
        self.bytes_range = byte_range
        self.zip_archive = zip_archive

    def download(self):

        """
        Method which allow to download zip file by its id
        :return:
        """

        if self.zip_archive.is_stored_on_disk:
            with open('URL_downloader/stored_archives/%s.zip' % self.zip_archive.id, 'rb') as buffer:
                zip_io = BytesIO(buffer.read())
        else:
            zip_io = BytesIO(self.zip_archive.archive)
        file_wrapper = FileWrapper(zip_io)
        if self.bytes_range:
            response = self._continue_downloading(self.zip_archive.id, file_wrapper, self.bytes_range)
        else:
            response = self._download_archive(file_wrapper)
        return response

    def _download_archive(self, file_wrapper):
        """
        Create response for downloading archive file
        :param file_wrapper: object with archive
        :return: download response
        """

        file_wrapper.seek(0)
        headers = {
            'Content-Disposition': 'attachment; filename=%s.zip' % self.zip_archive.id
        }
        response = Response(
            file_wrapper,
            mimetype='application/zip',
            direct_passthrough=True,
            headers=headers
        )
        return response

    def _continue_downloading(self, zip_name, file_wrapper, bytes_range):
        """
        Continue downloading if range header provided
        :param zip_name: archive name
        :param file_wrapper: object with archive
        :param bytes_range: byte from which script should continue downloading
        :return: download response
        """

        headers = {
            'Content-Disposition': 'attachment,'
            'filename=%s.zip' % zip_name,
            'Status': '206',
            'Accept-Ranges': 'bytes',
        }
        file_part = self._get_file_part(file_wrapper, bytes_range)
        response = Response(
            file_part,
            mimetype="application/zip",
            direct_passthrough=True,
            headers=headers
        )
        return response

    @staticmethod
    def _get_file_part(file_wrapper, bytes_range):
        """
        Get part of file started from provided byte
        :param file_wrapper: object with archive
        :param bytes_range: byte from which script should start
        :return: FileWrapper object with archive
        """
        start_byte = bytes_range.ranges[0][0]
        file_wrapper.seek(start_byte)
        return file_wrapper
