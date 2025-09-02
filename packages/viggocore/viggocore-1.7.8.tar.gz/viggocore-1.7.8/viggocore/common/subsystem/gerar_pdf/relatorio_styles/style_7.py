# estilo mais padrão com tracejado entre as linhas da tabela sendo
# pontilhados (usado nos relatórios de estoque de matéria prima e de
# produto por exemplo)
STYLE = """
<style type="text/css">
    .title-table-category  {
        font-size: 10px;
        font-weight: bold;
    }

    .title-table-resume {
        font-size: 10px;
        font-weight: bold;
        text-align: center;
    }

    .div-table {
        display: flex;
        flex-direction: column;
    }

    .table {
        width: 100%;
        height: 100%;
        border-collapse: collapse;
        text-align: center;
    }

    .tr-table-top {
        border-bottom: 0.5px solid gray;
        border-top: 0.5px solid gray;
    }

    .tr-table-center {
        border-top: 0.0px solid gray;
        border-bottom: 0.0px solid gray;
    }

    .tr-table-bottom {
        border-top: 0px solid gray;
    }

    .td1-table {
        text-align: left;
        font-size: 10px;
        padding-left: 5px;
        padding-right: 5px !important;
    }

    .td2-table {
        text-align: right;
        font-size: 10px;
        padding-top: 1px;
        padding-bottom: 1px;
        padding-left: 5px !important;
        padding-right: 5px;
    }

    .tr-table-border {
        border-left: 1px solid gray;
        border-right: 1px solid gray;
        border-top: 1px solid gray;
        border-bottom: 1px solid gray;
    }
</style>"""  # noqa
