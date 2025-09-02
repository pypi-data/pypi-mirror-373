

import flask

from viggocore.common import exception, utils


def export_capabilities_and_policies_sql(self, id):
    if flask.request.is_json:
        data = flask.request.get_json()
    else:
        data = {}

    try:
        download_folder, file_name = (
            self.manager.export_capabilities_and_policies_sql(id=id, **data))
    except exception.ViggoCoreException as exc:
        return flask.Response(response=exc.message,
                              status=exc.status)

    response = flask.send_from_directory(download_folder, file_name)
    utils.remove_file(f'{download_folder}/{file_name}')
    return response
