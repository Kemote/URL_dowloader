from URL_downloader import app

@app.errorhandler(404)
def not_found(error):
    return 'Strona not found %s' % error