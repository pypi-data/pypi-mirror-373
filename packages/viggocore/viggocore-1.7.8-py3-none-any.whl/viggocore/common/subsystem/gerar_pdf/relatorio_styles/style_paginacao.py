import enum


class STYLE_PAGINATION_TYPE(enum.Enum):
    RETRATO = """
    <style>
        @page {
            size: A4;
            margin: 10mm;
        }
        @page {
            @bottom-right {
                content: "Página " counter(page) " de " counter(pages);
                font-size: 12px;
            }
        }
    </style>"""  # noqa

    PAISAGEM = """
    <style>
        @page {
            size: A4 landscape;
            margin: 10mm;
        }
        @page {
            @bottom-right {
                content: "Página " counter(page) " de " counter(pages);
                font-size: 12px;
            }
        }
    </style>"""  # noqa