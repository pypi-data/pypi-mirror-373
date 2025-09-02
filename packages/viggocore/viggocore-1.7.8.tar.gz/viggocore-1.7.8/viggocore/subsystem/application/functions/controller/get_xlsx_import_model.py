

import flask

from viggocore.common import exception, utils


def get_xlsx_import_model(self):
    try:
        download_folder, file_name = self.manager.get_xlsx_import_model()
    except exception.ViggoCoreException as exc:
        return flask.Response(response=exc.message,
                              status=exc.status)

    response = flask.send_from_directory(download_folder, file_name)
    utils.remove_file(f'{download_folder}/{file_name}')
    return response
