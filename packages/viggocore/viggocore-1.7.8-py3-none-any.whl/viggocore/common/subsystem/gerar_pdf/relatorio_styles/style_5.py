# style usado na ficha técnica do pedido
STYLE = """
<style type="text/css">
    .w-100 {
        width: 100%;
    }

    .w-50 {
        width: 50%;
    }

    .w-auto {
        width: auto;
    }

    .w-20 {
        width: 20%;
    }

    .flex {
        display: flex;
    }

    .flex-column {
        display: flex;
        flex-direction: column;
    }

    .justify-content-between {
        justify-content: space-between;
    }

    .justify-content-around {
        justify-content: space-around;
    }

    .align-items-center {
        align-items: center;
    }

    .main-style {
        font-size: 12px;
        height: 100%;
        font-family: \'Lucida Sans\', \'Lucida Sans Regular\', \'Lucida Grande\', \'Lucida Sans Unicode\', Geneva, Verdana, sans-serif;
    }

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
        border-bottom: 0px solid gray;
    }

    .tr-table-bottom {
        border-bottom: 0.5px solid black;
    }

    .td-table {
        text-align: center;
        font-size: 10px;
        padding-top: 1px;
        padding-bottom: 1px;
    }

    .sub-header-info-label {
        width: auto;
        text-align: start;
    }

    .margin-between-horizontal {
        margin: 1px 0px 1px 0px;
    }

    .text-underline {
        text-decoration: underline;
    }

    .text-start {
        text-align: start;
    }

    .img-container {
        text-align: center !important;
    }

    .img-card {
        width: 100%;
        height: 100%;
        max-width: 200px;
        max-height: 200px;
        object-fit: contain;
        background-color: #fff;
        border: 2px solid black;
        border-radius: 10%;
        -moz-border-radius: 10%;
        -webkit-border-radius: 10%;
        clip-path: square();
    }

    .observacao-box {
        width: auto;
        height: auto;
        border: 1.5px solid black;
        padding: 1px;
    }

    .pl-10 {
        padding-left: 5px;
    }
</style>"""  # noqa