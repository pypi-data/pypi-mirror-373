import logging

from zyjj_client_sdk.base.tool import data_convert

def test_type_convert():
    logging.info("{}".format(data_convert(1)))
    logging.info("{}".format(data_convert('2')))
    logging.info("{}".format(data_convert(bool)))
    logging.info("{}".format(data_convert(None)))
    logging.info("{}".format(data_convert(b'123')))
    logging.info("{}".format(data_convert(Exception('123'))))
    logging.info("{}".format(data_convert([1, b'123', {'1': 2}])))
    logging.info("{}".format(data_convert({1: {2: b'3'}})))
