# estilo mais enxuto sem tracejado entre as linhas da tabela
# (usado no relatório de entrada e saída)
STYLE = """
<style type="text/css">
    .div-table {
        display: flex;
        flex-direction: column;
    }
    .table {
        width: 100%;
        height: auto;
        margin-top: 1px;
        border-collapse: collapse;
        text-align: center;
    }
    .tr-table-top {
        border-bottom: 0.5px solid gray;
        border-top: 0.5px solid gray;
    }
    .tr-table-center {
        border-top: 0px solid gray;
        border-bottom: 0.5px solid gray;
    }
    .tr-table-bottom {
        border-bottom: 0px solid gray;
    }
    .tr-table-right {
        border-right: 0.5px solid gray;
    }
    .tr-table-left {
        border-left: 0.5px solid gray;
    }
    .tr-table-color{
        background-color: #deebf7;
    }
    .td1-table {
        text-align: left;
        font-size: 9px;
        padding-left: 30px;
        padding-right: 0px !important;
    }
    .td2-table {
        text-align: right;
        font-size: 9px;
        padding-top: 1px;
        padding-bottom: 1px;
    }
    .td3-table {
        text-align: center;
        font-size: 9px;
        padding-top: 1px;
        padding-bottom: 1px;
    }
</style>
""" # noqa