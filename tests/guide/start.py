import logging

from GuideMain import GuideMain
import Helper

if __name__ == '__main__':
    Helper.init_logging()
    logging.info('***** Main start *****')

    a = GuideMain()
    a.start()
