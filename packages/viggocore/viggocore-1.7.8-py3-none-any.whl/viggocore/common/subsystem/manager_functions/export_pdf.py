from enum import Enum
from datetime import datetime
from viggocore.common.subsystem import operation
from viggocore.common import exception, utils as core_utils
from viggocore.common.subsystem.gerar_pdf import (
    relatorio_utils as ru,
    layout_padrao_html as layout)


class ExportPdf(operation.Operation):

    def _treat_data_type(self, data, col):
        data_type = col.get('type', 'STRING')
        result = ''

        if data_type == 'STRING':
            result = data if data is not None else '-'
            if data is not None:
                result = data.name if isinstance(data, Enum) else data
        elif data_type == 'BOOLEAN':
            result = 'Sim' if data is True else 'Não'
        elif data_type == 'DATE':
            result = datetime.strftime(data, '%d/%m/%Y') \
                if data is not None \
                else '-'
        elif data_type == 'DATETIME':
            result = datetime.strftime(data, '%d/%m/%Y %H:%M') \
                if data is not None \
                else '-'
        elif data_type == 'CURRENCY' or data_type == 'FLOAT':
            decimals = col.get('decimals', None)
            if decimals is not None:
                result = core_utils.to_decimal_n(data, decimals) \
                    if data is not None \
                    else core_utils.to_decimal_n('0', decimals)
            else:
                result = core_utils.to_decimal(data) \
                    if data is not None \
                    else core_utils.to_decimal('0')
        elif data_type == 'INT':
            result = int(data) if data is not None else 0

        return result

    def _montar_tr(self, columns, entity):
        tr_html = ''
        td_html = ''
        for col in columns:
            value = ''
            fields = col.get('field', None)
            if fields is not None:
                fields = fields.split('.')
                if len(fields) > 1:
                    value = None if entity is None else entity
                    if entity is not None:
                        for field in fields:
                            if value is not None:
                                value = value.__getattribute__(field)
                else:
                    value = entity.__getattribute__(fields[0])

                value = self._treat_data_type(value, col)

            if col.get('type', None) in ['INT', 'CURRENCY', 'FLOAT']:
                td_html += layout.TD_RIGHT.format(
                    width=col.get('width', '1%'),
                    value=value)
            else:
                td_html += layout.TD_LEFT.format(
                    width=col.get('width', '1%'),
                    value=value)

        if len(td_html) > 0:
            tr_html = layout.TR.format(tds=td_html)

        return tr_html

    def _montar_tr_title(self, columns):
        td_html = ''
        for col in columns:
            td_html += layout.TD_BOLD.format(
                width=col.get('width', '1%'),
                value=col.get('header_name', ''))
        return layout.TR.format(tds=td_html)

    # TODO(JorgeSilva): verificar a necessidade de mapear os filtros aplicados
    def _get_filtros(self, **kwargs):
        return ''

    def _get_domain_display_name(self, entities):
        domain_display_name = ''
        info_empresa = ''
        try:
            domain = entities[0].domain
        except Exception:
            domain = self.manager.api.domains().get(id=entities[0].domain_id)

        # verifica se o display_name do domínio não está vazio
        if not core_utils.is_empty_or_blank(domain.display_name):
            domain_display_name = domain.display_name

        if self.com_endereco:
            address = ''
            address2 = ''
            if len(domain.addresses) > 0:
                addr = domain.addresses[0]
                address = (
                    f'{addr.logradouro}, {addr.numero}, {addr.bairro}, ' +
                    f'{addr.municipio.nome}/{addr.municipio.sigla_uf}')
                address2 = f'CEP. {ru.formatar_cep(addr.cep)}'
                if domain.doc is not None:
                    address2 = f'{address2} - CNPJ: ' \
                        if len(domain.doc) > 11 \
                        else f'{address2} - CPF: '
                    address2 = address2 + \
                        ru.apply_mask_cpf_cnpj(domain.doc)

            if address != '':
                info_empresa = "<br>".join([
                    address, address2, ''])

        return (domain_display_name, info_empresa)

    def _gerar_html(self, entities, columns):
        if not hasattr(self, 'filtros'):
            self.filtros = ''

        body = layout.BODY
        data_solicitacao = self.data_solicitacao.strftime('%d/%m/%Y, %H:%M')
        domain_display_name, info_empresa = self._get_domain_display_name(
            entities)

        # montar o html do título de cada coluna da tabela
        tr_title = self._montar_tr_title(columns)

        # montar o html das linhas da tabela
        trs = ''
        for entity in entities:
            trs += self._montar_tr(columns, entity)

        # montar o footer do html
        footer = layout.TR_FOOTER \
            .format(count=f'Total de linhas: {len(entities)}')

        img_url = ru.get_logo_path(self.manager, self.domain_id)

        # monta o header
        header = ru.montar_header(
            img_url=img_url,
            nome_empresa=domain_display_name,
            info_empresa=info_empresa,
            titulo=self.title,
            data_emissao=data_solicitacao,
            filtros=self.filtros,
            domain_name_style=self.domain_name_style,
            domain_info_style=self.domain_info_style,
            title_style=self.title_style)

        # monta o body (este é específico para cada relatório)
        body = body.format(tr_title=tr_title, trs=trs)

        # joga o header e o body formatados dentro do template
        template = ru.montar_template(
            header=header, body=body, op_style=7, footer=footer,
            style_pagination=self.style_pagination)

        return template

    def pre(self, **kwargs):
        # pega a flag com_endereco responsável por contatenar o nome
        # do domínio com o seu endereço caso a flag seja passada
        self.com_endereco = kwargs.pop('com_endereco', False)
        # pega a data de solicitação de relatório para colocar no pdf
        self.data_solicitacao = ru.get_data_solicitacao_dt(**kwargs)
        # pega o título que deseja que apareça no relatório
        self.title = kwargs.get('title', 'Exportação em PDF')
        # pega o domain_id para ter as informações do domínio e conseguir
        # puxar a logo para montar o cabeçalho do PDF
        self.domain_id = kwargs.get('domain_id', None)
        # verifica se o domain_id foi passado na requisição ou não
        if self.domain_id is None:
            raise exception.BadRequest('É obrigatório passar o domain_id.')

        # caso seja passado um style_pagination então o backend irá
        # aplicar ele, caso não seja passado então será aplicado o
        # RETRATO como padrão
        style_pagination = kwargs.get('style_pagination', None)
        if style_pagination is None:
            self.style_pagination = ru.STYLE_PAGINATION_TYPE.RETRATO
        else:
            self.style_pagination = ru.STYLE_PAGINATION_TYPE[style_pagination]

        # pega as variáveis do style de cada parte do meio do header.
        # Se não for passado vai manter o padrão
        self.domain_name_style = kwargs.get('domain_name_style', None)
        self.domain_info_style = kwargs.get('domain_info_style', None)
        self.title_style = kwargs.get('title_style', None)

        return True

    def do(self, session, **kwargs):
        filters = kwargs.get('filters', {})
        columns = kwargs.get('columns', [])

        self.filtros = self._get_filtros(**filters)

        entities = self.manager.list(session=session, **filters)
        if type(entities) is tuple:
            entities = entities[0]

        if len(entities) > 0:
            html = self._gerar_html(entities, columns).replace('\n', '')
        else:
            raise exception.BadRequest(
                'Não existe nada para essa filtragem.')

        # chama a função que gera o pdf e trata a resposta
        response = ru.gerar_pdf(html)
        return response
