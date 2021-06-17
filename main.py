from URL_downloader import app
from URL_downloader import zip_archive
from URL_downloader import zip_downloader
from flask import request, jsonify, abort
import requests

zip_collection_dict = {}    # dictionary which contain all archive objects, its ids and current status
# to powyzej mozna by zastapic BD


@app.route('/api/archive/create', methods=['POST'])
def create_zip_from_urls():
    """
    Function which create archive file from provided URLs
    in separate thread and return it's
    :return: zip file id
    """

    received_urls = request.form.getlist('urls')
    broken_urls = check_urls(received_urls)
    if broken_urls:
        response = jsonify(broken_urls)
        response.status_code = 400
        return response
    storage_on_disk = request.form.get('storage_on_disk')
    if not storage_on_disk:
        storage_on_disk = False
    elif storage_on_disk.lower() == 'false':
        storage_on_disk = False
    else:
        storage_on_disk = True
    zip_object = zip_archive.ZippedUrls(received_urls, storage_on_disk)
    zip_collection_dict[zip_object.id] = zip_object
    zip_object.create_zip()
    return jsonify({'archive_hash': zip_object.id})


@app.route('/api/archive/get/<redirected_address>.zip', methods=['GET'])
def download_zip_file(redirected_address):
    zip_id = redirected_address
    zip_archive_object = zip_collection_dict.get(zip_id)
    if not zip_archive_object:
        abort(404, description="Resource doesn't exist, or wrong id provided")
    if request.range:
        bytes_range = request.range
        downloader = zip_downloader.Downloader(zip_archive_object, bytes_range)
    else:
        downloader = zip_downloader.Downloader(zip_archive_object)
    return downloader.download()


@app.route('/api/archive/status/<redirected_address>')
def check_status(redirected_address):
    """
    Get archive status by its id
    :param redirected_address: represent archive id
    :return: archive status
    """

    zip_id = redirected_address
    print(zip_collection_dict)
    zip_archive_object = zip_collection_dict.get(zip_id)
    print(zip_id)
    print(zip_archive_object)
    if not zip_archive_object:
        abort(404, description="Resource doesn't exist, or wrong id provided")
    status = zip_archive_object.status
    status_response = {'status': status}
    if status is 'completed':
        is_stored_on_disk = zip_archive_object.is_stored_on_disk
        on_completed_response = {
                'url': 'http://localhost:5000/api/archive/get/%s.zip' % zip_id,
                'is_stored_on_disk': is_stored_on_disk
            }
        status_response.update(on_completed_response)
    return status_response


def check_urls(urls):
    broken_urls = {}
    for url in urls:
        url_header = requests.head(url)
        status_code = int(url_header.status_code)
        print(status_code)
        if status_code > 299:
            broken_urls[url] = status_code
    return broken_urls


#zipy beda zapisywane na dysku w razie czego beda rowniez w pamieci generalnie lista bedzie puki co jako lokalna zmienna