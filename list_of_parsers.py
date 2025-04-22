from parser_yandex import start_parser_yandex
from parser_wb import start_parser_wb
from parser_ozon import start_parser_ozon

PARSERS = {
    'яндекс.маркет': start_parser_yandex,
    'яндекс': start_parser_yandex,
    'ozon': start_parser_ozon,
    'озон': start_parser_ozon,
    'wildberries': start_parser_wb,
    'wb': start_parser_wb,
}