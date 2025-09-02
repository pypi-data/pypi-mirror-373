# estilo mais padrão com tracejado entre as linhas da tabela sendo
# pontilhados (usado nos relatórios de estoque de matéria prima e de
# produto por exemplo)
STYLE = """
<style>
    body {
        font-family: Georgia, 'Times New Roman', Times, serif, sans-serif;
        margin: 15px;
        font-size: 10px;
    }

    .cabecalho {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding-bottom: 5px;
        margin-bottom: 15px;
    }

    .logo img {
        width: 70px;
        height: auto;
    }

    .centro {
        text-align: center;
        flex-grow: 1;
    }

    .centro h2 {
        margin: 0;
        font-size: 13px;
    }

    .centro p {
        margin: 1px 0;
        font-size: 9px;
    }

    .centro .titulo-relatorio {
        margin-top: 12px;
        font-size: 13px;
        font-weight: bold;
        text-transform: uppercase;
    }

    .emissao {
        font-size: 9px;
        text-align: right;
    }

    table {
        width: 100%;
        border-collapse: collapse;
    }

    th,
    td {
        border: 1px solid #ccc;
        padding: 4px;
        vertical-align: top;
        font-size: 9px;
    }

    th {
        background-color: #f9f9f9;
        color: #000000;
        /* ← Cor preta aplicada aqui */
        text-align: left;
    }

    td.foto {
        text-align: center;
    }

    td.foto img {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        object-fit: cover;
    }

    .motivo {
        white-space: pre-wrap;
        padding-top: 2px;
        font-style: italic;
    }

    .linha-motivo td {
        border-top: none;
        background-color: #f9f9f9;
        font-size: 9px;
        table-layout: fixed;
    }
</style>"""  # noqa
