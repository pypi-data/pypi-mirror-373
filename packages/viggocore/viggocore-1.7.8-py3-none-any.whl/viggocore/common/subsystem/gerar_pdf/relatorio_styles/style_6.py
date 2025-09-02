STYLE = """
<style type="text/css">
    .div-table {
        display: flex;
        flex-direction: column;
    }
    .separated-column {
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
        border-bottom: 0.5px solid gray;
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
    .td-table {
        text-align: center;
        padding-top: 1px;
        padding-bottom: 1px;
        border: 0.5px solid gray;
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
    .div-header{
        display: flex; 
        flex-direction: row; 
        justify-content: space-between; 
        align-items: center;
    }
    .sub-header-info{
        display: flex; 
        flex-direction: row; 
        justify-content: space-between;
        width: 100%;
    }
    .sub-header-text{
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
    }
    .sub-header-info-label{
        width: 10%; 
        text-align: center;
    }
</style>
"""  # noqa