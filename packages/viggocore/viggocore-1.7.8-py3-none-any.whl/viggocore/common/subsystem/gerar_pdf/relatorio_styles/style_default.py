STYLE = """
<style type="text/css">
    .main-style {
        font-size: 12px;
        height: max-content;
        font-family: \'Lucida Sans\', \'Lucida Sans Regular\', \'Lucida Grande\', \'Lucida Sans Unicode\', Geneva, Verdana, sans-serif;
    }
    .text-primary {
        color: #324581;
        font-weight: bold;
    }
    .text-green {
        color: green;
        font-weight: bold;
    }
    .text-red {
        color: red;
        font-weight: bold;
    }
    .text-bolder{
        font-weight: bold;
    }
    .text-lighter{
        font-weight: lighter;
    }
    .fs-small {
        font-size: 0.758rem !important;
    }
    .fs-normal {
        font-size: 0.958rem !important;
    }
    .fs-large {
        font-size: 1.058rem !important;
    }
    .fs-xsmall {
        font-size: 0.558rem !important;
    }
    .avatar {
        vertical-align: middle;
        width: 50x;
        height: 50px;
        border-radius: 50%;
        margin: 2px 0px 2px 0px;
    }
    .div-header{
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        padding-top: 1px;
        padding-bottom: 1px;
    }
    .margin-between-horizontal{
        margin: 2px 0px 2px 0px;
    }
    .mt-1{
        margin-top: 1px;
    }
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

    .tr-table-border {
        border-top: 1px dotted gray;
        border-bottom: 1px dotted gray;
    }

    .sub-header-info {
        display: flex;
        flex-direction: column;
        justify-content: end;
        width: 100%;
    }

    .sub-header-info-label {
        width: 20%;
        text-align: start;
    }

    .div-sub-header {
        border-top: 2px solid gray;
    }

    .sub-header-text {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: start;
    }

    .text-center {
        text-align: center;
    }

    .text-left {
        text-align: left;
    }

    .text-right {
        text-align: right;
    }

    .footer-total {
        display: flex;
        justify-content: end;
        align-items: center;
        width: 100%;
        margin-top: 5px;
    }

    .ml-4 {
        margin-left: 2rem;
    }

    .flex-column {
        display: flex;
        flex-direction: column;
    }

    .flex {
        display: flex;
    }

    .td-table-left {
        text-align: left;
        font-size: 10px;
        padding-left: 10px;
        border: 0.5px solid gray;
    }

    .td-table-right {
        text-align: right;
        font-size: 10px;
        padding-right: 10px;
        border: 0.5px solid gray;
    }

    .quebra-texto {
        overflow-wrap: break-word;
        /* ← Permite que o navegador quebre longas palavras quando necessário para evitar overflow. */
        word-wrap: break-word;
        /* ← É um alias mais antigo para overflow-wrap e ajuda na compatibilidade com navegadores mais antigos. */
        word-break: break-word;
        /* ← Controla como as palavras devem ser quebradas quando o texto atinge o limite do container. Diferente de word-break: break-all, que pode quebrar no meio de qualquer caractere, o valor break-word tenta quebrar em pontos apropriados.*/
        hyphens: auto;
        /* ← Adiciona hifenização automática quando uma palavra é quebrada, melhorando a legibilidade (funciona em navegadores que suportam a propriedade). */
        max-width: 100%;
        /* ← Garante que o conteúdo não ultrapasse a largura da célula. */
        -webkit-hyphens: auto;
        -moz-hyphens: auto;
    }
</style>
"""  # noqa