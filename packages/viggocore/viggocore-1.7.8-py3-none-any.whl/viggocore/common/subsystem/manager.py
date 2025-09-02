import os
from viggocore.common.subsystem.driver import Driver
from viggocore.common.subsystem import operation
from viggocore.common import exception
from viggocore.common.subsystem.manager_functions import (
    export_pdf, make_exportar_xlsx)


DATA_DOWNLOAD_FOLDER = 'data/<id>/download'


class ExportXlsx(operation.List):
    def pre(self, **kwargs):
        self.title = kwargs.get('title', 'Exportação em XLSX')
        self.file_title = kwargs.get('file_title', 'exportacao_xlsx')
        return True

    def do(self, session, **kwargs):
        filters = kwargs.get('filters', {})
        columns = kwargs.get('columns', [])

        entities = self.manager.list(session=session, **filters)
        if type(entities) is tuple:
            entities = entities[0]

        if len(entities) > 0:
            download_folder, file_name = \
                self.manager.make_export_xlsx(
                    entities=entities,
                    columns=columns,
                    title=self.title,
                    file_title=self.file_title
                )
        else:
            raise exception.BadRequest(
                'Não existe nada para essa filtragem.')

        return download_folder, file_name


class Manager(object):

    def __init__(self, driver: Driver, gerar_log=None) -> None:
        self.driver = driver
        # flag usada para saber se gera log
        self.gerar_log = gerar_log

        self.create = operation.Create(self)
        self.get = operation.Get(self)
        self.list = operation.List(self)
        self.update = operation.Update(self)
        self.delete = operation.Delete(self)
        # NOTE(samueldmq): what do we use this for ?
        self.count = operation.Count(self)
        self.list_multiple_selection = operation.ListMultipleSelection(self)
        self.activate_or_deactivate_multiple_entities = operation.\
            ActivateOrDeactivateMultipleEntities(self)
        self.export_xlsx = ExportXlsx(self)
        self.make_export_xlsx = make_exportar_xlsx.MakeExportarXsls(self)
        self.export_pdf = export_pdf.ExportPdf(self)

    def init_query(self, session, order_by, resource):
        raise exception.BadRequest(
            f'Method _init_query() not implemented for {resource.__name__}.')

    def valid_dinamic_order_by(self, order_by):
        result = False
        count_points = order_by.count('.')
        if ('.' in order_by and count_points == 1) or count_points == 0:
            result = True
        elif count_points > 1:
            raise exception.BadRequest(
                'order_by item cannot have more than one point.')
        return result

    def get_multiple_selection_ids(self, entities):
        try:
            return [entity.id for entity in entities]
        except Exception:
            raise exception.BadRequest(
                'id is not an attribute of this entity')

    def aplicar_filtro_status_periodo_data(self, query, resource, **kwargs):
        return self.driver._aplicar_filtro_status_periodo_data(
            query, resource, **kwargs)

    @classmethod
    def _get_download_folder(cls, id):
        data_download_folder = DATA_DOWNLOAD_FOLDER.replace('<id>', id)
        data_download_folder = os.environ.get('VIGGOCORE_FILE_DIR',
                                              data_download_folder)
        if not os.path.isabs(data_download_folder):
            data_download_folder = os.path.join(os.getcwd(),
                                                data_download_folder)
        return data_download_folder

    @classmethod
    def get_download_folder(cls, id):
        download_folder = cls._get_download_folder(id)
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        return download_folder
