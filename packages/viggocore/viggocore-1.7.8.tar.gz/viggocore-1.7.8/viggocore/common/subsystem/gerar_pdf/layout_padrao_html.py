TD_LEFT = """
<td style="width:{width};" class="td1-table tr-table-border quebra-texto">
    {value}
</td>
"""

TD_RIGHT = """
<td style="width:{width};" class="td2-table tr-table-border quebra-texto">
    {value}
</td>
"""


TD_BOLD = """
<td style="width:{width};" class="td1-table tr-table-border quebra-texto">
    <b>{value}</b>
</td>
"""


TR = """
<tr class="tr-table-center tr-table-border quebra-texto">
    {tds}
</tr>
"""

TR_FOOTER = """
<tr class="tr-table-center tr-table-border">
    <td style="width:0%;" class="td1-table tr-table-border quebra-texto">
        </br>
        <b>{count}</b>
    </td>
</tr>
"""

BODY = """
<div class="div-table">
    <table class="table">
        {tr_title}
        {trs}
    </table>
</div>
"""
