HEADER_DEFAULT = """
<div>
    <div style="width: 100%; text-align: center">
    <div class="div-header tr-table-bottom">
        <img src={img_url} alt="Avatar" class="avatar">
        <div>
            <h4 style="{domain_name_style}">{nome_empresa}</h4>
            <h4 style="{domain_info_style}">{info_empresa}</h4>
            <span style="{title_style}">{titulo}</span>
        </div>
        <span class="text-lighter fs-small">{data_emissao}</span>
    </div>
    <div class="margin-between-horizontal">
        {filtros}
    </div>
    </div>
</div>
"""  # noqa 501

FILTRO_ROW_TEMPLATE = "<b>{descricao}:</b> {valor} | "


TEMPLATE_DEFAULT = """
{style}
<div class="main-style">
    {header}
    {body}
    {footer}
</div>
"""  # noqa 501
