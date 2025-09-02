# imports
import os
import requests
from datetime import datetime

from viggocore.common.subsystem.gerar_pdf.relatorio_html import (
    FILTRO_ROW_TEMPLATE, HEADER_DEFAULT, TEMPLATE_DEFAULT)
from viggocore.common import exception
from viggocore.common.subsystem.entity import DATE_FMT, DATETIME_FMT

from viggocore.common.subsystem.gerar_pdf.relatorio_styles import (
    style_1, style_2, style_3, style_4, style_5, style_6, style_7,
    style_8, style_default)
from viggocore.common.subsystem.gerar_pdf.relatorio_styles.style_paginacao \
    import STYLE_PAGINATION_TYPE
from typing import List, Dict


# constantes
HTML2PDF_URL = os.getenv('HTML2PDF_URL', 'http://172.17.0.1:1234/html2pdf')
DOMAIN_NAME_STYLE = (
    'font-weight: lighter; margin-top: 0px; margin-bottom: 0px; ' +
    'padding-top: 0px; padding-bottom: 0px; font-weight: bold; ' +
    'font-size: 1.058rem;')
DOMAIN_INFO_STYLE = (
    'font-weight: lighter; margin-top: 0px; margin-bottom: 0px; ' +
    'padding-top: 0px; padding-bottom: 0px;')
TITLE_STYLE = 'font-weight: bold; font-size: 1.058rem;'


# funções
def gerar_pdf(html, parametros=None, url=HTML2PDF_URL):
    data = {
        'html': html,
        'parametros': (
            parametros if parametros is not None else get_parametros())
    }
    r = requests.post(url, json=data)
    if r.status_code != 200:
        raise exception.ViggoCoreException(r.text)
    else:
        return r.content


def format_qtd(qtd, precisao=2):
    mascara = '{:_.' + str(precisao) + 'f}'
    return mascara.format(float(qtd)).replace('_', ' ')


def format_dinheiro(valor, precisao=2, moeda=''):
    mascara = '{:_.' + str(precisao) + 'f}'
    return moeda + mascara.format(float(valor))\
        .replace('.', ',').replace('_', '.')


def get_dia_da_semana(data_hora):
    dia = data_hora.weekday()
    dia_nomes = (
        "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
        "Sexta-feira", "Sábado", "Domingo")
    dia_nome = dia_nomes[dia]
    return dia_nome


def get_mes_por_extenso(data_hora):
    mes = data_hora.month
    mes_nomes = (
        "UNKNOWN", "Janeiro", "Fevereiro", "Março", "Abril",
        "Maio", "Junho", "Julho",
        "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro")
    mes_nome = mes_nomes[mes]
    return mes_nome


def normaliza_dia_ou_mes(dia_ou_mes):
    response = str(dia_ou_mes)
    if dia_ou_mes < 10:
        response = f'0{dia_ou_mes}'
    return response


def get_data_formatada(data_hora):
    return data_hora.strftime('%d/%m/%Y')


def formatar_cep(cep):
    return f'{cep[:5]}-{cep[5:]}'


def apply_mask_cpf_cnpj(cpf_cnpj):
    cpf_cnpj_with_mask = '-'
    if cpf_cnpj is None:
        return '-'
    cpf_cnpj = cpf_cnpj.strip()
    if len(cpf_cnpj) == 11:
        cpf_cnpj_with_mask = '{}.{}.{}-{}'.\
            format(cpf_cnpj[:3], cpf_cnpj[3:6], cpf_cnpj[6:9], cpf_cnpj[9:])
    elif len(cpf_cnpj) == 14:
        cpf_cnpj_with_mask = '{}.{}.{}/{}-{}'.\
            format(cpf_cnpj[:2], cpf_cnpj[2:5], cpf_cnpj[5:8],
                   cpf_cnpj[8:12], cpf_cnpj[12:])
    return cpf_cnpj_with_mask


def get_data_solicitacao(**kwargs):
    data_solicitacao = kwargs.pop('data_solicitacao', None)
    if data_solicitacao is None:
        raise exception.BadRequest('É orbrigatório passar a data_solicitação.')
    try:
        if 'T' in data_solicitacao:
            data_solicitacao = datetime.strptime(
                data_solicitacao, DATETIME_FMT)
            data_solicitacao = data_solicitacao.strftime('%d/%m/%Y, %H:%M')
        else:
            data_solicitacao = datetime.strptime(data_solicitacao, DATE_FMT)
            data_solicitacao = data_solicitacao.strftime('%d/%m/%Y')
    except Exception:
        raise exception.BadRequest(
            'Não foi possível converter a data_solicitacao.')
    return data_solicitacao


def get_data_solicitacao_dt(**kwargs):
    data_solicitacao = kwargs.pop('data_solicitacao', None)
    if data_solicitacao is None:
        raise exception.BadRequest('É obrigatório passar a data_solicitação.')
    try:
        if 'T' in data_solicitacao:
            data_solicitacao = datetime.strptime(
                data_solicitacao, DATETIME_FMT)
        else:
            data_solicitacao = datetime.strptime(data_solicitacao, DATE_FMT)
    except Exception:
        raise exception.BadRequest(
            'Não foi possível converter a data_solicitacao.')
    return data_solicitacao


# parametros padrões para passar para o componente html2pdf
def get_parametros(margin_left=0.1, margin_right=0.1,
                   margin_top=0.1, landscape=False,
                   display_header_footer=False,
                   header_template='',
                   footer_template=''):
    '''
    link dos possíveis parametros: https://chromedevtools.github.io/devtools-protocol/tot/Page/#method-printToPDF
    '''  # noqa
    FOOTER_DEFAULT = 'o FOOTER_DEFAULT não foi implementado'
    if len(footer_template) == 0:
        footer_template = FOOTER_DEFAULT

    parametros = {
        'marginLeft': margin_left,
        'marginRight': margin_right,
        'marginTop': margin_top,
        'landscape': landscape,
        'displayHeaderFooter': display_header_footer,
        'headerTemplate': header_template,
        'footerTemplate': footer_template,
    }
    return parametros


# funcao de formatar datas que será usada nas duas próximas funções
def _format_data(data):
    data_splited = data.split('-')
    dia = data_splited[2]
    mes = data_splited[1]
    if len(dia) == 1:
        dia = '0' + dia
    if len(mes) == 1:
        mes = '0' + mes
    ano = data_splited[0]
    return f'{dia}/{mes}/{ano}'


# tratar filtros 'de' e 'ate'
def tratar_filtros_de_ate(filtros, filtros_dict, filtro_mapper_dict={}):
    has_de = 'de' in filtros.keys()
    has_ate = 'ate' in filtros.keys()
    has_attribute = 'attribute' in filtros.keys()
    if has_de and has_ate and has_attribute:
        de = filtros.get('de', '')
        ate = filtros.get('ate', '')
        attribute = filtros.get('attribute', '')

        chave = filtro_mapper_dict.get(attribute, 'NÃO MAPEADO')
        de = _format_data(de)
        ate = _format_data(ate)
        filtros_dict.append(montar_filtro_dict(
            descricao=chave,
            valor=f'entre {de} e {ate}'
        ))
    return filtros_dict


# tratar filtros de multiplas datas
def tratar_filtros_multiplas_datas(filtros, filtros_dict,
                                   filtro_mapper_dict={}):
    has_de_filter = 'de_filter' in filtros.keys()
    has_ate_filter = 'ate_filter' in filtros.keys()
    has_attributes_filter = 'attributes_filter' in filtros.keys()
    if has_de_filter and has_ate_filter and has_attributes_filter:
        de_filter = filtros.get('de_filter', '').split(',')
        ate_filter = filtros.get('ate_filter', '').split(',')
        attributes_filter = filtros.get('attributes_filter', '').split(',')
        for i in range(len(attributes_filter)):
            chave = filtro_mapper_dict.get(attributes_filter[i], 'NÃO MAPEADO')
            de = _format_data(de_filter[i])
            ate = _format_data(ate_filter[i])
            filtros_dict.append(montar_filtro_dict(
                descricao=chave,
                valor=f'entre {de} e {ate}'
            ))
    return filtros_dict


# funções usadas para preencher o html do relatório
def get_domain_name(domain):
    if domain.display_name is not None:
        return domain.display_name
    else:
        return domain.name


def get_logo_path(manager, domain_id):
    try:
        HTML2PDF_FILE_DIR = os.environ.get('HTML2PDF_FILE_DIR', '')
        IMAGEM_DEFAULT = (
            HTML2PDF_FILE_DIR + '/default/default-domain-image.png')

        # exemplo de PATH_BASE_IMAGES = '/all_files/project_name'
        PATH_BASE = os.environ.get('PATH_BASE_IMAGES', None)
        if PATH_BASE is None:
            raise exception.BadRequest(
                'É obrigatório preencher a variável PATH_BASE_IMAGES no env.')

        imagem_path = IMAGEM_DEFAULT
        domains = manager.api.domains().list(id=domain_id)

        if len(domains) > 0 and domains[0].logo_id is not None:
            path, filename = manager.api.images().get(
                id=domains[0].logo_id,
                quality='max')
            imagem_path = f'{PATH_BASE}{path}/{filename}'
        return imagem_path
    except Exception:
        return ''


def montar_filtro_dict(descricao, valor) -> Dict[str, str]:
    return {
        'descricao': str(descricao),
        'valor': str(valor)
    }


def montar_filtros(filtros: List[Dict[str, str]]) -> str:
    filtros_html = ''
    if len(filtros) > 0:
        for filtro in filtros:
            filtro_html = FILTRO_ROW_TEMPLATE.format(
                descricao=filtro.get('descricao', ''),
                valor=filtro.get('valor', '')
            )
            filtros_html += filtro_html
        filtros_html = filtros_html[:-3]
    if len(filtros_html) > 0:
        filtros_html = 'Filtros: ' + filtros_html
    return filtros_html


def montar_header(img_url, nome_empresa, titulo, data_emissao, filtros,
                  info_empresa='', domain_name_style=None,
                  domain_info_style=None, title_style=None):
    # se os styles customizados não forem passados então o backend
    # vai usar os padrões
    if domain_name_style is None:
        domain_name_style = DOMAIN_NAME_STYLE
    if domain_info_style is None:
        domain_info_style = DOMAIN_INFO_STYLE
    if title_style is None:
        title_style = TITLE_STYLE

    # info_empresa = são informações como o endereço e o doc do domain
    return HEADER_DEFAULT.format(
        img_url=img_url,
        nome_empresa=nome_empresa,
        info_empresa=info_empresa,
        titulo=titulo,
        data_emissao=data_emissao,
        filtros=filtros,
        domain_name_style=domain_name_style,
        domain_info_style=domain_info_style,
        title_style=title_style
    )


def get_style(op_style: int):
    opcoes = {
        1: style_1.STYLE,
        2: style_2.STYLE,
        3: style_3.STYLE,
        4: style_4.STYLE,
        5: style_5.STYLE,
        6: style_6.STYLE,
        7: style_7.STYLE,
        8: style_8.STYLE,
    }
    style_escolhido = opcoes.get(op_style, style_1.STYLE)
    return (style_default.STYLE + style_escolhido)


# todas as variáveis devem ser html em string
def montar_template(header: str, body: str, footer: str = '',
                    style: str = '', op_style: int = 7,
                    style_pagination: STYLE_PAGINATION_TYPE =
                    STYLE_PAGINATION_TYPE.RETRATO):
    style_final = get_style(op_style) + style
    # se quiser gerar o relatório com paginação então aplica o style da
    # paginação específico. O style definirá a direção da folha se será
    # RETRATO ou PAISAGEM
    if style_pagination is not None:
        style_final += style_pagination.value

    return TEMPLATE_DEFAULT.format(
        style=style_final,
        header=header,
        body=body,
        footer=footer
    ).replace('\n', '')
